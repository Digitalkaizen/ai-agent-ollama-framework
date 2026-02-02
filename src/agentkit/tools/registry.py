from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]
    # JSON Schema for function calling (optional for tools without args)
    parameters: dict[str, Any] | None = None


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def list(self) -> list[Tool]:
        return list(self._tools.values())

    def as_openai_tools(self) -> list[dict[str, Any]]:
        """
        Convert internal tools into OpenAI function-calling schema:
        [{"type":"function","name":...,"description":...,"parameters":...}, ...]
        """
        out: list[dict[str, Any]] = []
        for t in self.list():
            out.append(
                {
                    "type": "function",
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters
                    or {"type": "object", "properties": {}, "required": []},
                }
            )
        return out
