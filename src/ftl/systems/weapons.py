"""WeaponsSystem — routes power to individual Weapon instances on the ship."""

from __future__ import annotations

from ftl.systems.system import System


class WeaponsSystem(System):
    name = "weapons"
