"""HackingSystem — fires a drone at an enemy system; activate to disable + damage.

Two phases:
1. **Launch.** Player presses H → CombatEngine spawns a HackingDrone
   Projectile flying to the target system's room (~2s).
2. **Latch.** On arrival, `latched_system` is set; system status icon
   on the enemy ship reads "HACKED" but is still operational.
3. **Activate.** Player presses H again → if latched + cooldown == 0,
   the target system is disabled for ACTIVE_SECONDS (effective_power
   forced to 0) and takes 1 damage per second.
4. **Cooldown.** After active period, target is released; cooldown
   begins.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.systems.system import System

if TYPE_CHECKING:
    from ftl.ships.ship import Ship

ACTIVE_SECONDS: float = 7.0
COOLDOWN_SECONDS: float = 25.0
DAMAGE_PER_SEC: float = 1.0


class HackingSystem(System):
    name = "hacking"

    def __init__(self, max_power: int = 3, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.active_remaining: float = 0.0
        self.cooldown_remaining: float = 0.0
        self.latched_system: System | None = None
        self.latched_on_ship: Ship | None = None
        self.damage_accum: float = 0.0
        self.drone_in_flight: bool = False

    @property
    def is_active(self) -> bool:
        return self.active_remaining > 0.0

    @property
    def is_latched(self) -> bool:
        return self.latched_system is not None and not self.is_active

    @property
    def can_launch(self) -> bool:
        return (
            self.is_operational
            and not self.drone_in_flight
            and self.latched_system is None
            and self.cooldown_remaining <= 0.0
        )

    @property
    def can_activate(self) -> bool:
        return self.is_latched and self.cooldown_remaining <= 0.0

    def begin_launch(self) -> None:
        self.drone_in_flight = True

    def on_drone_arrival(self, target_system: System, on_ship: Ship) -> None:
        self.drone_in_flight = False
        self.latched_system = target_system
        self.latched_on_ship = on_ship

    def activate(self) -> bool:
        if not self.can_activate:
            return False
        self.active_remaining = ACTIVE_SECONDS
        if self.latched_system is not None:
            self.latched_system.hacked = True
        return True

    def tick(self, dt: float) -> None:
        super().tick(dt)
        if self.active_remaining > 0.0:
            self.active_remaining = max(0.0, self.active_remaining - dt)
            if self.latched_system is not None:
                self.damage_accum += DAMAGE_PER_SEC * dt
                while self.damage_accum >= 1.0 and (
                    self.latched_system.damage < self.latched_system.level
                ):
                    self.latched_system.take_damage(1)
                    self.damage_accum -= 1.0
            if self.active_remaining <= 0.0:
                self.cooldown_remaining = COOLDOWN_SECONDS
                if self.latched_system is not None:
                    self.latched_system.hacked = False
                self.latched_system = None
                self.latched_on_ship = None
                self.damage_accum = 0.0
        elif self.cooldown_remaining > 0.0:
            self.cooldown_remaining = max(0.0, self.cooldown_remaining - dt)
