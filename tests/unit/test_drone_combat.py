"""Combat drone charges and fires projectiles."""

from __future__ import annotations

from random import Random

from ftl.data.registry import Registry
from ftl.drones.runtime import tick_drones
from ftl.scenarios.loader import build_combat_from_scenario


def _engine_with_combat_drone():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(0)
    )
    # Replace the player's drones with one combat drone.
    from ftl.drones.drone import Drone, DroneStats

    engine.player.drones.clear()
    stats = DroneStats(
        id="cd", name="cd", family="combat", power_required=2, damage=1, charge_time=1.0,
    )
    engine.player.drones.append(Drone(stats))
    # Power drone control.
    dc = engine.player.systems["drone_control"]
    dc.set_power(2)
    return engine


def test_combat_drone_fires_when_powered_and_charged() -> None:
    engine = _engine_with_combat_drone()
    # Tick drones for 2 seconds — should fire at least once (charge_time=1.0).
    for _ in range(60 * 2):
        tick_drones(engine.player, engine.enemy, engine, 1.0 / 60.0)
    assert any(p.weapon_family == "laser" for p in engine.projectiles)


def test_unpowered_combat_drone_does_not_fire() -> None:
    engine = _engine_with_combat_drone()
    engine.player.systems["drone_control"].set_power(0)
    for _ in range(60 * 2):
        tick_drones(engine.player, engine.enemy, engine, 1.0 / 60.0)
    assert not engine.projectiles
