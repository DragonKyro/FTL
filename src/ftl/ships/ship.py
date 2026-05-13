"""Ship base class + Player/Enemy subclasses.

A Ship owns a hull, a layout (rooms + doors), installed systems, crew, and
loadout (weapons + drones). It's a Tickable: ticking a ship ticks all its
constituents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.config import DEFAULT_HULL_HP
from ftl.ships.hull import Hull

if TYPE_CHECKING:
    from ftl.crew.crew import Crew
    from ftl.drones.drone import Drone
    from ftl.ships.door import Door
    from ftl.ships.room import Room
    from ftl.systems.system import System
    from ftl.weapons.weapon import Weapon


class Ship:
    """Base ship. Holds layout, systems, crew, and loadout."""

    def __init__(self, name: str = "Unnamed", max_hull: int = DEFAULT_HULL_HP) -> None:
        self.name = name
        self.hull = Hull(current=max_hull, maximum=max_hull)
        self.rooms: dict[str, Room] = {}
        self.doors: dict[str, Door] = {}
        self.systems: dict[str, System] = {}
        self.crew: list[Crew] = []
        self.weapons: list[Weapon] = []
        self.drones: list[Drone] = []
        self.reactor_power: int = 8

    def add_room(self, room: Room) -> None:
        self.rooms[room.id] = room

    def add_door(self, door: Door) -> None:
        self.doors[door.id] = door

    def install_system(self, system: System, room_id: str) -> None:
        self.systems[system.name] = system
        if room_id in self.rooms:
            self.rooms[room_id].system = system

    def tick(self, dt: float) -> None:
        for room in self.rooms.values():
            room.tick(dt)
        for system in self.systems.values():
            system.tick(dt)
        for weapon in self.weapons:
            weapon.tick(dt)
        for drone in self.drones:
            drone.tick(dt)
        for crew_member in self.crew:
            crew_member.tick(dt)


class PlayerShip(Ship):
    """Ship under player control."""


class EnemyShip(Ship):
    """Ship under AI control."""
