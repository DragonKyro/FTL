"""Doors connect adjacent rooms.

Phase 2 doors are inferred from room geometry. Each door sits on the edge
between two adjacent rooms and connects exactly one tile pair (one tile
in each room).

A door is conceptually always "open" — boarders walk through freely —
unless the player has explicitly `force_closed` it. Force-closed doors
block hostile movement, oxygen flow, and fire spread; the home team
walks through them (the door auto-opens for them). Door HP / ion /
breach-the-door mechanics are deferred to Phase 3+.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Door:
    id: str
    room_a: str
    room_b: str
    tile_a: tuple[int, int]  # global coord of the room_a-side tile
    tile_b: tuple[int, int]  # global coord of the room_b-side tile
    force_closed: bool = False
    level: int = 1
    hp: int = 4
    ionized: bool = False

    @property
    def is_open(self) -> bool:
        return not self.force_closed

    def passable_for(self, is_home_team: bool) -> bool:
        """Can a crew of the given team pass this door right now?

        Doors auto-open for the home team. Force-closed doors block any
        non-home crew (boarders in Phase 2 = the player's crew on the
        enemy ship, or vice versa).
        """
        if self.force_closed and not is_home_team:
            return False
        return True

    def toggle(self) -> None:
        self.force_closed = not self.force_closed

    def connects_tiles(self, coord_a: tuple[int, int], coord_b: tuple[int, int]) -> bool:
        pair = {coord_a, coord_b}
        return pair == {self.tile_a, self.tile_b}
