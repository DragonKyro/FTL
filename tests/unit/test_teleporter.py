"""Teleporter system: cooldown, send_boarders, recall_boarders."""

from __future__ import annotations

from random import Random

from ftl.combat.combat_state import Outcome
from ftl.data.registry import Registry
from ftl.scenarios.loader import build_combat_from_scenario


def _engine():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(0)
    )
    tele = engine.player.teleporter
    assert tele is not None
    tele.set_power(1)
    return engine


def test_teleporter_starts_ready() -> None:
    engine = _engine()
    assert engine.player.teleporter is not None
    assert engine.player.teleporter.is_ready


def test_send_boarders_moves_crew_to_enemy_ship() -> None:
    engine = _engine()
    # Put a crew on the teleporter pad.
    pad_room = next(
        r for r in engine.player.rooms.values() if r.system is engine.player.teleporter
    )
    pad_tile = pad_room.tiles[0]
    boarder = engine.player.crew[0]
    boarder.current_tile = pad_tile
    target_room = engine.enemy.rooms["gun_bay"]
    starting_player_count = len(engine.player.crew)
    starting_enemy_count = len(engine.enemy.crew)
    success = engine.send_boarders([boarder], target_room)
    assert success
    assert len(engine.player.crew) == starting_player_count - 1
    assert len(engine.enemy.crew) == starting_enemy_count + 1
    assert boarder.current_ship is engine.enemy
    assert boarder.current_tile in target_room.tiles


def test_send_starts_cooldown() -> None:
    engine = _engine()
    pad_room = next(
        r for r in engine.player.rooms.values() if r.system is engine.player.teleporter
    )
    boarder = engine.player.crew[0]
    boarder.current_tile = pad_room.tiles[0]
    target_room = engine.enemy.rooms["bridge"]
    engine.send_boarders([boarder], target_room)
    assert engine.player.teleporter is not None
    assert engine.player.teleporter.cooldown_remaining > 0
    assert not engine.player.teleporter.is_ready


def test_recall_brings_boarders_back() -> None:
    engine = _engine()
    pad_room = next(
        r for r in engine.player.rooms.values() if r.system is engine.player.teleporter
    )
    boarder = engine.player.crew[0]
    boarder.current_tile = pad_room.tiles[0]
    target_room = engine.enemy.rooms["bridge"]
    engine.send_boarders([boarder], target_room)
    # Cooldown elapses.
    assert engine.player.teleporter is not None
    engine.player.teleporter.cooldown_remaining = 0
    success = engine.recall_boarders()
    assert success
    assert boarder.current_ship is engine.player
    assert boarder.current_tile in pad_room.tiles


def test_send_fails_when_cooldown_active() -> None:
    engine = _engine()
    assert engine.player.teleporter is not None
    engine.player.teleporter.cooldown_remaining = 10.0
    pad_room = next(
        r for r in engine.player.rooms.values() if r.system is engine.player.teleporter
    )
    boarder = engine.player.crew[0]
    boarder.current_tile = pad_room.tiles[0]
    target_room = engine.enemy.rooms["bridge"]
    success = engine.send_boarders([boarder], target_room)
    assert not success
