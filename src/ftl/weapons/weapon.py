"""Weapon base + WeaponStats.

The hybrid content model in one file: `WeaponStats` is the immutable
description of a weapon (loaded from YAML); `Weapon` is the stateful runtime
wrapper around it (charge progress, powered/unpowered, firing). Family
subclasses (`BeamWeapon`, `LaserWeapon`, ...) implement `_on_fire`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.room import Room


@dataclass(frozen=True)
class WeaponStats:
    id: str
    name: str
    family: str  # "beam" | "laser" | "missile" | "bomb" | "ion" | "flak"
    damage: int = 0
    charge_time: float = 10.0
    shield_pierce: int = 0
    breach_chance: float = 0.0
    fire_chance: float = 0.0
    stun_seconds: float = 0.0
    ion_damage: int = 0
    crew_damage: int = 0
    system_damage: int = 0
    beam_length: float = 0.0
    missile_cost: int = 0
    power_required: int = 1
    sprite_key: str = ""
    sfx_key: str = ""


class Weapon:
    """Charge-and-fire runtime wrapper around a WeaponStats."""

    def __init__(self, stats: WeaponStats) -> None:
        self.stats: WeaponStats = stats
        self.powered: bool = False
        self.charge_progress: float = 0.0

    @property
    def ready(self) -> bool:
        return self.powered and self.charge_progress >= self.stats.charge_time

    def tick(self, dt: float) -> None:
        if self.powered and self.charge_progress < self.stats.charge_time:
            self.charge_progress = min(
                self.stats.charge_time, self.charge_progress + dt
            )

    def fire(self, target_room: Room) -> bool:
        """Fire if ready. Returns True if a shot was actually launched."""
        if not self.ready:
            return False
        self.charge_progress = 0.0
        self._on_fire(target_room)
        return True

    def _on_fire(self, target_room: Room) -> None:
        """Override in family subclasses to spawn projectiles/beams."""
