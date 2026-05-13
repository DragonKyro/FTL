"""Store inventory generator.

Builds a randomized inventory of weapons, drones, augments, hireable
species, and system-upgrade offers from the active `Registry`. The
returned `StoreInventory` is consumed by the `StoreScene` and by
`purchase.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from random import Random

    from ftl.data.registry import Registry
    from ftl.data.schemas import (
        AugmentDef,
        DroneDef,
        SpeciesDef,
        WeaponDef,
    )


REPAIR_UNIT_COST: int = 2
HIRE_COST: int = 45


@dataclass
class SystemUpgradeOffer:
    system_name: str
    new_level: int
    cost: int


@dataclass
class StoreInventory:
    weapons: list[WeaponDef] = field(default_factory=list)
    drones: list[DroneDef] = field(default_factory=list)
    augments: list[AugmentDef] = field(default_factory=list)
    crew_for_hire: list[SpeciesDef] = field(default_factory=list)
    system_upgrades: list[SystemUpgradeOffer] = field(default_factory=list)
    repair_unit_cost: int = REPAIR_UNIT_COST


def generate_store_inventory(registry: Registry, rng: Random) -> StoreInventory:
    """Build a fresh store stock from registry contents."""
    weapons = list(registry.weapons.values())
    drones = list(registry.drones.values())
    augments = list(registry.augments.values())
    species = [s for s in registry.species.values() if s.id != "synthetic"]
    rng.shuffle(weapons)
    rng.shuffle(drones)
    rng.shuffle(augments)
    rng.shuffle(species)
    return StoreInventory(
        weapons=weapons[:3],
        drones=drones[:2],
        augments=augments[:2],
        crew_for_hire=species[:1],
    )


def build_upgrade_offers(player_ship, registry: Registry) -> list[SystemUpgradeOffer]:  # type: ignore[no-untyped-def]
    """Per the player ship's current system levels, list the +1 upgrades available."""
    offers: list[SystemUpgradeOffer] = []
    for name, system in player_ship.systems.items():
        if system.level >= system.max_power:
            continue
        cost = 30 * (system.level + 1)
        offers.append(SystemUpgradeOffer(system_name=name, new_level=system.level + 1, cost=cost))
    return offers
