"""End-to-end combat flow under a fixed RNG seed.

A real CombatEngine ticked at simulation rate must:
  - resolve to Outcome.WON when the player plays well
  - resolve to Outcome.LOST when the player ignores their systems
  - resolve to Outcome.FLED after 15 simulated seconds of charging

These tests are integration-marked but kept fast enough to run on every
pytest invocation (each fight resolves within ~10000 ticks at most).
"""

from __future__ import annotations

from random import Random
from typing import TYPE_CHECKING

import pytest

from ftl.combat.combat_state import Outcome
from ftl.data.registry import Registry
from ftl.scenarios.loader import build_combat_from_scenario

if TYPE_CHECKING:
    from ftl.combat.engine import CombatEngine

DT: float = 1.0 / 60.0
MAX_TICKS: int = 60 * 240  # 4 simulated minutes


def _engine_for_first_encounter(seed: int) -> "CombatEngine":
    reg = Registry()
    reg.load_all()
    scenario = reg.scenarios["first_encounter"]
    return build_combat_from_scenario(scenario, reg, Random(seed))


def _power_up_player(engine: "CombatEngine") -> None:
    player = engine.player
    player.systems["weapons"].set_power(2)
    player.systems["shields"].set_power(2)
    player.systems["engines"].set_power(1)
    player.systems["piloting"].set_power(1)
    for weapon in player.weapons:
        weapon.powered = True
        weapon.target_room_id = "gun_bay"


def _run_until_outcome(
    engine: "CombatEngine", max_ticks: int = MAX_TICKS
) -> int:
    ticks = 0
    while engine.outcome is Outcome.FIGHTING and ticks < max_ticks:
        engine.tick(DT)
        ticks += 1
    return ticks


@pytest.mark.integration
def test_armed_player_wins_first_encounter():
    engine = _engine_for_first_encounter(seed=1)
    _power_up_player(engine)
    ticks = _run_until_outcome(engine)
    assert engine.outcome is Outcome.WON, (
        f"expected WON, got {engine.outcome.value} after {ticks} ticks"
    )
    assert engine.enemy.hull.destroyed
    assert engine.player.hull.current > 0


@pytest.mark.integration
def test_passive_player_loses_first_encounter():
    engine = _engine_for_first_encounter(seed=2)
    # Player does nothing — no power, no targeting.
    ticks = _run_until_outcome(engine)
    assert engine.outcome is Outcome.LOST, (
        f"expected LOST, got {engine.outcome.value} after {ticks} ticks"
    )
    assert engine.player.hull.destroyed


@pytest.mark.integration
def test_flee_charge_resolves_after_15_seconds():
    engine = _engine_for_first_encounter(seed=3)
    # Give player shields so they survive the 15-second charge.
    engine.player.systems["shields"].set_power(2)
    engine.player.systems["piloting"].set_power(1)
    engine.player.systems["engines"].set_power(1)
    engine.begin_flee()
    ticks = _run_until_outcome(engine, max_ticks=60 * 30)
    assert engine.outcome is Outcome.FLED, (
        f"expected FLED, got {engine.outcome.value} after {ticks} ticks"
    )
    # Should resolve close to 15 seconds (60 * 15 = 900 ticks). Allow slack.
    assert 880 <= ticks <= 920


@pytest.mark.integration
def test_outcome_is_sticky_once_set():
    engine = _engine_for_first_encounter(seed=4)
    _power_up_player(engine)
    _run_until_outcome(engine)
    initial_outcome = engine.outcome
    for _ in range(60):
        engine.tick(DT)
    assert engine.outcome is initial_outcome
