"""A single grid cell within a Room. Crew stand on tiles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Tile:
    """A tile on the ship grid.

    `(x, y)` is the *global* ship-grid coordinate, not room-local. Two
    tiles in the same ship share a coordinate space; tiles in two
    different ships are independent universes (each ship has its own
    grid origin at (0, 0)).
    """

    x: int
    y: int
    room_id: str = ""
    walkable: bool = True

    def coord(self) -> tuple[int, int]:
        return self.x, self.y
