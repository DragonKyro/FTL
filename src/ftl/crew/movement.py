"""Crew per-tick logic: movement, manning, repair, healing, fire-fighting.

Called once per fixed sim tick from the CombatEngine, for each ship.
This is the heart of the Phase 2 crew loop. It does *not* handle:
- Fire damage to crew (in `ships.hazards`)
- Suffocation damage (in `ships.atmosphere`)
- Crew-vs-crew combat (in `crew.combat`)

The order each tick:
1. Advance every crew along their path.
2. Re-assign manning of each system based on who is now in its room.
3. For non-moving non-fighting crew: do their task (repair, heal,
   fight fire, repair breach).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.crew.crew import CrewState

if TYPE_CHECKING:
    from ftl.crew.crew import Crew
    from ftl.ships.ship import Ship
    from ftl.systems.system import System


# Seconds per tile for a species with move_speed=1.0 and behavior multiplier=1.0.
BASE_TILE_TIME: float = 0.4

# Per-tick rates.
REPAIR_RATE: float = 0.5            # system damage-bars per second per crew
BREACH_REPAIR_RATE: float = 1.0     # breach percent per second per crew
FIRE_FIGHT_RATE: float = 5.0        # fire percent per second per crew
MEDBAY_HEAL_PER_POWER: float = 2.0  # HP/sec per effective power


def tick_movement(ship: Ship, dt: float) -> None:
    for crew in ship.crew:
        if not crew.alive:
            continue
        if crew.state is CrewState.FIGHTING:
            # Crew combat takes priority over movement; let crew.combat decide.
            continue
        _advance_path(crew, ship, dt)

    _reassign_manning(ship)
    _assign_tasks(ship, dt)


def _advance_path(crew: Crew, ship: Ship, dt: float) -> None:
    if not crew.path:
        return
    move_time = _move_time_for(crew)
    crew.move_progress += dt
    while crew.path and crew.move_progress >= move_time:
        next_tile = crew.path[0]
        # Re-check door passability — a door may have been closed since the path was found.
        if crew.current_tile is not None:
            cur = (crew.current_tile.x, crew.current_tile.y)
            nxt = (next_tile.x, next_tile.y)
            if next_tile.room_id != crew.current_tile.room_id:
                door = ship.door_between(cur, nxt)
                if door is not None and not door.passable_for(ship.is_home_team(crew)):
                    crew.path = []
                    crew.move_progress = 0.0
                    return
        crew.current_tile = next_tile
        crew.path.pop(0)
        crew.move_progress -= move_time
        # Recompute move_time in case species speed changes mid-walk (Phase 3+).
        move_time = _move_time_for(crew)
        # Trigger room-enter hook if the room changed.
        room = crew.current_room()
        if room is not None:
            crew.behavior.on_room_enter(crew, room)
    if not crew.path:
        crew.move_progress = 0.0
        if crew.state is CrewState.MOVING:
            crew.state = CrewState.IDLE
    else:
        crew.state = CrewState.MOVING


def _move_time_for(crew: Crew) -> float:
    species_speed = max(0.1, crew.species.move_speed)
    behavior_mul = crew.behavior.move_speed_multiplier(crew)
    return BASE_TILE_TIME / (species_speed * behavior_mul)


def _reassign_manning(ship: Ship) -> None:
    """One crew per system mans it. Boarders don't man enemy systems."""
    # Clear existing assignments.
    for system in ship.systems.values():
        system.manning_crew = None
    # Place first eligible crew in each system's room.
    for system_name, system in ship.systems.items():
        host_room = next(
            (r for r in ship.rooms.values() if r.system is system),
            None,
        )
        if host_room is None:
            continue
        for crew in ship.crew:
            if not crew.alive:
                continue
            if crew.home_ship is not ship:
                continue  # boarders don't man
            if crew.current_tile is None:
                continue
            if crew.current_tile.room_id == host_room.id:
                system.manning_crew = crew
                break


def _assign_tasks(ship: Ship, dt: float) -> None:
    """Pick a task per crew member and apply its per-tick effect."""
    for crew in ship.crew:
        if not crew.alive:
            continue
        if crew.path:
            continue  # already MOVING
        if crew.state is CrewState.FIGHTING:
            continue
        room = crew.current_room()
        if room is None:
            crew.state = CrewState.IDLE
            continue
        # Boarders skip friendly tasks; they only get to fight on their tile.
        if crew.home_ship is not ship:
            crew.state = CrewState.IDLE
            continue
        # Fire takes priority — it hurts everyone in the room.
        if room.fire > 0:
            crew.state = CrewState.FIGHTING_FIRE
            room.fire = max(0, room.fire - FIRE_FIGHT_RATE * dt)
            continue
        # Breach repair next.
        if room.breach > 0:
            crew.state = CrewState.REPAIRING
            room.breach = max(0, room.breach - BREACH_REPAIR_RATE * crew.species.repair_speed * dt)
            continue
        # Medbay healing.
        if (
            room.system is not None
            and room.system.name == "medbay"
            and crew.hp < crew.max_hp
            and room.system.is_operational
        ):
            crew.state = CrewState.HEALING
            crew.hp = min(
                float(crew.max_hp),
                crew.hp + MEDBAY_HEAL_PER_POWER * room.system.effective_power * dt,
            )
            continue
        # Manning takes precedence over repair when both apply.
        if room.system is not None and room.system.manning_crew is crew:
            if room.system.damage > 0:
                # Manning + repair simultaneously: tick repair.
                _tick_repair(crew, room.system, dt)
                crew.state = CrewState.REPAIRING
            else:
                crew.state = CrewState.MANNING
            continue
        # Plain repair (system damaged, this crew is not the manner).
        if room.system is not None and room.system.damage > 0:
            _tick_repair(crew, room.system, dt)
            crew.state = CrewState.REPAIRING
            continue
        crew.state = CrewState.IDLE


def _tick_repair(crew: Crew, system: System, dt: float) -> None:
    """Apply repair to a system, with per-crew sub-bar accumulation."""
    crew.repair_accum += REPAIR_RATE * crew.species.repair_speed * dt
    while crew.repair_accum >= 1.0 and system.damage > 0:
        system.damage -= 1
        crew.repair_accum -= 1.0
    if system.damage == 0:
        crew.repair_accum = 0.0
