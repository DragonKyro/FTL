"""Medbay healing logic."""

from __future__ import annotations

from ftl.crew.movement import tick_movement
from ftl.data.registry import Registry
from ftl.ships.pathfinding import find_path
from ftl.ships.ship import PlayerShip


def _wayfarer() -> PlayerShip:
    reg = Registry()
    reg.load_all()
    ship = PlayerShip.from_def(reg.ships["wayfarer"], reg)
    medbay = ship.medbay
    assert medbay is not None
    medbay.set_power(1)
    return ship


def _send_crew_to_medbay(ship, crew) -> None:  # type: ignore[no-untyped-def]
    medbay_room = next(r for r in ship.rooms.values() if r.system is ship.medbay)
    goal = medbay_room.tiles[0]
    path = find_path(ship, crew.current_tile, goal, True)
    assert path is not None
    crew.path = list(path)
    dt = 1.0 / 60.0
    while crew.path:
        tick_movement(ship, dt)


def test_crew_in_medbay_heals() -> None:
    ship = _wayfarer()
    crew = ship.crew[0]
    crew.hp = 50.0
    _send_crew_to_medbay(ship, crew)
    starting_hp = crew.hp
    dt = 1.0 / 60.0
    for _ in range(60 * 2):  # 2s
        tick_movement(ship, dt)
    assert crew.hp > starting_hp


def test_unpowered_medbay_does_not_heal() -> None:
    ship = _wayfarer()
    crew = ship.crew[0]
    crew.hp = 50.0
    _send_crew_to_medbay(ship, crew)
    if ship.medbay is not None:
        ship.medbay.set_power(0)
    starting_hp = crew.hp
    for _ in range(60 * 2):
        tick_movement(ship, 1.0 / 60.0)
    assert crew.hp == starting_hp


def test_full_hp_crew_in_medbay_is_idle() -> None:
    ship = _wayfarer()
    crew = ship.crew[0]
    crew.hp = float(crew.max_hp)
    _send_crew_to_medbay(ship, crew)
    tick_movement(ship, 1.0 / 60.0)
    from ftl.crew.crew import CrewState

    assert crew.state is not CrewState.HEALING
