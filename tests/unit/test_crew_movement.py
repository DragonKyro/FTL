"""Crew path advancement + manning auto-assignment."""

from __future__ import annotations

from ftl.crew.crew import CrewState
from ftl.crew.movement import BASE_TILE_TIME, tick_movement
from ftl.data.registry import Registry
from ftl.ships.pathfinding import find_path
from ftl.ships.ship import PlayerShip


def _wayfarer() -> PlayerShip:
    reg = Registry()
    reg.load_all()
    return PlayerShip.from_def(reg.ships["wayfarer"], reg)


def test_crew_starts_in_a_room() -> None:
    ship = _wayfarer()
    for crew in ship.crew:
        assert crew.current_tile is not None
        assert crew.current_ship is ship


def test_crew_arrives_at_goal_in_expected_ticks() -> None:
    ship = _wayfarer()
    crew = ship.crew[0]  # Sapien on bridge
    start = crew.current_tile
    assert start is not None
    # Target an adjacent room.
    goal = ship.tile_graph[(1, 0)]
    path = find_path(ship, start, goal, is_home_team=True)
    assert path is not None and len(path) == 1
    crew.path = list(path)
    crew.state = CrewState.MOVING

    # 1 tile @ BASE_TILE_TIME seconds. Tick until arrival.
    dt = 1.0 / 60.0
    ticks = 0
    while crew.path and ticks < 200:
        tick_movement(ship, dt)
        ticks += 1
    assert not crew.path
    assert crew.current_tile is goal


def test_manning_auto_assigns_when_crew_in_system_room() -> None:
    ship = _wayfarer()
    # Sapien starts on the bridge (piloting). After one tick of movement,
    # manning should be assigned.
    tick_movement(ship, 1.0 / 60.0)
    piloting = ship.systems.get("piloting")
    assert piloting is not None
    assert piloting.manning_crew is not None


def test_manning_clears_when_crew_leaves_room() -> None:
    ship = _wayfarer()
    tick_movement(ship, 1.0 / 60.0)
    piloting = ship.systems["piloting"]
    original_manner = piloting.manning_crew
    assert original_manner is not None

    # Send the manner away.
    goal = ship.tile_graph[(2, 0)]  # shield_room
    path = find_path(ship, original_manner.current_tile, goal, True)
    assert path is not None
    original_manner.path = list(path)

    dt = 1.0 / 60.0
    ticks = 0
    while original_manner.path and ticks < 500:
        tick_movement(ship, dt)
        ticks += 1
    # The crew left piloting; piloting's manning_crew should no longer be them.
    assert piloting.manning_crew is not original_manner
