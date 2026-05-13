"""CombatState outcome semantics + damage event struct."""

from __future__ import annotations

from ftl.combat.combat_state import CombatState, Outcome
from ftl.combat.damage import DamageEvent
from ftl.ships.ship import EnemyShip, PlayerShip


def test_combat_state_initial_outcome_is_fighting():
    player = PlayerShip(name="P", max_hull=30)
    enemy = EnemyShip(name="E", max_hull=10)
    combat = CombatState(player, enemy)

    assert combat.outcome is Outcome.FIGHTING
    assert not combat.over


def test_combat_state_outcome_is_settable_and_sticky():
    player = PlayerShip(name="P", max_hull=30)
    enemy = EnemyShip(name="E", max_hull=10)
    combat = CombatState(player, enemy)

    combat.outcome = Outcome.WON
    assert combat.over
    assert combat.player_won
    assert not combat.player_lost
    assert not combat.player_fled


def test_combat_state_tracks_player_inventory():
    player = PlayerShip(max_hull=20)
    enemy = EnemyShip(max_hull=10)
    combat = CombatState(player, enemy, player_missiles=4)
    assert combat.player_inventory.missiles == 4


def test_damage_event_struct_carries_fields():
    ship = PlayerShip(max_hull=20)
    event = DamageEvent(ship=ship, room_id="bridge", damage=3)
    assert event.damage == 3
    assert event.room_id == "bridge"
