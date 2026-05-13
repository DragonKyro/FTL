"""CloakingSystem — temporary 100%-ish evasion + freeze enemy weapons.

Activation:
- Player presses C (via CombatEngine.activate_cloak).
- Requires `is_operational` and `cooldown_remaining == 0`.
- Sets `active_remaining = ACTIVE_SECONDS`; while active, the ship
  gains a large evasion bonus AND the opponent's weapons don't charge.
- When active_remaining hits 0, the system enters cooldown for
  `COOLDOWN_SECONDS` before it can fire again.
"""

from __future__ import annotations

from ftl.systems.system import System

ACTIVE_SECONDS: float = 5.0
COOLDOWN_SECONDS: float = 30.0
EVASION_BONUS: float = 0.6


class CloakingSystem(System):
    name = "cloaking"

    def __init__(self, max_power: int = 3, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.active_remaining: float = 0.0
        self.cooldown_remaining: float = 0.0

    @property
    def is_active(self) -> bool:
        return self.active_remaining > 0.0

    def activate(self) -> bool:
        if not self.is_operational:
            return False
        if self.cooldown_remaining > 0.0:
            return False
        if self.is_active:
            return False
        self.active_remaining = ACTIVE_SECONDS
        return True

    def tick(self, dt: float) -> None:
        super().tick(dt)
        if self.active_remaining > 0.0:
            self.active_remaining = max(0.0, self.active_remaining - dt)
            if self.active_remaining <= 0.0:
                self.cooldown_remaining = COOLDOWN_SECONDS
        elif self.cooldown_remaining > 0.0:
            self.cooldown_remaining = max(0.0, self.cooldown_remaining - dt)
