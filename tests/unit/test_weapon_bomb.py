"""Bomb weapon: bypasses shields; consumes a missile."""

from __future__ import annotations

from random import Random

from ftl.combat.damage import DamageEvent
from ftl.combat.pipeline import apply_damage
from ftl.ships.room import Room
from ftl.ships.ship import EnemyShip
from ftl.systems.shields import ShieldsSystem


def test_bomb_bypasses_shields() -> None:
    ship = EnemyShip(name="t", max_hull=20)
    ship.add_room(Room(id="shield_room"))
    ship.add_room(Room(id="any"))
    shields = ShieldsSystem()
    shields.set_power(2)
    shields.current_layers = 1
    ship.install_system(shields, "shield_room")
    event = DamageEvent(
        ship=ship, room_id="any", damage=3, shield_piercing=True,
    )
    result = apply_damage(event, Random(0))
    assert result.hull_damage == 3
    # Shield untouched (bomb bypassed it).
    assert shields.current_layers == 1
