"""Augment install/uninstall side effects on the ship."""

from __future__ import annotations

from ftl.augments.factory import augment_from_def
from ftl.core.game import Game
from ftl.ships.ship import PlayerShip


def _ship():  # type: ignore[no-untyped-def]
    game = Game()
    game.load_content()
    return game, PlayerShip.from_def(game.registry.ships["wayfarer"], game.registry)


def test_riveted_plating_adds_hull() -> None:
    game, ship = _ship()
    aug_def = game.registry.augments["riveted_plating"]
    aug = augment_from_def(aug_def)
    assert aug is not None
    start_max = ship.hull.maximum
    aug.install(ship)
    assert ship.hull.maximum == start_max + 5
    aug.uninstall(ship)
    assert ship.hull.maximum == start_max


def test_mote_reactor_link_reduces_drone_power_cost() -> None:
    game, ship = _ship()
    aug = augment_from_def(game.registry.augments["mote_reactor_link"])
    assert aug is not None
    start = ship.drone_power_discount
    aug.install(ship)
    assert ship.drone_power_discount == start + 1
    aug.uninstall(ship)
    assert ship.drone_power_discount == start


def test_helix_scanners_bumps_sensors_bonus() -> None:
    game, ship = _ship()
    aug = augment_from_def(game.registry.augments["helix_scanners"])
    assert aug is not None
    aug.install(ship)
    assert ship.sensors_bonus >= 1


def test_threadlink_sets_revive_chance() -> None:
    game, ship = _ship()
    aug = augment_from_def(game.registry.augments["lattice_threadlink"])
    assert aug is not None
    aug.install(ship)
    assert ship.threadlink_revive_chance == 0.25


def test_bonebreaker_drills_boosts_melee_mult() -> None:
    game, ship = _ship()
    aug = augment_from_def(game.registry.augments["bonebreaker_drills"])
    assert aug is not None
    start = ship.melee_damage_mult
    aug.install(ship)
    assert ship.melee_damage_mult > start
