"""A* over a Ship's tile graph."""

from __future__ import annotations

from ftl.data.registry import Registry
from ftl.ships.pathfinding import find_path
from ftl.ships.ship import PlayerShip


def _wayfarer() -> PlayerShip:
    reg = Registry()
    reg.load_all()
    ship_def = reg.ships["wayfarer"]
    return PlayerShip.from_def(ship_def, reg)


def test_path_to_self_is_empty() -> None:
    ship = _wayfarer()
    bridge_tile = ship.tile_graph[(0, 0)]
    path = find_path(ship, bridge_tile, bridge_tile, is_home_team=True)
    assert path == []


def test_path_across_one_door() -> None:
    ship = _wayfarer()
    start = ship.tile_graph[(0, 0)]   # bridge
    goal = ship.tile_graph[(1, 0)]    # gun_bay (adjacent)
    path = find_path(ship, start, goal, is_home_team=True)
    assert path is not None
    assert len(path) == 1
    assert path[-1] is goal


def test_path_across_multiple_doors() -> None:
    ship = _wayfarer()
    start = ship.tile_graph[(0, 0)]   # bridge
    goal = ship.tile_graph[(0, 2)]    # teleporter_pad
    path = find_path(ship, start, goal, is_home_team=True)
    assert path is not None
    # Path length = Manhattan distance for an unobstructed grid.
    assert len(path) == 2
    assert path[-1] is goal


def test_force_closed_door_blocks_enemy() -> None:
    ship = _wayfarer()
    # Force-close the bridge↔gun_bay door.
    for door in ship.doors.values():
        if {door.room_a, door.room_b} == {"bridge", "gun_bay"}:
            door.force_closed = True
            break
    start = ship.tile_graph[(0, 0)]
    goal = ship.tile_graph[(1, 0)]
    # Home team passes through closed doors freely.
    home_path = find_path(ship, start, goal, is_home_team=True)
    assert home_path is not None and len(home_path) == 1
    # Boarders cannot.
    boarder_path = find_path(ship, start, goal, is_home_team=False)
    # The boarder may still find a way around (bridge → medbay → engine_room → gun_bay).
    if boarder_path is not None:
        # If a path exists, it should not include the direct door.
        assert (1, 0) in {(t.x, t.y) for t in boarder_path}
        assert len(boarder_path) > 1
