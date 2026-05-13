"""Per-tick oxygen simulation + crew suffocation damage.

Oxygen is a per-room float in [0.0, 1.0]. Each tick:

1. **Production.** If the oxygen system is operational, raise oxygen in
   the room hosting it by `0.10 * effective_power * dt`.
2. **Venting.** Rooms with `breach > 0` lose oxygen at `0.20 * dt`.
3. **Flow.** Each open door allows oxygen to flow between its two
   rooms toward equilibrium at rate `1.0 / sec * differential`.
4. **Suffocation.** Crew in any room with `oxygen < 0.1` lose HP at
   `2 * dt * species.suffocation_mult` per second.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship


OXYGEN_SYSTEM_PRODUCTION: float = 0.10  # per power per second
OXYGEN_VENT_RATE: float = 0.20          # per second per breached room
OXYGEN_FLOW_RATE: float = 1.0           # fraction of differential per second
SUFFOCATION_HP_PER_SEC: float = 2.0
LOW_OXYGEN_THRESHOLD: float = 0.1


def tick_atmosphere(ship: Ship, dt: float) -> None:
    _produce_oxygen(ship, dt)
    _vent_breached(ship, dt)
    _flow_through_doors(ship, dt)
    _suffocate_crew(ship, dt)


def _produce_oxygen(ship: Ship, dt: float) -> None:
    oxygen_system = ship.oxygen_system
    if oxygen_system is None or not oxygen_system.is_operational:
        return
    # Find the room hosting the oxygen system.
    host = next(
        (r for r in ship.rooms.values() if r.system is oxygen_system),
        None,
    )
    if host is None:
        return
    host.oxygen = min(
        1.0,
        host.oxygen + OXYGEN_SYSTEM_PRODUCTION * oxygen_system.effective_power * dt,
    )


def _vent_breached(ship: Ship, dt: float) -> None:
    for room in ship.rooms.values():
        if room.breach > 0:
            room.oxygen = max(0.0, room.oxygen - OXYGEN_VENT_RATE * dt)


def _flow_through_doors(ship: Ship, dt: float) -> None:
    # Compute deltas first, then apply, to avoid order-of-iteration bias.
    deltas: dict[str, float] = {rid: 0.0 for rid in ship.rooms}
    fraction = min(1.0, OXYGEN_FLOW_RATE * dt)
    for door in ship.doors.values():
        if not door.is_open:
            continue
        room_a = ship.rooms.get(door.room_a)
        room_b = ship.rooms.get(door.room_b)
        if room_a is None or room_b is None:
            continue
        differential = room_b.oxygen - room_a.oxygen
        transfer = differential * (fraction / 2.0)
        deltas[room_a.id] += transfer
        deltas[room_b.id] -= transfer
    for rid, delta in deltas.items():
        room = ship.rooms[rid]
        room.oxygen = max(0.0, min(1.0, room.oxygen + delta))


def _suffocate_crew(ship: Ship, dt: float) -> None:
    for crew in ship.crew:
        if not crew.alive:
            continue
        room = crew.current_room()
        if room is None:
            continue
        if room.oxygen >= LOW_OXYGEN_THRESHOLD:
            continue
        damage = SUFFOCATION_HP_PER_SEC * dt * crew.species.suffocation_mult
        crew.hp = max(0.0, crew.hp - damage)
