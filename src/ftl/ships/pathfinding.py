"""A* pathfinding over a Ship's tile graph.

Honors door passability: tile-to-tile edges crossing a room boundary
require the door between them to be `passable_for(is_home_team)`.
Within-room edges are always walkable.

Returns the path *excluding* the start tile (so the first element is
the next step the crew should take).
"""

from __future__ import annotations

import heapq
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship
    from ftl.ships.tile import Tile


_NEIGHBOR_OFFSETS: tuple[tuple[int, int], ...] = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _heuristic(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def find_path(
    ship: Ship,
    start: Tile,
    goal: Tile,
    is_home_team: bool,
) -> list[Tile] | None:
    """Find the shortest tile path from `start` to `goal`.

    Returns the list of tiles *after* `start`, or `None` if no path
    exists. If `start is goal`, returns an empty list.
    """
    if start is goal:
        return []

    start_coord = (start.x, start.y)
    goal_coord = (goal.x, goal.y)

    if goal_coord not in ship.tile_graph:
        return None

    open_set: list[tuple[int, int, tuple[int, int]]] = []
    counter = 0
    heapq.heappush(open_set, (_heuristic(start_coord, goal_coord), counter, start_coord))
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score: dict[tuple[int, int], int] = {start_coord: 0}

    while open_set:
        _, _, current = heapq.heappop(open_set)
        if current == goal_coord:
            return _reconstruct_path(ship, came_from, current)

        for ox, oy in _NEIGHBOR_OFFSETS:
            neighbor_coord = (current[0] + ox, current[1] + oy)
            neighbor = ship.tile_graph.get(neighbor_coord)
            if neighbor is None:
                continue
            current_tile = ship.tile_graph[current]
            if neighbor.room_id != current_tile.room_id:
                door = ship.door_between(current, neighbor_coord)
                if door is not None and not door.passable_for(is_home_team):
                    continue
            tentative = g_score[current] + 1
            if tentative < g_score.get(neighbor_coord, 1 << 30):
                g_score[neighbor_coord] = tentative
                came_from[neighbor_coord] = current
                f = tentative + _heuristic(neighbor_coord, goal_coord)
                counter += 1
                heapq.heappush(open_set, (f, counter, neighbor_coord))

    return None


def _reconstruct_path(
    ship: Ship,
    came_from: dict[tuple[int, int], tuple[int, int]],
    current: tuple[int, int],
) -> list[Tile]:
    coords: list[tuple[int, int]] = [current]
    while current in came_from:
        current = came_from[current]
        coords.append(current)
    coords.reverse()
    # Drop the start tile.
    return [ship.tile_graph[c] for c in coords[1:]]
