"""Fire spread + damage + vacuum extinguishment."""

from __future__ import annotations

from ftl.data.registry import Registry
from ftl.ships.hazards import FIRE_SPREAD_THRESHOLD, tick_hazards
from ftl.ships.ship import PlayerShip


def _wayfarer() -> PlayerShip:
    reg = Registry()
    reg.load_all()
    return PlayerShip.from_def(reg.ships["wayfarer"], reg)


def test_fire_grows_with_oxygen() -> None:
    ship = _wayfarer()
    bridge = ship.rooms["bridge"]
    bridge.fire = 10.0
    bridge.oxygen = 1.0
    for _ in range(60 * 5):
        tick_hazards(ship, 1.0 / 60.0)
    assert bridge.fire > 10.0


def test_fire_extinguishes_in_vacuum() -> None:
    ship = _wayfarer()
    bridge = ship.rooms["bridge"]
    bridge.fire = 50.0
    bridge.oxygen = 0.0
    for _ in range(60 * 10):
        tick_hazards(ship, 1.0 / 60.0)
    assert bridge.fire == 0.0


def test_fire_spreads_through_open_door() -> None:
    ship = _wayfarer()
    bridge = ship.rooms["bridge"]
    gun_bay = ship.rooms["gun_bay"]
    bridge.fire = FIRE_SPREAD_THRESHOLD + 5
    bridge.oxygen = 1.0
    gun_bay.oxygen = 1.0
    for _ in range(60 * 2):
        tick_hazards(ship, 1.0 / 60.0)
    assert gun_bay.fire > 0


def test_fire_blocked_by_closed_door() -> None:
    ship = _wayfarer()
    bridge = ship.rooms["bridge"]
    gun_bay = ship.rooms["gun_bay"]
    bridge.fire = FIRE_SPREAD_THRESHOLD + 5
    bridge.oxygen = 1.0
    gun_bay.oxygen = 1.0
    # Close the door between them.
    for door in ship.doors.values():
        if {door.room_a, door.room_b} == {"bridge", "gun_bay"}:
            door.force_closed = True
    for _ in range(60 * 2):
        tick_hazards(ship, 1.0 / 60.0)
    assert gun_bay.fire == 0


def test_fire_damages_crew() -> None:
    ship = _wayfarer()
    crew = ship.crew[0]
    room = crew.current_room()
    assert room is not None
    room.fire = 50.0
    room.oxygen = 1.0
    starting_hp = crew.hp
    for _ in range(60 * 2):
        tick_hazards(ship, 1.0 / 60.0)
    assert crew.hp < starting_hp
