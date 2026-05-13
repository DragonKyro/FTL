"""Halene — passive +1 reactor power while alive in an oxygenated room.

The Halene biology converts ambient particles into electrical potential.
Mechanically: every tick we add 1 to the home ship's `crew_power_bonus`
if the Halene is alive and in a room with oxygen > 0.1. The bonus is
zeroed at the start of each ship tick, so we only have to re-add it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.crew.species import SpeciesBehavior

if TYPE_CHECKING:
    from ftl.crew.crew import Crew


class HaleneBehavior(SpeciesBehavior):
    def on_tick(self, crew: Crew, dt: float) -> None:
        if not crew.alive:
            return
        if crew.home_ship is None or crew.current_ship is not crew.home_ship:
            # Halene contributes only while on their own ship.
            return
        room = crew.current_room()
        if room is None or room.oxygen < 0.1:
            return
        crew.home_ship.crew_power_bonus += 1
