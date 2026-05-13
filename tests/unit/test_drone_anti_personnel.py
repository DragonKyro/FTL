"""Anti-personnel drone deploys on the player's teleporter pad."""

from __future__ import annotations

from random import Random

from ftl.data.registry import Registry
from ftl.drones.drone import Drone, DroneStats
from ftl.scenarios.loader import build_combat_from_scenario


def _engine_with_ap_drone():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    engine = build_combat_from_scenario(
        reg.scenarios["first_encounter"], reg, Random(0)
    )
    engine.player.drones.append(
        Drone(DroneStats(id="ap", name="ap", family="anti_personnel", power_required=2))
    )
    engine.player.systems["drone_control"].set_power(2)
    engine.state.player_inventory.drone_parts = 3
    return engine


def test_ap_drone_deploys_on_own_ship() -> None:
    engine = _engine_with_ap_drone()
    starting_crew = len(engine.player.crew)
    ok = engine.try_deploy_ap_drone()
    assert ok
    assert len(engine.player.crew) == starting_crew + 1
    new_crew = engine.player.crew[-1]
    assert new_crew.species.id == "synthetic"
    assert new_crew.current_ship is engine.player
    assert new_crew.home_ship is engine.player
