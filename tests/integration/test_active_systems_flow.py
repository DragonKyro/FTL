"""Active-system flow: cloak freezes enemy weapons, battery surges
reactor, mind-control flips an enemy crew, hacking disables + damages."""

from __future__ import annotations

from random import Random

import pytest

from ftl.combat.combat_state import Outcome
from ftl.data.registry import Registry
from ftl.scenarios.loader import build_combat_from_scenario


def _setup():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(11)
    )
    # Power everything Phase 3 brings to bear.
    p = engine.player
    p.systems["weapons"].set_power(2)
    p.systems["shields"].set_power(2)
    p.systems["engines"].set_power(2)
    p.systems["piloting"].set_power(1)
    p.systems["oxygen"].set_power(1)
    p.systems["cloaking"].set_power(1)
    p.systems["battery"].set_power(1)
    p.systems["mind_control"].set_power(1)
    p.systems["hacking"].set_power(1)
    return engine


@pytest.mark.integration
def test_cloak_freezes_enemy_weapon_charge() -> None:
    engine = _setup()
    enemy_weapon = engine.enemy.weapons[0]
    enemy_weapon.powered = True
    # Tick a bit to build some charge.
    for _ in range(60 * 3):
        engine.tick(1.0 / 60.0)
    pre_cloak_charge = enemy_weapon.charge_progress
    # Activate cloak.
    assert engine.activate_cloak()
    for _ in range(60 * 4):  # 4 seconds of cloak (< 5s active duration)
        engine.tick(1.0 / 60.0)
    # Enemy weapon shouldn't have advanced (cloak freezes their charge).
    assert enemy_weapon.charge_progress <= pre_cloak_charge + 0.05


@pytest.mark.integration
def test_battery_grants_temporary_reactor_power() -> None:
    engine = _setup()
    base = engine.player.base_max_reactor_power + engine.player.crew_power_bonus
    assert engine.activate_battery()
    # Tick once to apply.
    engine.tick(1.0 / 60.0)
    assert engine.player.max_reactor_power >= base + 2


@pytest.mark.integration
def test_mind_control_flips_enemy_crew_team() -> None:
    engine = _setup()
    target = next(c for c in engine.enemy.crew if c.team == "enemy")
    assert engine.try_mind_control(target)
    assert target.team == "player"


@pytest.mark.integration
def test_hacking_drone_lands_and_activates() -> None:
    engine = _setup()
    target_system = engine.enemy.systems["weapons"]
    # Launch.
    assert engine.try_hack(target_system, engine.enemy)
    # Wait for arrival (~2s + a hair).
    for _ in range(60 * 3):
        engine.tick(1.0 / 60.0)
    hack = engine.player.systems["hacking"]
    assert hack.is_latched
    # Activate.
    assert engine.try_hack(target_system, engine.enemy)
    assert hack.is_active
    assert target_system.hacked
