"""In-flight projectile + beam sweep state.

Phase 1 uses time-based travel: a projectile flies for a fixed `travel_time`
seconds, then `arrived` flips True and the CombatEngine resolves the hit.
The UI interpolates screen position from `elapsed / travel_time`. Real
physics-based projectiles are deferred (no value in Phase 1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship


@dataclass
class Projectile:
    source_ship: Ship
    target_ship: Ship
    target_room_id: str
    damage: int
    shield_piercing: bool
    weapon_family: str  # "laser" | "missile" | "beam" | "bomb" | "ion" | "flak" | "hacking_drone"
    fire_chance: float = 0.0
    breach_chance: float = 0.0
    ion_damage: int = 0
    beam_length: int = 0          # for beams: how many rooms to sweep
    beam_room_damage: int = 0     # damage per room
    travel_time: float = 1.0
    elapsed: float = 0.0
    # Optional payload — used by hacking drones to identify which system
    # to latch on arrival. Stored loosely-typed to avoid a circular import.
    payload: dict | None = None

    @property
    def arrived(self) -> bool:
        return self.elapsed >= self.travel_time

    @property
    def progress(self) -> float:
        if self.travel_time <= 0.0:
            return 1.0
        return min(1.0, self.elapsed / self.travel_time)

    def tick(self, dt: float) -> None:
        if not self.arrived:
            self.elapsed += dt


@dataclass
class BeamSweep:
    """An in-progress beam sweep crossing one or more rooms. Phase 2+."""

    source_ship: Ship
    target_ship: Ship
    start_room_id: str
    end_room_id: str
    progress: float = 0.0
    speed: float = 1.0
    alive: bool = True

    def tick(self, dt: float) -> None:
        if not self.alive:
            return
        self.progress = min(1.0, self.progress + self.speed * dt)
        if self.progress >= 1.0:
            self.alive = False
