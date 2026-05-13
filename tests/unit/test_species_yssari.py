"""Yssari mind-control immunity."""

from __future__ import annotations

from ftl.crew.crew import Crew
from ftl.crew.species import Species
from ftl.crew.species_behaviors import YssariBehavior
from ftl.systems.mind_control import MindControlSystem


def test_yssari_resists_mind_control() -> None:
    mc = MindControlSystem()
    mc.set_power(1)
    target = Crew(
        name="Y", species=Species(id="yssari", name="Yssari"),
        team="enemy", behavior=YssariBehavior(),
    )
    assert not mc.begin(target)
    assert target.team == "enemy"  # unchanged
    assert not mc.is_active


def test_non_yssari_can_be_mind_controlled() -> None:
    from ftl.crew.species_behaviors import SapienBehavior

    mc = MindControlSystem()
    mc.set_power(1)
    target = Crew(
        name="S", species=Species(id="sapien", name="Sapien"),
        team="enemy", behavior=SapienBehavior(),
    )
    assert mc.begin(target)
    assert target.team == "player"
