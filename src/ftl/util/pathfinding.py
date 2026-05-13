"""A* pathfinding on the ship's tile grid. Phase-0 stub.

Crew need pathfinding that respects: closed doors, hostile occupants, fires
to avoid (cowardly species), and current room boundaries.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship
    from ftl.ships.tile import Tile


def find_path(ship: Ship, start: Tile, goal: Tile) -> list[Tile]:
    """Return a tile path from start to goal. Phase-0: returns [start, goal] only."""
    return [start, goal]
