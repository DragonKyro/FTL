"""Damage pipeline behavior: evasion, shield absorption, hull + system damage."""

from __future__ import annotations

from random import Random

from ftl.combat.damage import DamageEvent
from ftl.combat.pipeline import apply_damage
from ftl.ships.room import Room
from ftl.ships.ship import EnemyShip, PlayerShip
from ftl.systems.engines import EnginesSystem
from ftl.systems.shields import ShieldsSystem


def _ship_with_shields(layers: int) -> EnemyShip:
    ship = EnemyShip(name="t", max_hull=20)
    ship.add_room(Room(id="shield_room"))
    ship.add_room(Room(id="empty_room"))  # systemless room for clean hull-only hits
    shields = ShieldsSystem(level=2 * max(layers, 1))
    shields.set_power(2 * max(layers, 1))
    shields.current_layers = layers
    ship.install_system(shields, "shield_room")
    return ship


def test_zero_damage_event_short_circuits():
    ship = EnemyShip(name="t", max_hull=20)
    event = DamageEvent(ship=ship, room_id="any", damage=0)
    result = apply_damage(event, Random(0))
    assert result.hull_damage == 0
    assert result.shield_absorbed is False


def test_laser_absorbed_by_shields():
    ship = _ship_with_shields(layers=1)
    event = DamageEvent(ship=ship, room_id="shield_room", damage=1)
    result = apply_damage(event, Random(0))
    assert result.shield_absorbed
    assert ship.shields is not None
    assert ship.shields.current_layers == 0
    assert ship.hull.current == 20


def test_missile_bypasses_shields_and_hits_hull():
    ship = _ship_with_shields(layers=1)
    # Target the empty room so the missile damages only hull (not the
    # shield system, which would as a side effect drop the layer).
    event = DamageEvent(
        ship=ship, room_id="empty_room", damage=2, shield_piercing=True
    )
    result = apply_damage(event, Random(0))
    assert not result.shield_absorbed
    assert result.hull_damage == 2
    assert ship.hull.current == 18
    assert ship.shields is not None
    assert ship.shields.current_layers == 1  # shield system unharmed


def test_evasion_can_miss_with_engines_powered():
    ship = EnemyShip(name="t", max_hull=20)
    ship.add_room(Room(id="engine_room"))
    engines = EnginesSystem()
    engines.set_power(2)
    ship.install_system(engines, "engine_room")
    # Force a "miss" by patching Random
    rng = Random(0)
    # Engines at level 2, full power: 10% evasion. Use a deterministic seed
    # where the first sample is < 0.10.
    rng_low = Random()
    rng_low.random = lambda: 0.0  # type: ignore[assignment]
    event = DamageEvent(ship=ship, room_id="engine_room", damage=2)
    result = apply_damage(event, rng_low)
    assert result.missed
    assert ship.hull.current == 20


def test_hit_propagates_system_damage():
    ship = EnemyShip(name="t", max_hull=20)
    ship.add_room(Room(id="weapons_room"))
    from ftl.systems.weapons import WeaponsSystem

    ws = WeaponsSystem()
    ws.set_power(2)
    ship.install_system(ws, "weapons_room")
    event = DamageEvent(ship=ship, room_id="weapons_room", damage=1)
    result = apply_damage(event, Random(0))
    assert result.hull_damage == 1
    assert result.system_damage == 1
    assert ws.damage == 1
    assert ship.hull.current == 19
