"""Crew-vs-crew melee resolution."""

from __future__ import annotations

from ftl.crew.combat import tick_crew_combat
from ftl.crew.crew import Crew, CrewState
from ftl.crew.species import Species
from ftl.crew.species_behaviors import behavior_for
from ftl.data.registry import Registry
from ftl.ships.ship import EnemyShip, PlayerShip


def _scenario():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    player = PlayerShip.from_def(reg.ships["wayfarer"], reg)
    enemy = EnemyShip.from_def(reg.ships["vein_skiff"], reg)
    return player, enemy, reg


def _move_to(crew, tile) -> None:  # type: ignore[no-untyped-def]
    crew.current_tile = tile
    crew.path = []
    crew.move_progress = 0.0


def test_opposing_crew_on_same_tile_fight() -> None:
    player, enemy, reg = _scenario()
    # Send a player Mhirsa to the enemy's bridge to fight.
    mhirsa = next(c for c in player.crew if c.species.id == "mhirsa")
    enemy_bridge_tile = enemy.tile_graph[(0, 0)]
    # Move the Mhirsa into the enemy bridge tile (manually, for the test).
    enemy.crew.append(mhirsa)
    player.crew.remove(mhirsa)
    mhirsa.current_ship = enemy
    _move_to(mhirsa, enemy_bridge_tile)

    enemy_sapien = enemy.crew[0]  # the Sapien on the bridge
    _move_to(enemy_sapien, enemy_bridge_tile)

    dt = 1.0 / 60.0
    # 2 seconds of combat.
    for _ in range(60 * 2):
        tick_crew_combat(enemy, dt)
    # Both should have taken damage; Mhirsa hits harder so the Sapien should
    # be hurt more.
    assert mhirsa.hp < mhirsa.max_hp
    assert enemy_sapien.hp < enemy_sapien.max_hp
    assert (enemy_sapien.max_hp - enemy_sapien.hp) > (mhirsa.max_hp - mhirsa.hp)


def test_lone_crew_does_not_fight() -> None:
    """A crew member alone on a tile (no opponent) should not be FIGHTING."""
    player, _, _ = _scenario()
    crew = player.crew[0]
    crew.state = CrewState.IDLE
    tick_crew_combat(player, 1.0 / 60.0)
    assert crew.state is not CrewState.FIGHTING


def test_dead_crew_have_zero_hp() -> None:
    species = Species(id="x", name="X", max_hp=10, combat_damage=10.0)
    a = Crew(name="A", species=species, team="player", behavior=behavior_for("sapien"))
    b = Crew(name="B", species=species, team="enemy", behavior=behavior_for("sapien"))
    # Construct a minimal ship-like environment for the combat tick. The
    # function only iterates `ship.crew` and reads each crew's
    # `current_tile`, so a stub object works.
    from ftl.ships.tile import Tile

    tile = Tile(x=0, y=0, room_id="r")
    a.current_tile = tile
    b.current_tile = tile

    class _StubShip:
        def __init__(self) -> None:
            self.crew = [a, b]

    stub = _StubShip()
    dt = 1.0 / 60.0
    for _ in range(60 * 10):  # plenty of time
        tick_crew_combat(stub, dt)  # type: ignore[arg-type]
        if not a.alive or not b.alive:
            break
    assert (not a.alive) or (not b.alive)
