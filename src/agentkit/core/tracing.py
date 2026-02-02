import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TraceEvent:
    t: float
    name: str
    data: Dict[str, Any] = field(default_factory=dict)


class Tracer:
    def __init__(self) -> None:
        self.trace_id = str(uuid.uuid4())
        self.events: List[TraceEvent] = []

    def add(self, name: str, **data: Any) -> None:
        self.events.append(TraceEvent(t=time.time(), name=name, data=dict(data)))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "events": [
                {"t": e.t, "name": e.name, "data": e.data}
                for e in self.events
            ],
        }
