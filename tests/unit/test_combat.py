"""Combat state win/loss + damage pipeline stub."""

from __future__ import annotations

from ftl.combat.combat_state import CombatState
from ftl.combat.damage import DamageEvent, apply_damage
from ftl.ships.ship import EnemyShip, PlayerShip


def test_combat_state_over_when_enemy_hull_destroyed():
    player = PlayerShip(name="P", max_hull=30)
    enemy = EnemyShip(name="E", max_hull=10)
    combat = CombatState(player, enemy)

    assert not combat.over

    enemy.hull.damage(10)
    assert combat.player_won
    assert combat.over


def test_combat_state_lost_when_player_destroyed():
    player = PlayerShip(name="P", max_hull=5)
    enemy = EnemyShip(name="E", max_hull=10)
    combat = CombatState(player, enemy)

    player.hull.damage(5)
    assert combat.player_lost
    assert combat.over


def test_damage_event_applies_hull_damage():
    ship = PlayerShip(max_hull=20)
    event = DamageEvent(ship=ship, room_id="bridge", damage=3)
    apply_damage(event)
    assert ship.hull.current == 17
