"""Crew construction, species stats, alive flag."""

from __future__ import annotations

from ftl.crew.crew import Crew, CrewState
from ftl.crew.skills import Skill
from ftl.crew.species import Species


def test_crew_starts_full_hp_and_idle(basic_crew: Crew):
    assert basic_crew.alive
    assert basic_crew.hp == basic_crew.max_hp
    assert basic_crew.state is CrewState.IDLE


def test_species_stats_applied_to_hp():
    sp = Species(id="tough", name="Tough", max_hp=150)
    c = Crew(name="Brick", species=sp)
    assert c.hp == 150
    assert c.max_hp == 150


def test_crew_dies_at_zero_hp(basic_crew: Crew):
    basic_crew.hp = 0
    assert not basic_crew.alive


def test_skills_all_initialized():
    sp = Species(id="any", name="Any")
    c = Crew(name="Trainee", species=sp)
    for skill in Skill:
        assert c.skills[skill] == 0
