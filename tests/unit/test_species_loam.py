"""Loam passive HP regen."""

from __future__ import annotations

from ftl.crew.crew import Crew
from ftl.crew.species import Species
from ftl.crew.species_behaviors import LoamBehavior


def test_loam_regenerates_over_time() -> None:
    species = Species(id="loam", name="Loam", max_hp=100)
    crew = Crew(name="L", species=species, behavior=LoamBehavior())
    crew.hp = 50
    for _ in range(60 * 4):  # 4 seconds → ~1 HP
        crew.behavior.on_tick(crew, 1.0 / 60.0)
    assert crew.hp > 50


def test_loam_caps_at_max_hp() -> None:
    species = Species(id="loam", name="Loam", max_hp=100)
    crew = Crew(name="L", species=species, behavior=LoamBehavior())
    crew.hp = float(crew.max_hp)
    crew.behavior.on_tick(crew, 1.0)
    assert crew.hp == float(crew.max_hp)


def test_dead_loam_does_not_regenerate() -> None:
    species = Species(id="loam", name="Loam", max_hp=100)
    crew = Crew(name="L", species=species, behavior=LoamBehavior())
    crew.hp = 0.0
    crew.behavior.on_tick(crew, 10.0)
    assert crew.hp == 0.0
