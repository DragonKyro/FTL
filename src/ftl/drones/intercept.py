"""Defense drone projectile interception.

Called from `CombatEngine._tick_projectiles` before each projectile is
resolved. If any defense drone on the target ship is powered, off
cooldown, and rolls under its intercept_chance, the projectile is
intercepted (deleted) and the drone enters its short cooldown.

Phase 3 default: defense drones only intercept missiles
(`weapon_family == "missile"`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.drones.runtime import DEFENSE_INTERCEPT_COOLDOWN

if TYPE_CHECKING:
    from random import Random

    from ftl.ships.ship import Ship
    from ftl.weapons.projectile import Projectile


def try_intercept(
    projectile: Projectile, defender_ship: Ship, rng: Random
) -> bool:
    """Return True if a defense drone successfully intercepted `projectile`."""
    if projectile.weapon_family != "missile":
        return False
    for drone in defender_ship.drones:
        if not drone.alive or not drone.powered:
            continue
        if drone.stats.family != "defense":
            continue
        if drone.intercept_cooldown > 0:
            continue
        if rng.random() < drone.stats.intercept_chance:
            drone.intercept_cooldown = DEFENSE_INTERCEPT_COOLDOWN
            return True
    return False
