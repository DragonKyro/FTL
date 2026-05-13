"""Loam — fungal collective; regenerates HP slowly anywhere.

Phase 4 trait: passive +0.25 HP/sec regen while alive, regardless of
room. No medbay needed. Caps at max_hp.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.crew.species import SpeciesBehavior

if TYPE_CHECKING:
    from ftl.crew.crew import Crew


REGEN_PER_SEC: float = 0.25


class LoamBehavior(SpeciesBehavior):
    def on_tick(self, crew: Crew, dt: float) -> None:
        if not crew.alive:
            return
        if crew.hp < crew.max_hp:
            crew.hp = min(float(crew.max_hp), crew.hp + REGEN_PER_SEC * dt)
