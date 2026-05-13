"""Top-level Game state + per-playthrough Run state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ftl.config import (
    DEFAULT_STARTING_DRONE_PARTS,
    DEFAULT_STARTING_FUEL,
    DEFAULT_STARTING_MISSILES,
    DEFAULT_STARTING_SCRAP,
)
from ftl.core.event_bus import EventBus
from ftl.core.rng import RNG
from ftl.core.simulation import Simulation

if TYPE_CHECKING:
    from ftl.ships.ship import PlayerShip


@dataclass
class Run:
    """Per-playthrough state. One per active playthrough."""

    rng: RNG
    player_ship: PlayerShip | None = None
    scrap: int = DEFAULT_STARTING_SCRAP
    fuel: int = DEFAULT_STARTING_FUEL
    missiles: int = DEFAULT_STARTING_MISSILES
    drone_parts: int = DEFAULT_STARTING_DRONE_PARTS
    sector_index: int = 0
    story_flags: set[str] = field(default_factory=set)
    difficulty: str = "normal"


class Game:
    """Top-level container for active game state."""

    def __init__(self, seed: int | None = None) -> None:
        self.simulation: Simulation = Simulation()
        self.event_bus: EventBus = EventBus()
        self.run: Run | None = None
        self._seed = seed

    def new_run(self, seed: int | None = None) -> Run:
        self.simulation.reset()
        self.event_bus.clear()
        chosen_seed = seed if seed is not None else self._seed
        self.run = Run(rng=RNG(chosen_seed))
        return self.run
