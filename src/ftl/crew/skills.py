"""Crew skill enum + leveling rules."""

from __future__ import annotations

from enum import Enum


class Skill(str, Enum):
    PILOTING = "piloting"
    ENGINES = "engines"
    SHIELDS = "shields"
    WEAPONS = "weapons"
    REPAIR = "repair"
    COMBAT = "combat"


# Per-skill experience thresholds for promotion to the next level.
SKILL_THRESHOLDS: tuple[int, ...] = (15, 55, 95)
