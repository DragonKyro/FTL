"""TeleporterSystem — sends crew to enemy ship and back."""

from __future__ import annotations

from ftl.systems.system import System


class TeleporterSystem(System):
    name = "teleporter"

    def __init__(self, max_power: int = 4, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.cooldown_remaining: float = 0.0

    def tick(self, dt: float) -> None:
        super().tick(dt)
        if self.cooldown_remaining > 0:
            self.cooldown_remaining = max(0.0, self.cooldown_remaining - dt)
