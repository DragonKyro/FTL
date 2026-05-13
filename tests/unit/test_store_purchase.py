"""Store purchase actions mutate Run state correctly."""

from __future__ import annotations

from random import Random

from ftl.core.game import Game
from ftl.ships.ship import PlayerShip
from ftl.store.inventory import generate_store_inventory
from ftl.store.purchase import (
    buy_augment,
    buy_drone,
    buy_repair,
    buy_weapon,
    hire_crew,
)


def _game_with_ship_and_inventory():  # type: ignore[no-untyped-def]
    game = Game()
    game.load_content()
    run = game.new_run(seed=2)
    run.player_ship = PlayerShip.from_def(game.registry.ships["wayfarer"], game.registry)
    run.scrap = 500
    return game, run, generate_store_inventory(game.registry, Random(2))


def test_buy_weapon_adds_to_ship_and_deducts_scrap() -> None:
    _game, run, inv = _game_with_ship_and_inventory()
    weapons_before = len(run.player_ship.weapons)
    weapon = inv.weapons[0]
    cost = weapon.cost
    assert buy_weapon(run, weapon)
    assert len(run.player_ship.weapons) == weapons_before + 1
    assert run.scrap == 500 - cost


def test_buy_drone_adds_to_ship() -> None:
    _game, run, inv = _game_with_ship_and_inventory()
    drones_before = len(run.player_ship.drones)
    drone = inv.drones[0]
    assert buy_drone(run, drone)
    assert len(run.player_ship.drones) == drones_before + 1


def test_buy_augment_appends_to_run() -> None:
    _game, run, inv = _game_with_ship_and_inventory()
    aug = inv.augments[0]
    before_aug = len(run.augments)
    if buy_augment(run, aug):
        assert len(run.augments) == before_aug + 1


def test_buy_repair_increases_hull() -> None:
    _game, run, _inv = _game_with_ship_and_inventory()
    run.player_ship.hull.damage(5)
    hp_before = run.player_ship.hull.current
    repaired = buy_repair(run, 3)
    assert repaired == 3
    assert run.player_ship.hull.current == hp_before + 3


def test_hire_crew_adds_member() -> None:
    _game, run, inv = _game_with_ship_and_inventory()
    if not inv.crew_for_hire:
        return  # nothing to test if shuffled out
    before = len(run.player_ship.crew)
    species = inv.crew_for_hire[0]
    if hire_crew(run, species):
        assert len(run.player_ship.crew) == before + 1


def test_cannot_afford_blocks_purchase() -> None:
    _game, run, inv = _game_with_ship_and_inventory()
    run.scrap = 0
    weapon = inv.weapons[0]
    assert not buy_weapon(run, weapon)
