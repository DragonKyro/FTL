"""Crew unit — one person aboard a ship.

Phase 2 adds:
- `home_ship` / `current_ship` (separate because boarders are on the
  *other* ship)
- `current_tile`, `path`, `move_progress` for tile-level movement
- `team` ("player" or "enemy")
- `CrewState.HEALING`, `CrewState.FIGHTING_FIRE` to round out the
  Phase 1 enum

Per-tick crew logic (movement, manning, repair, healing, suffocation,
melee) lives in:
- `ftl.crew.movement` — path advancement + manning auto-assignment + repair
- `ftl.ships.atmosphere` — suffocation damage
- `ftl.ships.hazards` — fire damage to crew
- `ftl.crew.combat` — crew-vs-crew melee

This file just holds state; the modules above mutate it each tick.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from ftl.crew.skills import Skill
from ftl.crew.species import Species, SpeciesBehavior

if TYPE_CHECKING:
    from ftl.ships.room import Room
    from ftl.ships.ship import Ship
    from ftl.ships.tile import Tile


class CrewState(str, Enum):
    IDLE = "idle"
    MOVING = "moving"
    MANNING = "manning"
    REPAIRING = "repairing"
    HEALING = "healing"
    FIGHTING_FIRE = "fighting_fire"
    FIGHTING = "fighting"
    DEAD = "dead"


class Crew:
    """One crew member (friendly or hostile boarder)."""

    def __init__(
        self,
        name: str,
        species: Species,
        team: str = "player",
        behavior: SpeciesBehavior | None = None,
    ) -> None:
        self.name: str = name
        self.species: Species = species
        self.behavior: SpeciesBehavior = behavior or SpeciesBehavior()
        self.team: str = team
        self.hp: float = float(species.max_hp)
        self.max_hp: int = species.max_hp
        self.state: CrewState = CrewState.IDLE
        self.home_ship: Ship | None = None
        self.current_ship: Ship | None = None
        self.current_tile: Tile | None = None
        self.path: list[Tile] = []
        self.move_progress: float = 0.0
        self.repair_accum: float = 0.0
        self.skills: dict[Skill, int] = {s: 0 for s in Skill}

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def current_room(self) -> Room | None:
        if self.current_ship is None or self.current_tile is None:
            return None
        return self.current_ship.rooms.get(self.current_tile.room_id)

    def is_moving(self) -> bool:
        return len(self.path) > 0

    def is_at(self, tile: Tile) -> bool:
        return self.current_tile is tile

    def stop(self) -> None:
        self.path = []
        self.move_progress = 0.0
        if self.alive and self.state is CrewState.MOVING:
            self.state = CrewState.IDLE

    def tick(self, dt: float) -> None:
        """Personal trait-driven tick. Movement/manning/etc are driven by
        the higher-level modules (`crew.movement`, `ships.atmosphere`,
        `ships.hazards`)."""
        self.behavior.on_tick(self, dt)
