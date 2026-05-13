"""Crew-vs-crew melee resolution.

Opposing crew (different `home_ship`) sharing a tile damage each other
each tick. Mhirsa hit harder via `SpeciesBehavior.melee_damage`. When a
crew member's HP drops to 0, they switch to `CrewState.DEAD`; the
engine sweeps them out of the ship's crew list at the end of the tick.

Locked-in-melee crew can't move, can't man, can't heal, can't repair —
the movement module respects `CrewState.FIGHTING` as a hard override.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from ftl.crew.crew import CrewState

if TYPE_CHECKING:
    from ftl.crew.crew import Crew
    from ftl.ships.ship import Ship


MELEE_BASE_DAMAGE_PER_SEC: float = 6.0


def tick_crew_combat(ship: Ship, dt: float) -> None:
    if not ship.crew:
        return
    # Bucket crew by tile.
    by_tile: dict[tuple[int, int], list[Crew]] = defaultdict(list)
    for crew in ship.crew:
        if not crew.alive or crew.current_tile is None:
            continue
        by_tile[(crew.current_tile.x, crew.current_tile.y)].append(crew)

    for tile_crew in by_tile.values():
        teams_on_tile = {c.team for c in tile_crew}
        if len(teams_on_tile) <= 1:
            # Clear FIGHTING state for crew that were fighting but are now
            # in a single-team tile.
            for c in tile_crew:
                if c.state is CrewState.FIGHTING:
                    c.state = CrewState.IDLE
            continue
        _resolve_melee_on_tile(tile_crew, dt)


def _resolve_melee_on_tile(tile_crew: list[Crew], dt: float) -> None:
    # Snapshot HP-at-start so two simultaneous attackers each deal damage
    # to a defender that's still alive at this tick start.
    alive_at_start = [c for c in tile_crew if c.alive]
    if len(alive_at_start) < 2:
        return
    for attacker in alive_at_start:
        if not attacker.alive:
            continue
        attacker.state = CrewState.FIGHTING
        attacker.path = []
        attacker.move_progress = 0.0
        targets = [c for c in alive_at_start if c.team != attacker.team and c.alive]
        if not targets:
            continue
        # All-vs-all sum split — each defender takes a share so two
        # boarders attacking one defender deal full damage each (FTL canon).
        for defender in targets:
            base = attacker.species.combat_damage * MELEE_BASE_DAMAGE_PER_SEC * dt
            # Augment-level ship melee bonus (Bonebreaker Drills).
            ship_mult = getattr(
                getattr(attacker, "current_ship", None),
                "melee_damage_mult",
                1.0,
            )
            scaled = attacker.behavior.melee_damage(attacker, base) * ship_mult
            defender.hp = max(0.0, defender.hp - scaled)
            attacker.behavior.on_combat_damage_dealt(attacker, defender, scaled)
            if defender.hp <= 0:
                defender.state = CrewState.DEAD
                from ftl.crew.xp import award_combat_xp

                award_combat_xp(attacker)
