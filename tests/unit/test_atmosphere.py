"""Oxygen distribution + flow + suffocation."""

from __future__ import annotations

from ftl.data.registry import Registry
from ftl.ships.atmosphere import tick_atmosphere
from ftl.ships.ship import PlayerShip


def _wayfarer() -> PlayerShip:
    reg = Registry()
    reg.load_all()
    ship = PlayerShip.from_def(reg.ships["wayfarer"], reg)
    # Drain all rooms so we can watch oxygen rise.
    for room in ship.rooms.values():
        room.oxygen = 0.0
    oxygen = ship.oxygen_system
    assert oxygen is not None
    oxygen.set_power(1)
    return ship


def test_oxygen_system_fills_its_own_room() -> None:
    ship = _wayfarer()
    oxygen_room = next(r for r in ship.rooms.values() if r.system is ship.oxygen_system)
    # Force-close every door so oxygen can't drain to other rooms; we're
    # testing only the production half of the loop here.
    for door in ship.doors.values():
        door.force_closed = True
    for _ in range(60 * 30):  # 30 simulated seconds
        tick_atmosphere(ship, 1.0 / 60.0)
    assert oxygen_room.oxygen > 0.5


def test_oxygen_flows_to_adjacent_rooms() -> None:
    ship = _wayfarer()
    oxygen_room = next(r for r in ship.rooms.values() if r.system is ship.oxygen_system)
    # Bridge is several doors away from the oxygen room on the new ship.
    target_room = ship.rooms["bridge"]
    for _ in range(60 * 180):  # 3 simulated minutes — bigger ship needs it
        tick_atmosphere(ship, 1.0 / 60.0)
    assert oxygen_room.oxygen > 0.4
    assert target_room.oxygen > 0.2


def test_breach_vents_oxygen() -> None:
    ship = _wayfarer()
    # Fill bridge with oxygen, breach it, no oxygen system production.
    bridge = ship.rooms["bridge"]
    bridge.oxygen = 1.0
    bridge.breach = 1.0
    oxygen = ship.oxygen_system
    if oxygen is not None:
        oxygen.set_power(0)
    # Force-close doors so flow can't refill from neighbors.
    for door in ship.doors.values():
        door.force_closed = True
    for _ in range(60 * 10):
        tick_atmosphere(ship, 1.0 / 60.0)
    assert bridge.oxygen < 0.2


def test_crew_suffocate_in_low_oxygen() -> None:
    ship = _wayfarer()
    crew = ship.crew[0]
    room = crew.current_room()
    assert room is not None
    room.oxygen = 0.0
    # Damage / disable oxygen system to prevent refill.
    oxygen = ship.oxygen_system
    if oxygen is not None:
        oxygen.set_power(0)
    starting_hp = crew.hp
    for _ in range(60 * 5):  # 5s
        tick_atmosphere(ship, 1.0 / 60.0)
    assert crew.hp < starting_hp
