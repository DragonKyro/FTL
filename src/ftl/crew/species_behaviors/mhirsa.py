"""Mhirsa — engineered worker-soldiers. +50% melee damage, +20% move speed."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.crew.species import SpeciesBehavior

if TYPE_CHECKING:
    from ftl.crew.crew import Crew


class MhirsaBehavior(SpeciesBehavior):
    def melee_damage(self, attacker: Crew, base: float) -> float:
        return base * 1.5

    def move_speed_multiplier(self, crew: Crew) -> float:
        return 1.2
