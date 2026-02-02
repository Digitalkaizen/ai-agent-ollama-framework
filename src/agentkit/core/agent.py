from __future__ import annotations

import json
import os
from typing import Any

from agentkit.core.llm import OpenAILLM
from agentkit.core.models import AgentInput, AgentOutput
from agentkit.core.tracing import Tracer
from agentkit.tools.registry import ToolRegistry, Tool
from agentkit.tools.time_tool import get_utc_time


DEFAULT_INSTRUCTIONS = """
You are a helpful AI agent running inside a developer starter kit.

Rules:
- Decide when to call tools. Use tools when they help produce a more accurate answer.
- If you call a tool, wait for its output, then answer the user.
- Be concise.
- Reply in the user's language when obvious.
"""


class Agent:
    """
    Agent with a real LLM-backed tool-calling loop.

    Flow (classic function calling):
    1) Send user message + available tools to the model.
    2) If model returns function_call -> execute locally.
    3) Send function_call_output back to the model.
    4) Repeat until model returns final text (or we hit a safety limit).
    """

    def __init__(
        self,
        tools: ToolRegistry | None = None,
        llm: OpenAILLM | None = None,
        instructions: str | None = None,
        max_tool_rounds: int = 5,
    ) -> None:
        self.tools = tools or ToolRegistry()
        self.max_tool_rounds = max_tool_rounds
        self.instructions = (instructions or DEFAULT_INSTRUCTIONS).strip()

        # Register built-in tools
        self.tools.register(
            Tool(
    name="time_now_utc",
    description="Get current UTC time as string.",
    fn=get_utc_time,
    parameters={"type": "object", "properties": {}, "required": []},
)
        )

        # If OPENAI_API_KEY is set, we can use the LLM.
        # Otherwise, we keep a graceful fallback (starter behavior).
        self.llm = llm
        if self.llm is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.llm = OpenAILLM(api_key=api_key)

    def run(self, inp: AgentInput) -> AgentOutput:
        tracer = Tracer()
        tracer.add("input.received", message=inp.message, session_id=inp.session_id)

        # Fallback if no LLM configured
        if self.llm is None:
            tracer.add("llm.disabled", reason="OPENAI_API_KEY not set")
            answer = "LLM is not configured (set OPENAI_API_KEY). Starter agent is running."
            tracer.add("output.ready", answer_preview=answer[:80])
            return AgentOutput(answer=answer, trace_id=tracer.trace_id, meta={"trace": tracer.to_dict()})

        tools_schema = self.tools.as_openai_tools()
        tracer.add("tools.available", count=len(tools_schema), tools=[t["name"] for t in tools_schema])

        # We build a running "input list" exactly like the reference loop:
        # Start with the user message. Then append model outputs (incl. function calls),
        # plus our function_call_output items. :contentReference[oaicite:4]{index=4} (conceptually)
        input_list: list[dict[str, Any]] = [
            {"role": "user", "content": inp.message},
        ]

        rounds = 0
        final_text: str | None = None

        while rounds <= self.max_tool_rounds:
            rounds += 1
            tracer.add("llm.request", round=rounds, input_len=len(input_list))

            response = self.llm.create_response(
                input_list=input_list,
                tools=tools_schema,
                instructions=self.instructions,
            )

            # Append model output items into the conversation state
            # The Responses API returns an "output" list with items (message/function_call/etc.). :contentReference[oaicite:5]{index=5}
            output_items = getattr(response, "output", None) or []
            input_list += output_items

            # If model already produced text, capture it
            output_text = getattr(response, "output_text", None)
            if isinstance(output_text, str) and output_text.strip():
                final_text = output_text.strip()

            tracer.add(
                "llm.response",
                round=rounds,
                output_items=len(output_items),
                has_text=bool(final_text),
            )

            # Look for function calls in this response
            function_calls = [it for it in output_items if getattr(it, "type", None) == "function_call"]

            if not function_calls:
                # No tool calls: we're done (final_text should exist; if not, give a fallback)
                if not final_text:
                    final_text = "I did not produce a text response. (No tool call either.)"
                break

            # Execute each function call (we allow multiple per round)
            for call in function_calls:
                tool_name = getattr(call, "name", None)
                call_id = getattr(call, "call_id", None)
                raw_args = getattr(call, "arguments", "{}")

                tracer.add("tool.call", tool=tool_name, call_id=call_id, arguments=raw_args)

                if not tool_name or not call_id:
                    tracer.add("tool.error", error="Malformed function_call item")
                    continue

                tool = self.tools.get(tool_name)

                # Parse arguments JSON (tool may have no args)
                try:
                    args_obj = json.loads(raw_args) if raw_args else {}
                except json.JSONDecodeError:
                    args_obj = {}

                # Call the tool
                try:
                    if isinstance(args_obj, dict):
                        result = tool.fn(**args_obj)
                    else:
                        result = tool.fn()
                except Exception as e:
                    result = {"error": str(e)}

                tracer.add("tool.result", tool=tool_name, call_id=call_id, result=result)

                # Provide tool output back to the model in required format
                input_list.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps(result, ensure_ascii=False)
                        if not isinstance(result, str)
                        else result,
                    }
                )

            # Continue loop: model will see tool outputs and (usually) answer.

        tracer.add("output.ready", answer_preview=(final_text or "")[:120], rounds=rounds)

        return AgentOutput(
            answer=final_text or "",
            trace_id=tracer.trace_id,
            meta={"trace": tracer.to_dict()},
        )
