"""EnginesSystem — drives evasion + FTL charge."""

from __future__ import annotations

from ftl.systems.system import System


class EnginesSystem(System):
    name = "engines"

    @property
    def evasion_chance(self) -> float:
        return min(0.6, 0.05 * self.effective_power)
