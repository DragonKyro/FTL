"""A Room is a connected set of tiles, optionally housing a System.

Tracks oxygen %, fire intensity, breach level, and occupants. Per-tick
behavior (oxygen depletion, fire spread, etc.) is a Phase-1 implementation
detail; Phase-0 stub demonstrates the tick contract.
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
    fire: int = 0  # intensity 0..100
    breach: int = 0
    system: System | None = None
    occupants: list[Crew] = field(default_factory=list)

    def tick(self, dt: float) -> None:
        # Stub. Phase 1 will model proper oxygen flow / fire propagation.
        if self.breach > 0:
            self.oxygen = max(0.0, self.oxygen - 0.05 * dt)
