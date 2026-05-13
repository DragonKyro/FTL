"""Quest — a multi-step event chain with state."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Quest:
    id: str
    name: str
    steps: list[str] = field(default_factory=list)
    current_step: int = 0
    completed: bool = False

    def advance(self) -> None:
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
        else:
            self.completed = True
