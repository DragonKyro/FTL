"""Concrete `AugmentEffect` implementations for Phase-4 augments.

Each class knows how to apply to a Ship and how to remove cleanly so an
augment can be sold or replaced.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.augments.augment import AugmentEffect

if TYPE_CHECKING:
    from ftl.ships.ship import Ship


class RivetedPlating(AugmentEffect):
    """+5 max hull. Riveted scrap plates welded over the original frame."""

    def __init__(self, value: float = 5.0) -> None:
        self.value: int = int(value)

    def apply(self, ship: Ship) -> None:
        ship.hull.maximum += self.value
        ship.hull.current += self.value

    def remove(self, ship: Ship) -> None:
        ship.hull.maximum -= self.value
        ship.hull.current = min(ship.hull.current, ship.hull.maximum)


class MoteReactorLink(AugmentEffect):
    """Drones cost -1 power each. Stacked into `ship.drone_power_discount`."""

    def apply(self, ship: Ship) -> None:
        ship.drone_power_discount += 1

    def remove(self, ship: Ship) -> None:
        ship.drone_power_discount = max(0, ship.drone_power_discount - 1)


class HelixScanners(AugmentEffect):
    """+1 sensors visibility, even without manning."""

    def apply(self, ship: Ship) -> None:
        ship.sensors_bonus += 1

    def remove(self, ship: Ship) -> None:
        ship.sensors_bonus = max(0, ship.sensors_bonus - 1)


class BonebreakerDrills(AugmentEffect):
    """+10% crew melee damage."""

    def apply(self, ship: Ship) -> None:
        ship.melee_damage_mult *= 1.10

    def remove(self, ship: Ship) -> None:
        ship.melee_damage_mult /= 1.10


class LatticeThreadlink(AugmentEffect):
    """25% chance on crew death to respawn at the medbay/clonebay with 1 HP.

    The actual respawn coin-flip happens in `CombatEngine._sweep_dead`; this
    effect just sets the ship-wide chance.
    """

    def apply(self, ship: Ship) -> None:
        ship.threadlink_revive_chance = max(ship.threadlink_revive_chance, 0.25)

    def remove(self, ship: Ship) -> None:
        ship.threadlink_revive_chance = 0.0


_EFFECTS: dict[str, type[AugmentEffect]] = {
    "riveted_plating": RivetedPlating,
    "mote_reactor_link": MoteReactorLink,
    "helix_scanners": HelixScanners,
    "bonebreaker_drills": BonebreakerDrills,
    "lattice_threadlink": LatticeThreadlink,
}


def effect_for(effect_id: str, value: float = 0.0) -> AugmentEffect | None:
    cls = _EFFECTS.get(effect_id)
    if cls is None:
        return None
    if cls is RivetedPlating:
        return RivetedPlating(value=value or 5.0)
    return cls()
