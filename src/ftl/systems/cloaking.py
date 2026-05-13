"""CloakingSystem — temporary 100% evasion + weapon-charge pause for enemies."""

from __future__ import annotations

from ftl.systems.system import System


class CloakingSystem(System):
    name = "cloaking"

    def __init__(self, max_power: int = 3, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.active_remaining: float = 0.0
        self.cooldown_remaining: float = 0.0

    def tick(self, dt: float) -> None:
        super().tick(dt)
        if self.active_remaining > 0:
            self.active_remaining = max(0.0, self.active_remaining - dt)
        elif self.cooldown_remaining > 0:
            self.cooldown_remaining = max(0.0, self.cooldown_remaining - dt)
