"""Weapon charge behavior and family construction."""

from __future__ import annotations

from ftl.weapons.beam import BeamWeapon
from ftl.weapons.laser import LaserWeapon
from ftl.weapons.weapon import Weapon, WeaponStats


def test_weapon_stats_loads_from_dict():
    raw = {
        "id": "pulse_lance_mk1",
        "name": "Pulse Lance Mk I",
        "family": "laser",
        "damage": 1,
        "charge_time": 10.0,
        "power_required": 1,
    }
    stats = WeaponStats(**raw)
    assert stats.id == "pulse_lance_mk1"
    assert stats.family == "laser"
    assert stats.damage == 1
    assert stats.charge_time == 10.0


def test_unpowered_weapon_does_not_charge(basic_weapon_stats: WeaponStats):
    weapon = Weapon(basic_weapon_stats)
    weapon.tick(5.0)
    assert weapon.charge_progress == 0.0
    assert not weapon.ready


def test_powered_weapon_charges_then_becomes_ready(basic_weapon_stats: WeaponStats):
    weapon = Weapon(basic_weapon_stats)
    weapon.powered = True

    weapon.tick(5.0)
    assert weapon.charge_progress == 5.0
    assert not weapon.ready

    weapon.tick(5.0)
    assert weapon.charge_progress == basic_weapon_stats.charge_time
    assert weapon.ready


def test_firing_resets_charge(basic_weapon_stats: WeaponStats):
    weapon = Weapon(basic_weapon_stats)
    weapon.powered = True
    weapon.tick(basic_weapon_stats.charge_time)
    assert weapon.ready

    # Reuse the base behavior: provide a stand-in target room by importing Room
    from ftl.ships.room import Room

    fired = weapon.fire(Room(id="target"))
    assert fired is True
    assert weapon.charge_progress == 0.0
    assert not weapon.ready


def test_family_subclasses_inherit_charge_behavior(basic_weapon_stats: WeaponStats):
    laser = LaserWeapon(basic_weapon_stats)
    beam = BeamWeapon(basic_weapon_stats)
    for w in (laser, beam):
        w.powered = True
        w.tick(basic_weapon_stats.charge_time)
        assert w.ready
