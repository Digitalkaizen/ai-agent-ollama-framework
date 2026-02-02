from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AgentInput:
    message: str
    session_id: Optional[str] = None


@dataclass
class AgentOutput:
    answer: str
    trace_id: str
    meta: Dict[str, Any]
