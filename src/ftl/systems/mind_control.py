"""MindControlSystem — temporarily turns an enemy crew member against their ship."""

from __future__ import annotations

from ftl.systems.system import System


class MindControlSystem(System):
    name = "mind_control"

    def __init__(self, max_power: int = 3, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.active_remaining: float = 0.0
        self.cooldown_remaining: float = 0.0
