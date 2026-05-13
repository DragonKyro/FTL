"""Choir +25% piloting manning bonus."""

from __future__ import annotations

from ftl.crew.crew import Crew
from ftl.crew.species import Species
from ftl.crew.species_behaviors import ChoirBehavior


def test_choir_piloting_bonus() -> None:
    crew = Crew(name="C", species=Species(id="choir", name="Choir"), behavior=ChoirBehavior())
    assert crew.behavior.manning_bonus(crew, "piloting") == 0.25


def test_choir_no_bonus_other_systems() -> None:
    crew = Crew(name="C", species=Species(id="choir", name="Choir"), behavior=ChoirBehavior())
    assert crew.behavior.manning_bonus(crew, "weapons") == 0.0
    assert crew.behavior.manning_bonus(crew, "engines") == 0.0
