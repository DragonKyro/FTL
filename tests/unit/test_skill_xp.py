"""Crew skill XP accrual + level-up + manning bonus scaling."""

from __future__ import annotations

from ftl.crew.crew import Crew
from ftl.crew.skills import Skill
from ftl.crew.species import Species
from ftl.crew.species_behaviors import SapienBehavior
from ftl.crew.xp import (
    award_combat_xp,
    award_manning_xp,
    award_repair_xp,
    award_shield_xp,
    award_weapon_xp,
    level_for,
    manning_bonus_multiplier,
)


def _sapien() -> Crew:
    return Crew(
        name="S", species=Species(id="sapien", name="Sapien"),
        behavior=SapienBehavior(),
    )


def test_manning_xp_accumulates() -> None:
    c = _sapien()
    for _ in range(60):  # 1s of ticks at 60Hz
        award_manning_xp(c, "piloting", 1.0 / 60.0)
    assert c.skills[Skill.PILOTING] > 0


def test_weapon_fire_xp_increments() -> None:
    c = _sapien()
    award_weapon_xp(c)
    award_weapon_xp(c)
    assert c.skills[Skill.WEAPONS] == 2


def test_shield_absorb_xp_increments() -> None:
    c = _sapien()
    award_shield_xp(c)
    assert c.skills[Skill.SHIELDS] == 1


def test_repair_xp_per_bar() -> None:
    c = _sapien()
    award_repair_xp(c, bars=3)
    assert c.skills[Skill.REPAIR] == 3


def test_combat_xp_per_kill() -> None:
    c = _sapien()
    award_combat_xp(c)
    assert c.skills[Skill.COMBAT] == 5


def test_levels_progress_at_thresholds() -> None:
    assert level_for(0) == 0
    assert level_for(14) == 0
    assert level_for(15) == 1
    assert level_for(54) == 1
    assert level_for(55) == 2
    assert level_for(94) == 2
    assert level_for(95) == 3


def test_manning_bonus_multiplier_scales_with_skill() -> None:
    c = _sapien()
    assert manning_bonus_multiplier(c, "piloting") == 1.0
    c.skills[Skill.PILOTING] = 15  # level 1
    assert manning_bonus_multiplier(c, "piloting") > 1.0
    c.skills[Skill.PILOTING] = 95  # level 3
    assert abs(manning_bonus_multiplier(c, "piloting") - 1.99) < 0.05
