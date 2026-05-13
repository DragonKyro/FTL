"""Scenario loader.

Turns a `ScenarioDef` (loaded from `content/scenarios/`) into a wired
`CombatEngine` ready to register with the simulation. The loader is the
sole place that knows how to:

- pull the player + enemy `ShipDef` from the registry
- build both ships via `Ship.from_def`
- instantiate the right AI profile
- seed the CombatState with the right starting missile counts
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.ai.enemy_pilot import EnemyPilot
from ftl.combat.combat_state import CombatState
from ftl.combat.engine import CombatEngine
from ftl.ships.ship import EnemyShip, PlayerShip

if TYPE_CHECKING:
    from random import Random

    from ftl.core.event_bus import EventBus
    from ftl.data.registry import Registry
    from ftl.data.schemas import ScenarioDef


def build_combat_from_scenario(
    scenario: ScenarioDef,
    registry: Registry,
    rng: Random,
    event_bus: EventBus | None = None,
) -> CombatEngine:
    """Construct a ready-to-tick `CombatEngine` for the given scenario."""
    player_def = registry.ships[scenario.player_ship]
    enemy_def = registry.ships[scenario.enemy_ship]

    player = PlayerShip.from_def(player_def, registry)
    enemy = EnemyShip.from_def(enemy_def, registry)

    player_missiles = (
        scenario.player_missiles
        if scenario.player_missiles is not None
        else player_def.starting_missiles
    )
    enemy_missiles = (
        scenario.enemy_missiles
        if scenario.enemy_missiles is not None
        else enemy_def.starting_missiles
    )

    state = CombatState(
        player=player,
        enemy=enemy,
        player_missiles=player_missiles,
        enemy_missiles=enemy_missiles,
    )

    ai = EnemyPilot(enemy, player, rng)

    return CombatEngine(state=state, ai=ai, rng=rng, event_bus=event_bus)
