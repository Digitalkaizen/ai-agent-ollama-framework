### ASCII Architecture Diagram

+----------------------------------------------------------------------------------+
| Interfaces |
| |
| CLI Adapter (typer) Web Adapter (FastAPI) |
| python -m agentkit.adapters.cli uvicorn agentkit.adapters.web:app |
+-----------------------------+----------------------------------+-----------------+
| |
v v
+----------------------------------------------------------------------------------+
| Agent |
| |
| Agent.run(input) |
| - intent detection (calc_intent > time_intent) |
| - policy enforcement (no hallucinated tools / math must use tools) |
| - loop orchestration (max_rounds) |
| - tracing events |
+-----------------------------+-------------------------------+--------------------+
| |
| builds messages | emits trace_id
v v
+--------------------------------------+ +-----------------------------+
| LLM | | Tracer |
| | | - llm.request/response |
| OllamaLLM.chat(messages) | | - tool.call/tool.result |
| POST http://localhost:11434/api/chat|
 | - protocol decisions |
| | | - output.ready |
+-----------------------------+--------+ +-----------------------------+
|
| returns 1-line JSON
v
+----------------------------------------------------------------------------------+
| JSON Protocol (Contract) |
| |
| Tool call: {"tool":"tool_name","args":{...}} |
| Final: {"final":"..."} |
| |
| Guards: |
| - reject "final" for calc until math tool used |
| - reject time tool calls for calc_intent |
| - retry on invalid / unknown tool selection |
+-----------------------------+-------------------------------+--------------------+
|
| tool_name + args
v
+----------------------------------------------------------------------------------+
| Tool Registry |
| |
| ToolRegistry |
| - register(Tool) |
| - get(name) |
| |
| Tools: |
| - time_now_utc() -> "YYYY-MM-DD HH:MM:SS UTC" |
| - math_mul(a,b) -> number |
| - math_add(a,b) -> number |
+-----------------------------+-------------------------------+--------------------+
|
| deterministic execution
v
+----------------------------------------------------------------------------------+
| Result |
| |
| observation (tool output) -> fed back to LLM |
| final answer -> returned to CLI / Web UI |
+----------------------------------------------------------------------------------+