"""Per-tick fire + system damage from fire.

Fire is a per-room float in [0.0, 100.0]. Each tick:

1. **Growth.** Rooms with `fire > 0` and `oxygen > 0` grow fire by
   `FIRE_GROWTH_RATE * dt`.
2. **Vacuum-extinguishment.** Rooms with `fire > 0` and `oxygen == 0`
   shrink fire by `FIRE_EXTINGUISH_RATE * dt`.
3. **Spread.** Rooms with `fire >= FIRE_SPREAD_THRESHOLD` light
   adjacent rooms (through open doors) with a small starting fire,
   but only if the neighbor has oxygen.
4. **Crew damage.** Crew in burning rooms lose HP at
   `FIRE_HP_PER_SEC * dt * (1 - species.fire_resistance)`.
5. **System damage.** Sub-tick accumulation on the room: each second
   of fire adds `FIRE_SYSTEM_DAMAGE_RATE` to a per-room accumulator;
   when ≥ 1.0, the system takes 1 damage bar.

Breach is *passive* — its only Phase-2 effect is venting oxygen in
`atmosphere.py`. Breach repair is in `crew.movement._assign_tasks`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship


FIRE_GROWTH_RATE: float = 2.0
FIRE_EXTINGUISH_RATE: float = 8.0
FIRE_SPREAD_THRESHOLD: float = 50.0
FIRE_SPREAD_IGNITION: float = 15.0
FIRE_HP_PER_SEC: float = 4.0
FIRE_SYSTEM_DAMAGE_RATE: float = 0.1  # damage-bars per sec; 1 bar every 10s


def tick_hazards(ship: Ship, dt: float) -> None:
    _grow_or_shrink_fire(ship, dt)
    _spread_fire(ship, dt)
    _damage_from_fire(ship, dt)


def _grow_or_shrink_fire(ship: Ship, dt: float) -> None:
    for room in ship.rooms.values():
        if room.fire <= 0:
            continue
        if room.oxygen > 0:
            room.fire = min(100.0, room.fire + FIRE_GROWTH_RATE * dt)
        else:
            room.fire = max(0.0, room.fire - FIRE_EXTINGUISH_RATE * dt)


def _spread_fire(ship: Ship, dt: float) -> None:
    new_fires: dict[str, float] = {}
    for door in ship.doors.values():
        if not door.is_open:
            continue
        room_a = ship.rooms.get(door.room_a)
        room_b = ship.rooms.get(door.room_b)
        if room_a is None or room_b is None:
            continue
        if room_a.fire >= FIRE_SPREAD_THRESHOLD and room_b.fire == 0 and room_b.oxygen > 0:
            new_fires[room_b.id] = max(new_fires.get(room_b.id, 0.0), FIRE_SPREAD_IGNITION)
        if room_b.fire >= FIRE_SPREAD_THRESHOLD and room_a.fire == 0 and room_a.oxygen > 0:
            new_fires[room_a.id] = max(new_fires.get(room_a.id, 0.0), FIRE_SPREAD_IGNITION)
    for room_id, fire in new_fires.items():
        room = ship.rooms[room_id]
        room.fire = max(room.fire, fire)


def _damage_from_fire(ship: Ship, dt: float) -> None:
    for room in ship.rooms.values():
        if room.fire <= 0:
            continue
        # Crew damage.
        for crew in ship.crew:
            if not crew.alive:
                continue
            if crew.current_tile is None or crew.current_tile.room_id != room.id:
                continue
            damage = FIRE_HP_PER_SEC * dt * (1.0 - crew.species.fire_resistance)
            if damage > 0:
                crew.hp = max(0.0, crew.hp - damage)
        # System damage via per-room accumulator.
        if room.system is not None:
            room.fire_system_damage_accum += FIRE_SYSTEM_DAMAGE_RATE * dt
            while room.fire_system_damage_accum >= 1.0 and room.system.damage < room.system.level:
                room.system.take_damage(1)
                room.fire_system_damage_accum -= 1.0
            if room.system.damage >= room.system.level:
                room.fire_system_damage_accum = 0.0
