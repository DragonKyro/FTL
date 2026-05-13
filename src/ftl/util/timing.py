"""Timing helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Cooldown:
    """Counts down to zero in tick(dt). Triggers when reset."""

    remaining: float = 0.0
    duration: float = 0.0

    @property
    def ready(self) -> bool:
        return self.remaining <= 0.0

    def start(self, duration: float | None = None) -> None:
        if duration is not None:
            self.duration = duration
        self.remaining = self.duration

    def tick(self, dt: float) -> None:
        if self.remaining > 0.0:
            self.remaining = max(0.0, self.remaining - dt)
