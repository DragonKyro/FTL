"""Species data + behavior hook protocol.

`Species` is a runtime dataclass mirroring `data.schemas.SpeciesDef`.
`SpeciesBehavior` is the override-point for non-stat traits. Concrete
behaviors (Sapien, Halene, Mhirsa, ...) live in `species_behaviors/`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.crew.crew import Crew
    from ftl.ships.room import Room


@dataclass
class Species:
    id: str
    name: str
    max_hp: int = 100
    move_speed: float = 1.0
    damage_mult: float = 1.0
    fire_resistance: float = 0.0
    suffocation_mult: float = 1.0
    repair_speed: float = 1.0
    combat_damage: float = 1.0
    traits: list[str] = field(default_factory=list)


class SpeciesBehavior:
    """Hook protocol for trait-driven behavior. Default = no-op everywhere."""

    def on_tick(self, crew: Crew, dt: float) -> None:
        return None

    def on_combat_damage_dealt(
        self, crew: Crew, victim: Crew, amount: float
    ) -> None:
        return None

    def on_room_enter(self, crew: Crew, room: Room) -> None:
        return None

    def melee_damage(self, attacker: Crew, base: float) -> float:
        """Allow species to scale outgoing melee damage."""
        return base

    def move_speed_multiplier(self, crew: Crew) -> float:
        """Allow species to scale how fast they walk tile-to-tile."""
        return 1.0
