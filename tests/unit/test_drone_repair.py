"""Hull repair drone passively repairs hull."""

from __future__ import annotations

from random import Random

from ftl.data.registry import Registry
from ftl.drones.drone import Drone, DroneStats
from ftl.drones.runtime import HULL_REPAIR_INTERVAL_SECONDS, tick_drones
from ftl.scenarios.loader import build_combat_from_scenario


def _engine_with_repair_drone():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(0)
    )
    engine.player.drones.clear()
    engine.player.drones.append(
        Drone(DroneStats(id="r", name="r", family="repair", power_required=2))
    )
    engine.player.systems["drone_control"].set_power(2)
    engine.player.hull.damage(5)
    return engine


def test_hull_repair_drone_restores_hull_over_time() -> None:
    engine = _engine_with_repair_drone()
    starting_hull = engine.player.hull.current
    for _ in range(60 * int(HULL_REPAIR_INTERVAL_SECONDS * 2)):
        tick_drones(engine.player, engine.enemy, engine, 1.0 / 60.0)
    assert engine.player.hull.current > starting_hull


def test_full_hull_no_op() -> None:
    engine = _engine_with_repair_drone()
    engine.player.hull.current = engine.player.hull.maximum
    for _ in range(60 * int(HULL_REPAIR_INTERVAL_SECONDS * 2)):
        tick_drones(engine.player, engine.enemy, engine, 1.0 / 60.0)
    assert engine.player.hull.current == engine.player.hull.maximum
