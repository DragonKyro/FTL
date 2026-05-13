"""HackingSystem — fires a hacking drone that latches onto an enemy system."""

from __future__ import annotations

from ftl.systems.system import System


class HackingSystem(System):
    name = "hacking"

    def __init__(self, max_power: int = 3, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.active_remaining: float = 0.0
        self.cooldown_remaining: float = 0.0
        self.target_system: str | None = None
