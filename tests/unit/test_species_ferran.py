"""Ferran lockdown — closes doors in current room for the duration."""

from __future__ import annotations

from ftl.crew.crew import Crew
from ftl.crew.species import Species
from ftl.crew.species_behaviors import FerranBehavior
from ftl.crew.species_behaviors.ferran import LOCKDOWN_DURATION
from ftl.data.registry import Registry
from ftl.ships.ship import PlayerShip


def _ship_with_ferran():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    ship = PlayerShip.from_def(reg.ships["wayfarer"], reg)
    species = Species(id="ferran", name="Ferran")
    crew = Crew(name="F", species=species, behavior=FerranBehavior())
    crew.home_ship = ship
    crew.current_ship = ship
    crew.current_tile = ship.rooms["bridge"].tiles[0]
    ship.crew.append(crew)
    return ship, crew


def test_activate_lockdown_closes_room_doors() -> None:
    ship, crew = _ship_with_ferran()
    assert crew.behavior.activate_lockdown(crew)
    # Every door bordering the bridge should now be force-closed.
    bridge_doors = [
        d for d in ship.doors.values()
        if d.room_a == "bridge" or d.room_b == "bridge"
    ]
    assert len(bridge_doors) > 0
    assert all(d.force_closed for d in bridge_doors)


def test_lockdown_releases_after_duration() -> None:
    ship, crew = _ship_with_ferran()
    crew.behavior.activate_lockdown(crew)
    bridge_doors = [
        d for d in ship.doors.values()
        if d.room_a == "bridge" or d.room_b == "bridge"
    ]
    # Tick past the lockdown duration.
    for _ in range(int(LOCKDOWN_DURATION * 60) + 5):
        crew.behavior.on_tick(crew, 1.0 / 60.0)
    assert all(not d.force_closed for d in bridge_doors)


def test_cannot_double_activate() -> None:
    _ship, crew = _ship_with_ferran()
    assert crew.behavior.activate_lockdown(crew)
    assert not crew.behavior.activate_lockdown(crew)
