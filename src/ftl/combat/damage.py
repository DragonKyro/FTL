"""Damage application pipeline.

A `DamageEvent` is the canonical "something hit a ship" record. The pipeline
applies shields (in `shield_layer.py` and the `ShieldsSystem`), then the
remaining damage to the target room and hull, then secondary effects (ion,
crew damage, fire, breach). Phase-0 stub only handles raw hull damage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship


@dataclass
class DamageEvent:
    ship: Ship
    room_id: str
    damage: int
    ion_damage: int = 0
    crew_damage: int = 0
    system_damage: int = 0
    breach: bool = False
    fire: bool = False


def apply_damage(event: DamageEvent) -> None:
    """Apply a DamageEvent. Phase-0: hull damage only."""
    if event.damage > 0:
        event.ship.hull.damage(event.damage)
