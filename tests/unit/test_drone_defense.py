"""Defense drone interception of missiles."""

from __future__ import annotations

from random import Random

from ftl.drones.drone import Drone, DroneStats
from ftl.drones.intercept import try_intercept
from ftl.weapons.projectile import Projectile


def _defense_drone(intercept_chance: float = 1.0) -> Drone:
    drone = Drone(
        DroneStats(id="d", name="d", family="defense", intercept_chance=intercept_chance)
    )
    drone.powered = True
    drone.intercept_cooldown = 0.0
    return drone


class _StubShip:
    def __init__(self, drones: list[Drone]) -> None:
        self.drones = drones


def _missile() -> Projectile:
    return Projectile(
        source_ship=None,  # type: ignore[arg-type]
        target_ship=None,  # type: ignore[arg-type]
        target_room_id="x",
        damage=2,
        shield_piercing=True,
        weapon_family="missile",
    )


def _laser() -> Projectile:
    return Projectile(
        source_ship=None,  # type: ignore[arg-type]
        target_ship=None,  # type: ignore[arg-type]
        target_room_id="x",
        damage=1,
        shield_piercing=False,
        weapon_family="laser",
    )


def test_defense_drone_intercepts_missile_at_100pct() -> None:
    drone = _defense_drone(1.0)
    ship = _StubShip([drone])
    assert try_intercept(_missile(), ship, Random(0))  # type: ignore[arg-type]


def test_defense_drone_ignores_lasers() -> None:
    drone = _defense_drone(1.0)
    ship = _StubShip([drone])
    assert not try_intercept(_laser(), ship, Random(0))  # type: ignore[arg-type]


def test_unpowered_drone_does_not_intercept() -> None:
    drone = _defense_drone(1.0)
    drone.powered = False
    ship = _StubShip([drone])
    assert not try_intercept(_missile(), ship, Random(0))  # type: ignore[arg-type]


def test_drone_enters_cooldown_after_intercept() -> None:
    drone = _defense_drone(1.0)
    ship = _StubShip([drone])
    try_intercept(_missile(), ship, Random(0))  # type: ignore[arg-type]
    assert drone.intercept_cooldown > 0


def test_cooldown_blocks_second_intercept() -> None:
    drone = _defense_drone(1.0)
    drone.intercept_cooldown = 0.5
    ship = _StubShip([drone])
    assert not try_intercept(_missile(), ship, Random(0))  # type: ignore[arg-type]
