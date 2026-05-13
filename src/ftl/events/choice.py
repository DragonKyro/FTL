"""A Choice presented during a story event."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Choice:
    text: str
    outcome_id: str | None = None
    requires_flags: list[str] = field(default_factory=list)
    forbids_flags: list[str] = field(default_factory=list)
