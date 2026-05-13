"""Event runtime: choices resolve to outcomes, outcomes apply to runs."""

from __future__ import annotations

from ftl.core.game import Game
from ftl.events.choice import Choice
from ftl.events.event import Event
from ftl.events.outcome import Outcome


def test_event_resolve_returns_matching_outcome():
    outcome = Outcome(id="reward", scrap=25)
    event = Event(
        id="windfall",
        text="A friendly trader hails you...",
        choices=[Choice(text="Accept", outcome_id="reward")],
        outcomes={"reward": outcome},
    )

    resolved = event.resolve(0)
    assert resolved is outcome


def test_event_resolve_out_of_range_returns_none():
    event = Event(id="x", text="x")
    assert event.resolve(0) is None
    assert event.resolve(-1) is None


def test_outcome_applies_resource_changes():
    game = Game(seed=42)
    run = game.new_run()
    starting_scrap = run.scrap

    Outcome(id="r", scrap=25, fuel=2).apply(run)

    assert run.scrap == starting_scrap + 25
    assert run.fuel == 18  # default 16 + 2


def test_outcome_sets_flags():
    game = Game(seed=42)
    run = game.new_run()
    Outcome(id="r", set_flags=["met_explorer"]).apply(run)
    assert "met_explorer" in run.story_flags
