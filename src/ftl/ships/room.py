"""A Room is a connected set of tiles, optionally housing a System.

Tracks oxygen %, fire intensity, breach level, and occupants. Phase 1 keeps
oxygen/fire as inert state (no crew means no consequences yet) and adds the
canonical `take_hit(amount)` entry point used by the damage pipeline to
propagate damage from a weapon hit into the room's installed system.
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

    def take_hit(self, amount: int) -> None:
        """Apply `amount` system damage to the installed system, if any.

        Called by the damage pipeline after hull damage. Crew damage, fire,
        and breach side-effects land in Phase 2.
        """
        if self.system is not None and amount > 0:
            self.system.take_damage(amount)

    def tick(self, dt: float) -> None:
        # Stub. Phase 2 models proper oxygen flow / fire propagation.
        if self.breach > 0:
            self.oxygen = max(0.0, self.oxygen - 0.05 * dt)
