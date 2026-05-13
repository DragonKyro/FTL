"""Full-run flow plumbing — no Arcade window, just engine-level dispatch."""

from __future__ import annotations

from random import Random

import pytest

from ftl.combat.combat_state import Outcome
from ftl.core.game import Game
from ftl.events.runtime import apply_outcome
from ftl.map.encounter_kind import EncounterKind
from ftl.map.generation import generate_star_map


def _game():  # type: ignore[no-untyped-def]
    g = Game()
    g.load_content()
    return g


@pytest.mark.integration
def test_three_sectors_generate_cleanly() -> None:
    game = _game()
    for sector_id in ("the_borderlands", "inner_spiral_edge", "concordat_warfront"):
        sector = game.registry.sectors[sector_id]
        m = generate_star_map(sector, Random(7))
        assert len(m.beacons) == 12
        assert m.current_beacon in m.beacons
        assert m.exit_beacon in m.beacons


@pytest.mark.integration
def test_run_starts_at_first_sector_start_beacon() -> None:
    game = _game()
    run = game.new_run(seed=1)
    sector = game.registry.sectors["the_borderlands"]
    run.star_map = generate_star_map(sector, run.rng.stream("test"))
    run.current_beacon_id = run.star_map.current_beacon
    current = run.star_map.beacons[run.current_beacon_id]
    assert current.visited
    assert current.encounter_id == EncounterKind.EMPTY.value


@pytest.mark.integration
def test_outcome_flag_propagates_to_run() -> None:
    from ftl.data.schemas import OutcomeDef

    game = _game()
    run = game.new_run(seed=2)
    outcome = OutcomeDef(scrap=10, set_flags=["touched_a_lattice_node"])
    apply_outcome(run, outcome)
    assert run.scrap == 30 + 10  # default 30 + 10
    assert "touched_a_lattice_node" in run.story_flags


@pytest.mark.integration
def test_final_boss_ship_exists() -> None:
    game = _game()
    assert "throne_of_ash" in game.registry.ships
    boss_def = game.registry.ships["throne_of_ash"]
    assert boss_def.max_hull >= 25
    assert "helix_cutter_mk1" in boss_def.starting_weapons


@pytest.mark.integration
def test_combat_after_outcome_starts_combat_flag() -> None:
    """Outcomes that flip `starts_combat` route through the engine."""
    game = _game()
    ambush = game.registry.events.get("black_vein_ambush")
    assert ambush is not None
    # The ambush has a single choice → "fight" outcome.
    fight_outcome = ambush.outcomes["fight"]
    assert fight_outcome.starts_combat is True
    assert fight_outcome.enemy_ship_id == "vein_skiff"
