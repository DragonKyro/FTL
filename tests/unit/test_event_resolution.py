"""Event outcome application — mutates run state correctly."""

from __future__ import annotations

from ftl.core.game import Game
from ftl.data.schemas import OutcomeDef
from ftl.events.runtime import apply_outcome


def _game_with_run():  # type: ignore[no-untyped-def]
    game = Game()
    game.load_content()
    run = game.new_run(seed=1)
    return game, run


def test_outcome_grants_scrap_and_fuel() -> None:
    _game, run = _game_with_run()
    start_scrap = run.scrap
    start_fuel = run.fuel
    outcome = OutcomeDef(scrap=25, fuel=2)
    apply_outcome(run, outcome)
    assert run.scrap == start_scrap + 25
    assert run.fuel == start_fuel + 2


def test_outcome_sets_and_clears_flags() -> None:
    _game, run = _game_with_run()
    run.story_flags.add("preexisting")
    outcome = OutcomeDef(
        set_flags=["new_flag"], clear_flags=["preexisting"],
    )
    apply_outcome(run, outcome)
    assert "new_flag" in run.story_flags
    assert "preexisting" not in run.story_flags


def test_negative_scrap_clamped_at_zero() -> None:
    _game, run = _game_with_run()
    run.scrap = 5
    apply_outcome(run, OutcomeDef(scrap=-20))
    assert run.scrap == 0


def test_authored_event_loads_with_outcomes() -> None:
    """Every authored event YAML should parse with outcomes intact."""
    game, _run = _game_with_run()
    event = game.registry.events.get("asteroid_fold")
    assert event is not None
    assert "thread" in event.outcomes
    assert "burn_around" in event.outcomes
    assert event.outcomes["thread"].hull_damage == 2
