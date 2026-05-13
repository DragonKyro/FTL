"""Event outcome runtime.

Applies a YAML-defined `OutcomeDef` to the active `Run`. Mutates
resources, hull, flags. If the outcome `starts_combat`, the scene
controller transitions into a Combat scene instead of returning to
the star map.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.core.game import Run
    from ftl.data.schemas import OutcomeDef


def apply_outcome(run: Run, outcome: OutcomeDef) -> None:
    """Mutate run state per the outcome. Combat triggers are handled by
    the scene flow controller after this returns."""
    run.scrap = max(0, run.scrap + outcome.scrap)
    run.fuel = max(0, run.fuel + outcome.fuel)
    run.missiles = max(0, run.missiles + outcome.missiles)
    run.drone_parts = max(0, run.drone_parts + outcome.drone_parts)
    if outcome.hull_damage > 0 and run.player_ship is not None:
        run.player_ship.hull.damage(outcome.hull_damage)
    if outcome.hull_repair > 0 and run.player_ship is not None:
        run.player_ship.hull.repair(outcome.hull_repair)
    for flag in outcome.set_flags:
        run.story_flags.add(flag)
    for flag in outcome.clear_flags:
        run.story_flags.discard(flag)
