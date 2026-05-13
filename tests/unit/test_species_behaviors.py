"""Species behavior hooks for Halene, Mhirsa, Sapien."""

from __future__ import annotations

from ftl.crew.crew import Crew
from ftl.crew.species import Species
from ftl.crew.species_behaviors import (
    HaleneBehavior,
    MhirsaBehavior,
    SapienBehavior,
    behavior_for,
)
from ftl.data.registry import Registry
from ftl.ships.ship import PlayerShip


def test_behavior_factory_returns_correct_subclasses() -> None:
    assert isinstance(behavior_for("sapien"), SapienBehavior)
    assert isinstance(behavior_for("halene"), HaleneBehavior)
    assert isinstance(behavior_for("mhirsa"), MhirsaBehavior)


def test_unknown_species_falls_back_to_sapien() -> None:
    behavior = behavior_for("nonexistent_species")
    assert isinstance(behavior, SapienBehavior)


def test_mhirsa_melee_bonus_applies() -> None:
    species = Species(id="mhirsa", name="Mhirsa")
    crew = Crew(name="K", species=species, team="player", behavior=MhirsaBehavior())
    assert crew.behavior.melee_damage(crew, 10.0) == 15.0


def test_mhirsa_move_speed_multiplier_is_above_1() -> None:
    species = Species(id="mhirsa", name="Mhirsa")
    crew = Crew(name="K", species=species, team="player", behavior=MhirsaBehavior())
    assert crew.behavior.move_speed_multiplier(crew) > 1.0


def test_halene_contributes_reactor_power_while_alive() -> None:
    reg = Registry()
    reg.load_all()
    ship = PlayerShip.from_def(reg.ships["wayfarer"], reg)
    base_reactor = ship.base_max_reactor_power
    # One tick to let on_tick run.
    ship.tick(1.0 / 60.0)
    halene_present = any(c.species.id == "halene" for c in ship.crew)
    assert halene_present
    # With Halene alive in an oxygenated room, crew_power_bonus should be 1.
    assert ship.crew_power_bonus == 1
    assert ship.max_reactor_power == base_reactor + 1


def test_dead_halene_does_not_contribute_power() -> None:
    reg = Registry()
    reg.load_all()
    ship = PlayerShip.from_def(reg.ships["wayfarer"], reg)
    halene = next(c for c in ship.crew if c.species.id == "halene")
    halene.hp = 0.0
    ship.tick(1.0 / 60.0)
    # crew_power_bonus is reset each tick; dead Halene contributes 0.
    assert ship.crew_power_bonus == 0
