"""Scenario loader: First Encounter builds the expected ships + weapons + AI."""

from __future__ import annotations

from random import Random

from ftl.data.registry import Registry
from ftl.scenarios.loader import build_combat_from_scenario


def _registry() -> Registry:
    reg = Registry()
    reg.load_all()
    return reg


def test_first_encounter_builds_two_ships():
    reg = _registry()
    scenario = reg.scenarios["first_encounter"]
    engine = build_combat_from_scenario(scenario, reg, Random(0))
    assert engine.player.name == "Wayfarer"
    assert engine.enemy.name == "Black Vein Skiff"
    assert engine.player.hull.maximum == 18
    assert engine.enemy.hull.maximum == 12


def test_first_encounter_loads_player_loadout():
    reg = _registry()
    scenario = reg.scenarios["first_encounter"]
    engine = build_combat_from_scenario(scenario, reg, Random(0))
    weapon_ids = {w.stats.id for w in engine.player.weapons}
    assert weapon_ids == {"pulse_lance_mk1", "splinter_missile_mk1"}


def test_first_encounter_loads_enemy_loadout():
    reg = _registry()
    scenario = reg.scenarios["first_encounter"]
    engine = build_combat_from_scenario(scenario, reg, Random(0))
    weapon_ids = {w.stats.id for w in engine.enemy.weapons}
    assert weapon_ids == {"pulse_lance_mk1"}


def test_first_encounter_player_has_engines():
    reg = _registry()
    scenario = reg.scenarios["first_encounter"]
    engine = build_combat_from_scenario(scenario, reg, Random(0))
    assert engine.player.engines is not None
    assert engine.enemy.engines is None


def test_first_encounter_player_starts_with_missiles():
    reg = _registry()
    scenario = reg.scenarios["first_encounter"]
    engine = build_combat_from_scenario(scenario, reg, Random(0))
    assert engine.state.player_inventory.missiles == 8


def test_first_encounter_enemy_ai_powered_weapon():
    reg = _registry()
    scenario = reg.scenarios["first_encounter"]
    engine = build_combat_from_scenario(scenario, reg, Random(0))
    assert engine.enemy.weapons[0].powered is True
