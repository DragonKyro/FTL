"""SensorsSystem visibility levels."""

from __future__ import annotations

from ftl.combat.visibility import enemy_visibility
from ftl.data.registry import Registry
from ftl.ships.ship import PlayerShip


def _wayfarer() -> PlayerShip:
    reg = Registry()
    reg.load_all()
    return PlayerShip.from_def(reg.ships["wayfarer"], reg)


def test_unpowered_sensors_visibility_is_minimal() -> None:
    ship = _wayfarer()
    sensors = ship.systems.get("sensors")
    assert sensors is not None
    sensors.set_power(0)
    assert enemy_visibility(ship) == 1


def test_powered_sensors_reveal_more() -> None:
    ship = _wayfarer()
    sensors = ship.systems.get("sensors")
    assert sensors is not None
    sensors.set_power(2)
    # Power=2 → level 2 visibility (room labels, oxygen, fire/breach).
    assert enemy_visibility(ship) >= 2


def test_visibility_capped_at_4() -> None:
    ship = _wayfarer()
    sensors = ship.systems.get("sensors")
    assert sensors is not None
    sensors.set_power(sensors.max_power)
    assert enemy_visibility(ship) <= 4


def test_no_sensors_returns_1() -> None:
    """A ship with no sensors installed shows only outlines."""
    ship = _wayfarer()
    # Remove sensors to simulate an un-equipped ship.
    ship.systems.pop("sensors", None)
    assert enemy_visibility(ship) == 1
