"""EnginesSystem — drives evasion + FTL charge."""

from __future__ import annotations

from ftl.systems.system import System


class EnginesSystem(System):
    name = "engines"

    def __init__(self, max_power: int = 8, level: int = 2) -> None:
        # Default level = 2. 5% evasion per power.
        super().__init__(max_power=max_power, level=level)

    @property
    def evasion_chance(self) -> float:
        return min(0.6, 0.05 * self.effective_power)
