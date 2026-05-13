"""Shared test fixtures."""

from __future__ import annotations

import pytest

from ftl.crew.crew import Crew
from ftl.crew.species import Species
from ftl.weapons.weapon import WeaponStats


@pytest.fixture
def basic_species() -> Species:
    return Species(id="test_species", name="Test Species", max_hp=100)


@pytest.fixture
def basic_crew(basic_species: Species) -> Crew:
    return Crew(name="Tester", species=basic_species)


@pytest.fixture
def basic_weapon_stats() -> WeaponStats:
    return WeaponStats(
        id="test_laser",
        name="Test Laser",
        family="laser",
        damage=1,
        charge_time=10.0,
        power_required=1,
    )
