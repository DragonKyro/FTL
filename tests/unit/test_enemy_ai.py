"""EnemyPilot heuristic behavior."""

from __future__ import annotations

from random import Random

from ftl.ai.enemy_pilot import EnemyPilot
from ftl.ships.room import Room
from ftl.ships.ship import EnemyShip, PlayerShip
from ftl.systems.piloting import PilotingSystem
from ftl.systems.shields import ShieldsSystem
from ftl.systems.weapons import WeaponsSystem
from ftl.weapons.weapon import Weapon, WeaponStats


def _laser() -> Weapon:
    return Weapon(
        WeaponStats(
            id="x", name="L", family="laser", damage=1, charge_time=10.0,
            power_required=1,
        )
    )


def _player() -> PlayerShip:
    ship = PlayerShip(name="p", max_hull=10, max_reactor_power=4)
    ship.add_room(Room(id="bridge"))
    ship.add_room(Room(id="gun_bay"))
    ship.add_room(Room(id="shield_room"))
    ship.add_room(Room(id="engine_room"))
    ship.install_system(PilotingSystem(), "bridge")
    ship.install_system(WeaponsSystem(), "gun_bay")
    ship.install_system(ShieldsSystem(), "shield_room")
    return ship


def _enemy() -> EnemyShip:
    ship = EnemyShip(name="e", max_hull=10, max_reactor_power=4)
    ship.add_room(Room(id="bridge"))
    ship.add_room(Room(id="gun_bay"))
    ship.add_room(Room(id="shield_room"))
    ship.install_system(PilotingSystem(), "bridge")
    ship.install_system(WeaponsSystem(), "gun_bay")
    ship.install_system(ShieldsSystem(), "shield_room")
    ship.weapons.append(_laser())
    return ship


def test_ai_allocates_power_at_init():
    enemy = _enemy()
    EnemyPilot(enemy, _player(), Random(0))
    # weapons gets 1, piloting gets 1, shields gets 2 → 4 total
    assert enemy.systems["piloting"].current_power >= 1
    assert enemy.systems["weapons"].current_power >= 1
    assert enemy.systems["shields"].current_power >= 2


def test_ai_powers_its_weapon():
    enemy = _enemy()
    EnemyPilot(enemy, _player(), Random(0))
    assert enemy.weapons[0].powered is True


def test_ai_targets_player_gun_bay_first():
    enemy = _enemy()
    player = _player()
    ai = EnemyPilot(enemy, player, Random(0))
    ai.tick(0.0)
    assert enemy.weapons[0].target_room_id == "gun_bay"


def test_ai_falls_back_to_shield_room_if_weapons_destroyed():
    enemy = _enemy()
    player = _player()
    # Destroy the player's weapons system (mark fully damaged).
    player.systems["weapons"].damage = player.systems["weapons"].level
    ai = EnemyPilot(enemy, player, Random(0))
    ai.tick(0.0)
    assert enemy.weapons[0].target_room_id == "shield_room"


def test_ai_retargets_when_current_target_destroyed():
    enemy = _enemy()
    player = _player()
    ai = EnemyPilot(enemy, player, Random(0))
    ai.tick(0.0)
    assert enemy.weapons[0].target_room_id == "gun_bay"

    # Destroy gun_bay's weapons system; AI should re-target.
    player.systems["weapons"].damage = player.systems["weapons"].level
    ai.tick(0.0)
    assert enemy.weapons[0].target_room_id != "gun_bay"
