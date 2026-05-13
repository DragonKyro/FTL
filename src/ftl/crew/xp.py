"""Crew skill XP accrual + level-up.

Per FTL canon, crew earn XP while actively doing their job:
- Manning piloting → +XP/sec
- Manning engines → +XP/sec
- Manning shields → +XP per absorbed hit
- Manning weapons → +XP per shot fired
- Repairing → +XP per damage bar repaired
- Crew combat → +XP per kill

Thresholds are imported from `crew.skills` (`SKILL_THRESHOLDS`). The
manning *bonus multiplier* climbs from 1.0× (level 0) to 2.0× (level 3).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.crew.skills import SKILL_THRESHOLDS, Skill

if TYPE_CHECKING:
    from ftl.crew.crew import Crew


# Per-second accrual for "passively manning" XP.
MANNING_XP_PER_SEC: float = 0.5
# Per-event accrual for discrete XP gains.
WEAPON_XP_PER_SHOT: int = 1
SHIELD_XP_PER_HIT: int = 1
REPAIR_XP_PER_BAR: int = 1
COMBAT_XP_PER_KILL: int = 5

_SKILL_FROM_SYSTEM: dict[str, Skill] = {
    "piloting": Skill.PILOTING,
    "engines": Skill.ENGINES,
    "shields": Skill.SHIELDS,
    "weapons": Skill.WEAPONS,
}


def skill_for_system(system_name: str) -> Skill | None:
    return _SKILL_FROM_SYSTEM.get(system_name)


def add_xp(crew: Crew, skill: Skill, amount: float) -> None:
    if amount <= 0 or not crew.alive:
        return
    current = crew.skills.get(skill, 0.0)
    crew.skills[skill] = current + amount


def xp_int(crew: Crew, skill: Skill) -> int:
    return int(crew.skills.get(skill, 0.0))


def level_for(xp: float | int) -> int:
    """Convert an XP value to a discrete level (0..len(thresholds))."""
    lvl = 0
    for threshold in SKILL_THRESHOLDS:
        if xp >= threshold:
            lvl += 1
        else:
            break
    return lvl


def manning_bonus_multiplier(crew: Crew, system_name: str) -> float:
    """1.0× at skill level 0, climbing by 0.33× per level (max 2.0× at level 3)."""
    skill = skill_for_system(system_name)
    if skill is None:
        return 1.0
    level = level_for(crew.skills.get(skill, 0))
    return 1.0 + 0.33 * level


def award_manning_xp(crew: Crew, system_name: str, dt: float) -> None:
    skill = skill_for_system(system_name)
    if skill is None:
        return
    add_xp(crew, skill, MANNING_XP_PER_SEC * dt)


def award_weapon_xp(crew: Crew | None) -> None:
    if crew is None:
        return
    add_xp(crew, Skill.WEAPONS, WEAPON_XP_PER_SHOT)


def award_shield_xp(crew: Crew | None) -> None:
    if crew is None:
        return
    add_xp(crew, Skill.SHIELDS, SHIELD_XP_PER_HIT)


def award_repair_xp(crew: Crew, bars: int = 1) -> None:
    add_xp(crew, Skill.REPAIR, REPAIR_XP_PER_BAR * bars)


def award_combat_xp(crew: Crew) -> None:
    add_xp(crew, Skill.COMBAT, COMBAT_XP_PER_KILL)
