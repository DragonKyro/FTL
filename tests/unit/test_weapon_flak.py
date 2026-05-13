"""Flak weapon: fires multiple projectiles per shot."""

from __future__ import annotations

from random import Random

from ftl.data.registry import Registry
from ftl.scenarios.loader import build_combat_from_scenario


def test_flak_spawns_three_projectiles_per_fire() -> None:
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(0)
    )
    from ftl.weapons.flak import FlakWeapon
    from ftl.weapons.weapon import WeaponStats

    engine.player.weapons.clear()
    stats = WeaponStats(
        id="f", name="Flak", family="flak",
        damage=1, projectile_count=3,
        charge_time=2.0, power_required=2,
    )
    weapon = FlakWeapon(stats)
    weapon.powered = True
    weapon.charge_progress = stats.charge_time
    weapon.target_room_id = "gun_bay"
    engine.player.weapons.append(weapon)
    engine.player.systems["weapons"].set_power(2)

    before = len(engine.projectiles)
    engine._try_fire_weapons(engine.player, engine.enemy, engine.state.player_inventory)
    assert len(engine.projectiles) == before + 3
