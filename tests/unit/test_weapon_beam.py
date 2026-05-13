"""Beam weapon family: sweeps multiple rooms; shields fully block."""

from __future__ import annotations

from random import Random

from ftl.data.registry import Registry
from ftl.scenarios.loader import build_combat_from_scenario


def _engine_with_player_beam():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(0)
    )
    # Replace player weapons with a beam.
    from ftl.weapons.beam import BeamWeapon
    from ftl.weapons.weapon import WeaponStats

    engine.player.weapons.clear()
    stats = WeaponStats(
        id="beam", name="Test Beam", family="beam",
        beam_length=3, beam_room_damage=2, charge_time=2.0, power_required=1,
    )
    weapon = BeamWeapon(stats)
    weapon.powered = True
    weapon.charge_progress = stats.charge_time
    weapon.target_room_id = "gun_bay"
    engine.player.weapons.append(weapon)
    # Power up weapons system enough for the beam.
    engine.player.systems["weapons"].set_power(1)
    return engine


def test_beam_blocked_entirely_by_any_shield_layer() -> None:
    engine = _engine_with_player_beam()
    # Force enemy shields up.
    engine.enemy.systems["shields"].set_power(2)
    engine.enemy.shields.current_layers = 1
    starting_hull = engine.enemy.hull.current
    engine.tick(1.0 / 60.0)  # one tick: fires + projectile spawn
    # Tick until projectile arrives (~1.5s).
    for _ in range(60 * 3):
        engine.tick(1.0 / 60.0)
    # Hull should be unchanged (beam blocked).
    assert engine.enemy.hull.current == starting_hull


def test_beam_hits_multiple_rooms_when_unshielded() -> None:
    engine = _engine_with_player_beam()
    engine.enemy.systems["shields"].set_power(0)
    engine.enemy.shields.current_layers = 0
    starting_hull = engine.enemy.hull.current
    engine.tick(1.0 / 60.0)
    for _ in range(60 * 3):
        engine.tick(1.0 / 60.0)
    # Beam hit beam_length rooms with beam_room_damage each: 3 × 2 = 6 hull damage.
    assert engine.enemy.hull.current <= starting_hull - 3
