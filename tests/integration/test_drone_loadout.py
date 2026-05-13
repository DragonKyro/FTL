"""Defense + combat drone loadout deterministically affects the fight."""

from __future__ import annotations

from random import Random

import pytest

from ftl.combat.combat_state import Outcome
from ftl.data.registry import Registry
from ftl.drones.drone import Drone, DroneStats
from ftl.scenarios.loader import build_combat_from_scenario


def _power_up(engine):  # type: ignore[no-untyped-def]
    player = engine.player
    player.systems["weapons"].set_power(2)
    player.systems["shields"].set_power(2)
    player.systems["engines"].set_power(1)
    player.systems["piloting"].set_power(1)
    player.systems["oxygen"].set_power(1)
    for w in player.weapons:
        w.powered = True
        w.target_room_id = "gun_bay"


@pytest.mark.integration
def test_combat_drone_speeds_up_the_win() -> None:
    DT = 1.0 / 60.0
    reg = Registry()
    reg.load_all()

    # Baseline: no combat drone, default Wayfarer (1 defense drone exists but
    # the enemy has no missiles, so it's irrelevant).
    base_engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(7)
    )
    _power_up(base_engine)
    base_ticks = 0
    while base_engine.outcome is Outcome.FIGHTING and base_ticks < 60 * 240:
        base_engine.tick(DT)
        base_ticks += 1
    assert base_engine.outcome is Outcome.WON

    # With combat drone.
    drone_engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(7)
    )
    drone_engine.player.drones.append(
        Drone(DroneStats(
            id="cd", name="cd", family="combat",
            power_required=2, damage=1, charge_time=5.0,
        ))
    )
    drone_engine.player.systems["drone_control"].set_power(2)
    _power_up(drone_engine)
    drone_ticks = 0
    while drone_engine.outcome is Outcome.FIGHTING and drone_ticks < 60 * 240:
        drone_engine.tick(DT)
        drone_ticks += 1
    assert drone_engine.outcome is Outcome.WON
    # Combat drone fires extra shots; shields absorb some, but the run
    # shouldn't be slower than the no-drone baseline.
    assert drone_ticks <= base_ticks
