"""BatterySystem — temporary extra reactor power on a long cooldown."""

from __future__ import annotations

from ftl.systems.system import System


class BatterySystem(System):
    name = "battery"

    def __init__(self, max_power: int = 2, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.active_remaining: float = 0.0
        self.cooldown_remaining: float = 0.0
