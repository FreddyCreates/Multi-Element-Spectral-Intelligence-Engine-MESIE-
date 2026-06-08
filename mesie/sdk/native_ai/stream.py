"""Streaming events from the native local AI engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class StreamPhase(str, Enum):
    BOOT = "boot"
    INDEX = "index"
    LOGIC = "logic"
    REASONING = "reasoning"
    EMERGENCE = "emergence"
    ADAPTATION = "adaptation"
    QUERY = "query"
    MEMORY = "memory"
    MINT = "mint"
    VAULT = "vault"
    DELIVERABLE = "deliverable"
    COMPLETE = "complete"


@dataclass
class StreamEvent:
    """One streamed chunk from native AI generation."""

    phase: StreamPhase
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0
    sovereign: bool = True
    third_party: bool = False
    done: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "message": self.message,
            "data": self.data,
            "progress": round(self.progress, 4),
            "sovereign": self.sovereign,
            "third_party": self.third_party,
            "done": self.done,
        }