"""WeaponsSystem — routes power to individual Weapon instances on the ship."""

from __future__ import annotations

from ftl.systems.system import System


class WeaponsSystem(System):
    name = "weapons"

    def __init__(self, max_power: int = 8, level: int = 4) -> None:
        # Default level = 4 → up to four power slots for weapons (enough for
        # the Wayfarer's laser + missile, with headroom).
        super().__init__(max_power=max_power, level=level)
