"""Damage event + result structs.

The actual pipeline lives in `combat/pipeline.py`. This module exists to
hold the canonical message types — a `DamageEvent` is the input,
`DamageResult` is the output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship


@dataclass
class DamageEvent:
    """A pending damage application against a ship."""

    ship: Ship
    room_id: str
    damage: int
    ion_damage: int = 0
    crew_damage: int = 0
    system_damage: int = 0
    breach: bool = False
    fire: bool = False
    shield_piercing: bool = False


@dataclass
class DamageResult:
    """Outcome of one DamageEvent passing through the pipeline."""

    missed: bool = False
    shield_absorbed: bool = False
    hull_damage: int = 0
    system_damage: int = 0
