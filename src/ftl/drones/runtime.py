"""Per-tick drone driver.

Called from `CombatEngine.tick`. Handles:
- Powering drones up to the drone-control system's effective_power budget
- Per-family tick: defense (cooldown only — intercept happens in
  `intercept.try_intercept`), combat (charge + fire), repair (hull tick)
- Boarding / Anti-Personnel drones are deployed on-demand (not ticked
  here); once deployed, they become Crew with a `synthetic` species and
  obey the normal crew loop.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.weapons.projectile import Projectile

if TYPE_CHECKING:
    from random import Random

    from ftl.combat.engine import CombatEngine
    from ftl.drones.drone import Drone
    from ftl.ships.ship import Ship


COMBAT_DRONE_TRAVEL_TIME: float = 1.5
DEFENSE_INTERCEPT_COOLDOWN: float = 1.0
HULL_REPAIR_INTERVAL_SECONDS: float = 12.0


def tick_drones(
    ship: Ship,
    opponent: Ship,
    engine: CombatEngine,
    dt: float,
) -> None:
    """Power and tick the drones installed on `ship`."""
    drone_control = ship.systems.get("drone_control")
    budget = (
        drone_control.effective_power
        if drone_control is not None and drone_control.is_operational
        else 0
    )
    discount = getattr(ship, "drone_power_discount", 0)
    for drone in ship.drones:
        if not drone.alive:
            drone.powered = False
            continue
        cost = max(0, drone.stats.power_required - discount)
        if cost <= budget:
            drone.powered = True
            budget -= cost
        else:
            drone.powered = False
        if not drone.powered:
            continue
        _tick_one(drone, ship, opponent, engine, dt)


def _tick_one(
    drone: Drone,
    ship: Ship,
    opponent: Ship,
    engine: CombatEngine,
    dt: float,
) -> None:
    family = drone.stats.family
    if family == "defense":
        _tick_defense(drone, dt)
    elif family == "combat":
        _tick_combat(drone, ship, opponent, engine, dt)
    elif family == "repair":
        _tick_repair(drone, ship, dt)
    # boarding / anti_personnel deploy on command, not on tick.


def _tick_defense(drone: Drone, dt: float) -> None:
    if drone.intercept_cooldown > 0:
        drone.intercept_cooldown = max(0.0, drone.intercept_cooldown - dt)


def _tick_combat(
    drone: Drone,
    ship: Ship,
    opponent: Ship,
    engine: CombatEngine,
    dt: float,
) -> None:
    drone.charge_progress = min(
        drone.stats.charge_time, drone.charge_progress + dt
    )
    if drone.charge_progress < drone.stats.charge_time:
        return
    # Fire at a random enemy room (preserves the AI's pre-existing RNG).
    room_ids = list(opponent.rooms.keys())
    if not room_ids:
        return
    target_room_id = engine.rng.choice(room_ids)
    projectile = Projectile(
        source_ship=ship,
        target_ship=opponent,
        target_room_id=target_room_id,
        damage=drone.stats.damage,
        shield_piercing=False,
        weapon_family="laser",
        fire_chance=0.0,
        breach_chance=0.0,
        travel_time=COMBAT_DRONE_TRAVEL_TIME,
    )
    engine.projectiles.append(projectile)
    drone.charge_progress = 0.0


def _tick_repair(drone: Drone, ship: Ship, dt: float) -> None:
    if ship.hull.current >= ship.hull.maximum:
        drone.repair_progress = 0.0
        return
    drone.repair_progress += dt
    while drone.repair_progress >= HULL_REPAIR_INTERVAL_SECONDS:
        ship.hull.repair(1)
        drone.repair_progress -= HULL_REPAIR_INTERVAL_SECONDS
