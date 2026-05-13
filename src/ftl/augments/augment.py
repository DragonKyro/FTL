"""Augment base + hook points.

Augments are mostly passive ship modifiers — extra evasion, faster reactor
recharge, etc. Each augment lives as YAML (`content/augments/*.yaml`); a few
that need active logic subclass `Augment` and override the relevant hook.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship


@dataclass(frozen=True)
class AugmentStats:
    id: str
    name: str
    hook: str = ""
    value: float = 0.0


class Augment:
    """Passive ship modifier."""

    def __init__(self, stats: AugmentStats) -> None:
        self.stats: AugmentStats = stats

    def on_jump(self, ship: Ship) -> None:
        return None

    def on_damage_taken(self, ship: Ship, amount: int) -> None:
        return None

    def modify_ship_stats(self, ship: Ship) -> None:
        return None
