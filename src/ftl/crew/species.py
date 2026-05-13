"""Species data + behavior hooks.

`Species` is a runtime dataclass mirroring `data.schemas.SpeciesDef`.
`SpeciesBehavior` is the override-point for non-stat traits: oxygen-draining
metallic species, room-locking crystalline species, energy-providing low-HP
species, mind-affecting amphibious species, etc. Each special trait gets its
own behavior subclass.
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
    """Override hooks for trait-driven behavior. Default = no-op."""

    def on_tick(self, crew: Crew, dt: float) -> None:
        return None

    def on_combat_damage_dealt(self, crew: Crew, victim: Crew, amount: int) -> None:
        return None

    def on_room_enter(self, crew: Crew, room: Room) -> None:
        return None
