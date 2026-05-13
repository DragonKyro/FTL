"""Composable on-hit effects.

A weapon's `WeaponStats` describes its effect parameters; on impact we build
an `OnHitEffect` and apply it to the target room. Keeping effects
composable lets YAML express e.g. "ion + breach + 2 damage" in one weapon.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.room import Room


@dataclass
class OnHitEffect:
    damage: int = 0
    breach_chance: float = 0.0
    fire_chance: float = 0.0
    stun_seconds: float = 0.0
    ion_damage: int = 0
    crew_damage: int = 0
    system_damage: int = 0

    def apply(self, room: Room) -> None:
        """Apply this effect to a room. Phase-1 will implement real logic."""
