from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class LLMConfig:
    model: str = os.getenv("OPENAI_MODEL", "gpt-5")
    reasoning_effort: str | None = None  # e.g. "low" / "medium" / "high"


class OpenAILLM:
    """
    Minimal wrapper around OpenAI Responses API.

    We keep it small and explicit:
    - one method: create_response(...)
    - caller (Agent) manages the tool loop and input list
    """

    def __init__(self, api_key: str | None = None, config: LLMConfig | None = None) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Put it in .env or export it in your shell."
            )
        self.client = OpenAI(api_key=api_key)
        self.config = config or LLMConfig()

    def create_response(
        self,
        *,
        input_list: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        instructions: str | None = None,
    ) -> Any:
        """
        Calls the Responses API.
        Returns the raw response object from the SDK.
        """
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "input": input_list,
        }
        if tools is not None:
            kwargs["tools"] = tools
        if instructions:
            kwargs["instructions"] = instructions
        if self.config.reasoning_effort:
            kwargs["reasoning"] = {"effort": self.config.reasoning_effort}

        return self.client.responses.create(**kwargs)
