"""Save/load round-trip — start a run, save, load into a fresh Game,
verify the run state matches what we wrote out."""

from __future__ import annotations

from pathlib import Path
from random import Random

from ftl.augments.factory import augment_from_def
from ftl.core.game import Game
from ftl.crew.skills import Skill
from ftl.map.generation import generate_star_map
from ftl.persistence.save import list_saves, load_run, save_run
from ftl.ships.ship import PlayerShip


def _fresh_game() -> Game:
    g = Game()
    g.load_content()
    return g


def _seed_run(game: Game, *, scenario_id: str = "pilgrim_path") -> None:
    scenario = game.registry.scenarios[scenario_id]
    game.new_run(seed=42)
    run = game.run
    assert run is not None
    run.scenario_id = scenario_id
    run.sector_chain = ["the_borderlands", "inner_spiral_edge", "concordat_warfront"]
    run.sector_index = 1
    run.sectors_total = 3
    ship_def = game.registry.ships[scenario.player_ship]
    run.player_ship = PlayerShip.from_def(ship_def, game.registry)
    sector_def = game.registry.sectors[run.sector_chain[run.sector_index]]
    run.star_map = generate_star_map(sector_def, Random(7))
    run.current_beacon_id = run.star_map.current_beacon
    run.scrap = 88
    run.fuel = 9
    run.missiles = 3
    run.drone_parts = 1
    run.player_ship.hull.current = run.player_ship.hull.maximum - 4
    run.player_ship.crew[0].skills[Skill.PILOTING] = 35.0
    run.story_flags.add("touched_a_lattice_node")
    aug = augment_from_def(game.registry.augments["riveted_plating"])
    assert aug is not None
    aug.install(run.player_ship)
    run.augments.append(aug)


def test_save_roundtrip(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("ftl.persistence.save.SAVES_DIR", tmp_path)
    game = _fresh_game()
    _seed_run(game)
    original = game.run
    assert original is not None
    path = save_run(original, "test_slot")
    assert path.exists()

    fresh = _fresh_game()
    restored = load_run(path, fresh)
    assert restored is not None
    assert restored.scrap == 88
    assert restored.missiles == 3
    assert restored.sector_index == 1
    assert restored.current_beacon_id == original.current_beacon_id
    assert restored.scenario_id == "pilgrim_path"
    assert restored.player_ship is not None
    assert restored.player_ship.hull.current == original.player_ship.hull.current
    # Pilgrim ship has 3 crew; the first one should retain its skill XP.
    assert restored.player_ship.crew[0].skills[Skill.PILOTING] == 35.0
    # Star map structure preserved.
    assert len(restored.star_map.beacons) == 12  # type: ignore[union-attr]
    # Augment reinstalled (applied its +5 hull max).
    assert any(a.stats.id == "riveted_plating" for a in restored.augments)
    assert "touched_a_lattice_node" in restored.story_flags


def test_list_saves_returns_newest_first(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("ftl.persistence.save.SAVES_DIR", tmp_path)
    game = _fresh_game()
    _seed_run(game)
    assert game.run is not None
    save_run(game.run, "slot_a")
    save_run(game.run, "slot_b")
    slots = list_saves()
    assert {s.name for s in slots} == {"slot_a", "slot_b"}
