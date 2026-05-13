"""BatterySystem — temporary +N reactor power on a long cooldown.

Activation:
- Player presses B (CombatEngine.activate_battery).
- Adds `power_bonus` to the ship's max_reactor_power for `ACTIVE_SECONDS`.
- Then `COOLDOWN_SECONDS` before it can be used again.

The bonus is read by `Ship.max_reactor_power` via the ship's
`battery_bonus` property.
"""

from __future__ import annotations

from ftl.systems.system import System

ACTIVE_SECONDS: float = 8.0
COOLDOWN_SECONDS: float = 30.0


class BatterySystem(System):
    name = "battery"

    def __init__(self, max_power: int = 2, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.active_remaining: float = 0.0
        self.cooldown_remaining: float = 0.0

    @property
    def is_active(self) -> bool:
        return self.active_remaining > 0.0

    @property
    def power_bonus(self) -> int:
        """How much extra reactor power this system contributes right now."""
        if not self.is_active:
            return 0
        # Level 1 → +2, level 2 → +4, etc.
        return 2 * self.level

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
