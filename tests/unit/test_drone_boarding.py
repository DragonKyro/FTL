"""Boarding drone deploys a synthetic-species Crew on the enemy ship."""

from __future__ import annotations

from random import Random

from ftl.data.registry import Registry
from ftl.drones.drone import Drone, DroneStats
from ftl.scenarios.loader import build_combat_from_scenario


def _engine_with_boarding_drone():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(0)
    )
    engine.player.drones.append(
        Drone(DroneStats(id="bd", name="bd", family="boarding", power_required=3))
    )
    engine.player.systems["drone_control"].set_power(3)
    engine.state.player_inventory.drone_parts = 5
    return engine


def test_deploy_boarding_drone_creates_synthetic_crew_on_enemy() -> None:
    engine = _engine_with_boarding_drone()
    target = engine.enemy.rooms["gun_bay"]
    starting_enemy_crew = len(engine.enemy.crew)
    ok = engine.try_deploy_boarding_drone(target)
    assert ok
    assert len(engine.enemy.crew) == starting_enemy_crew + 1
    new_crew = engine.enemy.crew[-1]
    assert new_crew.species.id == "synthetic"
    assert new_crew.home_ship is engine.player
    assert new_crew.current_ship is engine.enemy


def test_consumes_drone_parts() -> None:
    engine = _engine_with_boarding_drone()
    target = engine.enemy.rooms["gun_bay"]
    starting_parts = engine.state.player_inventory.drone_parts
    engine.try_deploy_boarding_drone(target)
    assert engine.state.player_inventory.drone_parts == starting_parts - 1


def test_fails_without_drone_parts() -> None:
    engine = _engine_with_boarding_drone()
    engine.state.player_inventory.drone_parts = 0
    target = engine.enemy.rooms["gun_bay"]
    assert not engine.try_deploy_boarding_drone(target)
