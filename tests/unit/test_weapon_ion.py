"""Ion weapon: deposits ion_charge on target system; no hull damage."""

from __future__ import annotations

from random import Random

from ftl.combat.damage import DamageEvent
from ftl.combat.pipeline import apply_damage
from ftl.ships.room import Room
from ftl.ships.ship import EnemyShip
from ftl.systems.weapons import WeaponsSystem


def test_ion_deposits_charge_no_hull_damage() -> None:
    ship = EnemyShip(name="t", max_hull=20)
    ship.add_room(Room(id="gun_bay"))
    ws = WeaponsSystem()
    ws.set_power(2)
    ship.install_system(ws, "gun_bay")
    event = DamageEvent(
        ship=ship, room_id="gun_bay", damage=0, ion_damage=2, ion_only=True,
    )
    apply_damage(event, Random(0))
    assert ship.hull.current == 20  # no hull damage
    assert ws.ion_charge > 0


def test_ion_disables_system_during_charge() -> None:
    ship = EnemyShip(name="t", max_hull=20)
    ship.add_room(Room(id="gun_bay"))
    ws = WeaponsSystem()
    ws.set_power(2)
    ship.install_system(ws, "gun_bay")
    event = DamageEvent(
        ship=ship, room_id="gun_bay", damage=0, ion_damage=2, ion_only=True,
    )
    apply_damage(event, Random(0))
    assert not ws.is_operational  # ion charge prevents operation
