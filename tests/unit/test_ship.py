"""Ship construction: layout, rooms, system installation."""

from __future__ import annotations

from ftl.ships.room import Room
from ftl.ships.ship import PlayerShip, Ship
from ftl.systems.shields import ShieldsSystem
from ftl.systems.weapons import WeaponsSystem


def test_ship_starts_at_full_hull():
    ship = Ship(name="Pioneer", max_hull=20)
    assert ship.hull.current == 20
    assert ship.hull.maximum == 20
    assert not ship.hull.destroyed


def test_player_ship_is_a_ship():
    ship = PlayerShip(name="Pioneer")
    assert isinstance(ship, Ship)


def test_add_room_then_install_system():
    ship = Ship()
    bridge = Room(id="bridge")
    ship.add_room(bridge)
    assert "bridge" in ship.rooms

    weapons = WeaponsSystem()
    ship.install_system(weapons, "bridge")
    assert "weapons" in ship.systems
    assert ship.rooms["bridge"].system is weapons


def test_multiple_systems_in_their_own_rooms():
    ship = Ship()
    ship.add_room(Room(id="bridge"))
    ship.add_room(Room(id="shield_room"))
    ship.install_system(WeaponsSystem(), "bridge")
    ship.install_system(ShieldsSystem(), "shield_room")

    assert ship.systems["weapons"].__class__ is WeaponsSystem
    assert ship.systems["shields"].__class__ is ShieldsSystem


def test_hull_damage_and_destruction():
    ship = Ship(max_hull=3)
    ship.hull.damage(2)
    assert ship.hull.current == 1
    assert not ship.hull.destroyed
    ship.hull.damage(5)
    assert ship.hull.current == 0
    assert ship.hull.destroyed
