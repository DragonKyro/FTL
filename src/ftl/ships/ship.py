"""Ship base class + Player/Enemy subclasses.

A Ship owns a hull, a layout (rooms + doors), installed systems, crew, and
loadout (weapons + drones). It's a Tickable: ticking a ship ticks all its
constituents.

Phase 1 adds:
- `max_reactor_power` field
- `from_def(...)` factory that wires up a Ship from a ShipDef + Registry
- `evasion_chance()` derived from engines
- `shields` / `engines` / `weapons_system` typed accessors
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.config import DEFAULT_HULL_HP
from ftl.ships.hull import Hull
from ftl.ships.room import Room
from ftl.systems.cloaking import CloakingSystem
from ftl.systems.engines import EnginesSystem
from ftl.systems.piloting import PilotingSystem
from ftl.systems.shields import ShieldsSystem
from ftl.systems.system import System
from ftl.systems.weapons import WeaponsSystem
from ftl.weapons.laser import LaserWeapon
from ftl.weapons.missile import MissileWeapon
from ftl.weapons.weapon import Weapon, WeaponStats

if TYPE_CHECKING:
    from ftl.crew.crew import Crew
    from ftl.data.registry import Registry
    from ftl.data.schemas import ShipDef
    from ftl.drones.drone import Drone
    from ftl.ships.door import Door

# Maps "system name" (the canonical key) -> the concrete System subclass that
# implements it. New systems register here.
_SYSTEM_FACTORIES: dict[str, type[System]] = {
    "weapons": WeaponsSystem,
    "shields": ShieldsSystem,
    "engines": EnginesSystem,
    "piloting": PilotingSystem,
    "cloaking": CloakingSystem,
}

# Maps weapon family -> concrete Weapon class.
_WEAPON_FAMILIES: dict[str, type[Weapon]] = {
    "laser": LaserWeapon,
    "missile": MissileWeapon,
}


class Ship:
    """Base ship. Holds layout, systems, crew, and loadout."""

    def __init__(
        self,
        name: str = "Unnamed",
        max_hull: int = DEFAULT_HULL_HP,
        max_reactor_power: int = 5,
    ) -> None:
        self.name = name
        self.hull = Hull(current=max_hull, maximum=max_hull)
        self.max_reactor_power: int = max_reactor_power
        self.rooms: dict[str, Room] = {}
        self.doors: dict[str, Door] = {}
        self.systems: dict[str, System] = {}
        self.crew: list[Crew] = []
        self.weapons: list[Weapon] = []
        self.drones: list[Drone] = []

    # --- construction --------------------------------------------------------

    def add_room(self, room: Room) -> None:
        self.rooms[room.id] = room

    def add_door(self, door: Door) -> None:
        self.doors[door.id] = door

    def install_system(self, system: System, room_id: str) -> None:
        self.systems[system.name] = system
        if room_id in self.rooms:
            self.rooms[room_id].system = system

    # --- accessors -----------------------------------------------------------

    @property
    def shields(self) -> ShieldsSystem | None:
        s = self.systems.get("shields")
        return s if isinstance(s, ShieldsSystem) else None

    @property
    def engines(self) -> EnginesSystem | None:
        s = self.systems.get("engines")
        return s if isinstance(s, EnginesSystem) else None

    @property
    def weapons_system(self) -> WeaponsSystem | None:
        s = self.systems.get("weapons")
        return s if isinstance(s, WeaponsSystem) else None

    @property
    def power_used(self) -> int:
        return sum(s.current_power for s in self.systems.values())

    @property
    def power_available(self) -> int:
        return self.max_reactor_power - self.power_used

    def evasion_chance(self) -> float:
        engines = self.engines
        if engines is None:
            return 0.0
        return engines.evasion_chance

    # --- ticking -------------------------------------------------------------

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

    # --- factory -------------------------------------------------------------

    @classmethod
    def from_def(
        cls,
        ship_def: ShipDef,
        registry: Registry,
    ) -> Ship:
        """Build a Ship from a canonical ShipDef + Registry.

        Rooms come from the layout. Systems are installed in the first room
        that lists them. Weapons are looked up in the registry; an unknown
        weapon id raises KeyError.
        """
        ship = cls(
            name=ship_def.name,
            max_hull=ship_def.max_hull,
            max_reactor_power=ship_def.max_reactor_power,
        )

        # rooms first
        for room_layout in ship_def.rooms:
            ship.add_room(Room(id=room_layout.id))

        # systems — install into the room that names them
        for system_name in ship_def.starting_systems:
            factory = _SYSTEM_FACTORIES.get(system_name)
            if factory is None:
                continue
            host_room = next(
                (rl for rl in ship_def.rooms if rl.system == system_name),
                None,
            )
            if host_room is None:
                continue
            ship.install_system(factory(), host_room.id)

        # weapons
        for weapon_id in ship_def.starting_weapons:
            weapon_def = registry.weapons[weapon_id]
            stats = WeaponStats(
                id=weapon_def.id,
                name=weapon_def.name,
                family=weapon_def.family,
                damage=weapon_def.damage,
                charge_time=weapon_def.charge_time,
                shield_pierce=weapon_def.shield_pierce,
                breach_chance=weapon_def.breach_chance,
                fire_chance=weapon_def.fire_chance,
                stun_seconds=weapon_def.stun_seconds,
                ion_damage=weapon_def.ion_damage,
                crew_damage=weapon_def.crew_damage,
                system_damage=weapon_def.system_damage,
                beam_length=weapon_def.beam_length,
                missile_cost=weapon_def.missile_cost,
                power_required=weapon_def.power_required,
                sprite_key=weapon_def.sprite_key,
                sfx_key=weapon_def.sfx_key,
            )
            weapon_cls = _WEAPON_FAMILIES.get(weapon_def.family, Weapon)
            ship.weapons.append(weapon_cls(stats))

        return ship


class PlayerShip(Ship):
    """Ship under player control."""


class EnemyShip(Ship):
    """Ship under AI control."""
