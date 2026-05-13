"""MindControlSystem team flip + restoration."""

from __future__ import annotations

from ftl.crew.crew import Crew
from ftl.crew.species import Species
from ftl.crew.species_behaviors import behavior_for
from ftl.systems.mind_control import ACTIVE_SECONDS, MindControlSystem


def _target() -> Crew:
    return Crew(
        name="t", species=Species(id="sapien", name="Sapien"),
        team="enemy", behavior=behavior_for("sapien"),
    )


def _mc_ready() -> MindControlSystem:
    mc = MindControlSystem()
    mc.set_power(1)
    return mc


def test_begin_flips_team() -> None:
    mc = _mc_ready()
    target = _target()
    assert mc.begin(target)
    assert target.team == "player"
    assert mc.is_active


def test_restores_team_after_duration() -> None:
    mc = _mc_ready()
    target = _target()
    mc.begin(target)
    for _ in range(60 * int(ACTIVE_SECONDS + 1)):
        mc.tick(1.0 / 60.0)
    assert target.team == "enemy"
    assert not mc.is_active


def test_target_dying_ends_early() -> None:
    mc = _mc_ready()
    target = _target()
    mc.begin(target)
    target.hp = 0
    mc.tick(1.0 / 60.0)
    assert not mc.is_active


def test_cannot_begin_when_unpowered() -> None:
    mc = MindControlSystem()
    mc.set_power(0)
    target = _target()
    assert not mc.begin(target)
