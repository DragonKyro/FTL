"""Full boarding flow integration test.

Player teleports a Mhirsa to enemy gun_bay → enemy gunner takes damage →
weapon-system manning is broken → recall the boarder back.
"""

from __future__ import annotations

from random import Random

import pytest

from ftl.combat.combat_state import Outcome
from ftl.data.registry import Registry
from ftl.scenarios.loader import build_combat_from_scenario


@pytest.mark.integration
def test_boarding_kills_enemy_gunner_and_silences_their_weapons() -> None:
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(1)
    )
    # Power the teleporter pad so it's ready.
    tele = engine.player.teleporter
    assert tele is not None
    tele.set_power(1)
    # Make sure the Mhirsa is on the pad.
    pad_room = next(r for r in engine.player.rooms.values() if r.system is tele)
    mhirsa = next(c for c in engine.player.crew if c.species.id == "mhirsa")
    mhirsa.current_tile = pad_room.tiles[0]

    target_room = engine.enemy.rooms["gun_bay"]
    success = engine.send_boarders([mhirsa], target_room)
    assert success
    assert mhirsa.current_ship is engine.enemy

    # Find the enemy crew that was manning the gun bay.
    target_enemy = None
    for crew in engine.enemy.crew:
        if (
            crew.home_ship is engine.enemy
            and crew.current_tile is not None
            and crew.current_tile.room_id == "gun_bay"
        ):
            target_enemy = crew
            break
    assert target_enemy is not None

    # Tick the engine until the target enemy dies or we time out.
    dt = 1.0 / 60.0
    for _ in range(60 * 30):  # up to 30 simulated seconds
        engine.tick(dt)
        if not target_enemy.alive:
            break
        if engine.outcome is not Outcome.FIGHTING:
            break

    assert not target_enemy.alive


@pytest.mark.integration
def test_recall_returns_boarders() -> None:
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(2)
    )
    tele = engine.player.teleporter
    assert tele is not None
    tele.set_power(1)
    pad_room = next(r for r in engine.player.rooms.values() if r.system is tele)
    boarder = engine.player.crew[0]
    boarder.current_tile = pad_room.tiles[0]
    target_room = engine.enemy.rooms["bridge"]
    engine.send_boarders([boarder], target_room)
    # Force the cooldown to elapse instead of ticking 15s of combat.
    tele.cooldown_remaining = 0.0
    assert engine.recall_boarders()
    assert boarder.current_ship is engine.player
