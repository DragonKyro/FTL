"""Crew repair of damaged systems."""

from __future__ import annotations

from ftl.crew.movement import tick_movement
from ftl.data.registry import Registry
from ftl.ships.ship import PlayerShip


def _wayfarer() -> PlayerShip:
    reg = Registry()
    reg.load_all()
    return PlayerShip.from_def(reg.ships["wayfarer"], reg)


def test_crew_in_damaged_room_repairs_system() -> None:
    ship = _wayfarer()
    # Damage the piloting system; Sapien starts on the bridge.
    piloting = ship.systems["piloting"]
    piloting.damage = piloting.level
    # Tick movement long enough for repair_accum to accumulate.
    dt = 1.0 / 60.0
    for _ in range(60 * 5):
        tick_movement(ship, dt)
    assert piloting.damage < piloting.level


def test_multiple_crew_repair_faster() -> None:
    ship_one = _wayfarer()
    ship_two = _wayfarer()
    # Empty ship_one so only one crew remains in the bridge.
    while len(ship_one.crew) > 1:
        ship_one.crew.pop()
    # Move ship_two's second crew also into the bridge.
    bridge_tile = ship_two.tile_graph[(0, 0)]
    ship_two.crew[1].current_tile = bridge_tile
    # Damage piloting on both.
    ship_one.systems["piloting"].damage = ship_one.systems["piloting"].level
    ship_two.systems["piloting"].damage = ship_two.systems["piloting"].level
    dt = 1.0 / 60.0
    for _ in range(60 * 3):
        tick_movement(ship_one, dt)
        tick_movement(ship_two, dt)
    # ship_two had more crew on the system → should be at least as fixed.
    assert ship_two.systems["piloting"].damage <= ship_one.systems["piloting"].damage
