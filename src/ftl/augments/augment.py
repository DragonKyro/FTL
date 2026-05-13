"""Augment base + AugmentStats + AugmentEffect protocol.

Augments are passive ship modifiers. Each carries an `AugmentEffect`
that knows how to `apply` and `remove` itself from a ship. Concrete
effects live in `augments/effects.py`. The factory
`augment_for(def, registry)` builds a wired Augment from an `AugmentDef`.
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
    effect_id: str = ""
    value: float = 0.0
    rarity: int = 1


class AugmentEffect:
    """Subclasses override apply / remove for their concrete effect."""

    def apply(self, ship: Ship) -> None: ...
    def remove(self, ship: Ship) -> None: ...


class Augment:
    """Runtime augment: stats + an applied effect."""

    def __init__(self, stats: AugmentStats, effect: AugmentEffect) -> None:
        self.stats: AugmentStats = stats
        self.effect: AugmentEffect = effect
        self.installed: bool = False

    def install(self, ship: Ship) -> None:
        if self.installed:
            return
        self.effect.apply(ship)
        self.installed = True

    def uninstall(self, ship: Ship) -> None:
        if not self.installed:
            return
        self.effect.remove(ship)
        self.installed = False
