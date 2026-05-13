"""A Room is a connected set of tiles, optionally housing a System.

Tracks oxygen, fire, breach, and occupants. Per-tick *room-internal*
behavior is minimal here; the global atmosphere/hazards simulation lives
in `ships.atmosphere` and `ships.hazards`, which run in `Ship.tick`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ftl.ships.tile import Tile

if TYPE_CHECKING:
    from ftl.crew.crew import Crew
    from ftl.systems.system import System


@dataclass
class Room:
    id: str
    tiles: list[Tile] = field(default_factory=list)
    oxygen: float = 1.0  # 0.0 .. 1.0
    fire: float = 0.0  # 0.0 .. 100.0
    breach: float = 0.0  # 0.0 .. 100.0
    fire_system_damage_accum: float = 0.0
    system: System | None = None
    occupants: list[Crew] = field(default_factory=list)

    def take_hit(self, amount: int) -> None:
        """Apply system damage from a weapon hit landing in this room."""
        if self.system is not None and amount > 0:
            self.system.take_damage(amount)

    def tick(self, dt: float) -> None:
        """No-op in Phase 2. Atmosphere + hazards run at ship level."""
