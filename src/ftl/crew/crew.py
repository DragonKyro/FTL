"""Crew unit — one person aboard a ship."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from ftl.crew.skills import Skill
from ftl.crew.species import Species, SpeciesBehavior

if TYPE_CHECKING:
    from ftl.ships.room import Room
    from ftl.ships.tile import Tile


class CrewState(str, Enum):
    IDLE = "idle"
    MOVING = "moving"
    MANNING = "manning"
    FIGHTING = "fighting"
    REPAIRING = "repairing"
    DYING = "dying"


class Crew:
    """One crew member (friendly or hostile boarder)."""

    def __init__(
        self,
        name: str,
        species: Species,
        behavior: SpeciesBehavior | None = None,
    ) -> None:
        self.name: str = name
        self.species: Species = species
        self.behavior: SpeciesBehavior = behavior or SpeciesBehavior()
        self.hp: int = species.max_hp
        self.max_hp: int = species.max_hp
        self.state: CrewState = CrewState.IDLE
        self.room: Room | None = None
        self.tile: Tile | None = None
        self.target_tile: Tile | None = None
        self.skills: dict[Skill, int] = {s: 0 for s in Skill}

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def tick(self, dt: float) -> None:
        self.behavior.on_tick(self, dt)
