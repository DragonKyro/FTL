"""Ship base class + Player/Enemy subclasses.

A Ship owns a hull, a layout (rooms + tile grid + doors), installed
systems, crew, and loadout (weapons + drones). It's a Tickable: ticking
a ship ticks all its constituents.

Phase 2 adds:
- `tile_graph: dict[(x,y), Tile]` populated from `build_layout`
- `doors: list[Door]` inferred between adjacent rooms
- `crew_aboard` aliased to `crew` — boarders end up here when teleporters
  flip ownership
- Reactor power is no longer a fixed int: `max_reactor_power` is a
  property that adds `crew_power_bonus` (Halene contributions) on top
  of `base_max_reactor_power`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.config import DEFAULT_HULL_HP
from ftl.crew.crew import Crew
from ftl.crew.species import Species
from ftl.crew.species_behaviors import behavior_for
from ftl.ships.hull import Hull
from ftl.ships.layout import build_layout
from ftl.ships.room import Room
from ftl.systems.artillery import ArtillerySystem
from ftl.systems.battery import BatterySystem
from ftl.systems.cloaking import CloakingSystem
from ftl.systems.clonebay import ClonebaySystem
from ftl.systems.doors import DoorsSystem
from ftl.systems.drone_control import DroneControlSystem
from ftl.systems.engines import EnginesSystem
from ftl.systems.hacking import HackingSystem
from ftl.systems.medbay import MedbaySystem
from ftl.systems.mind_control import MindControlSystem
from ftl.systems.oxygen import OxygenSystem
from ftl.systems.piloting import PilotingSystem
from ftl.systems.sensors import SensorsSystem
from ftl.systems.shields import ShieldsSystem
from ftl.systems.system import System
from ftl.systems.teleporter import TeleporterSystem
from ftl.systems.weapons import WeaponsSystem
from ftl.drones.drone import Drone, DroneStats
from ftl.weapons.laser import LaserWeapon
from ftl.weapons.missile import MissileWeapon
from ftl.weapons.weapon import Weapon, WeaponStats

if TYPE_CHECKING:
    from ftl.data.registry import Registry
    from ftl.data.schemas import ShipDef
    from ftl.drones.drone import Drone
    from ftl.ships.door import Door
    from ftl.ships.tile import Tile

# Phase-2 placeholder crew names. Replaced by name generation in a later phase.
_CREW_NAME_POOL: tuple[str, ...] = (
    "Sera", "Renn", "Korr", "Aldine", "Yvet", "Tovin",
    "Mara", "Vex", "Lia", "Sten", "Pava", "Nyx",
)

# Preferred placement order — first crew goes to piloting room, etc.
_PLACEMENT_PREFERENCE: tuple[str, ...] = (
    "piloting", "weapons", "engines", "shields", "medbay", "teleporter", "oxygen",
)

# System name -> concrete System subclass.
_SYSTEM_FACTORIES: dict[str, type[System]] = {
    "weapons": WeaponsSystem,
    "shields": ShieldsSystem,
    "engines": EnginesSystem,
    "piloting": PilotingSystem,
    "cloaking": CloakingSystem,
    "medbay": MedbaySystem,
    "oxygen": OxygenSystem,
    "teleporter": TeleporterSystem,
    "sensors": SensorsSystem,
    "doors": DoorsSystem,
    "drone_control": DroneControlSystem,
    "hacking": HackingSystem,
    "mind_control": MindControlSystem,
    "battery": BatterySystem,
    "clonebay": ClonebaySystem,
    "artillery": ArtillerySystem,
}

# Weapon family -> concrete Weapon class.
_WEAPON_FAMILIES: dict[str, type[Weapon]] = {
    "laser": LaserWeapon,
    "missile": MissileWeapon,
}


class Ship:
    """Base ship. Holds layout, systems, crew, and loadout."""

    _team: str = "neutral"

    def __init__(
        self,
        name: str = "Unnamed",
        max_hull: int = DEFAULT_HULL_HP,
        max_reactor_power: int = 5,
    ) -> None:
        self.name = name
        self.hull = Hull(current=max_hull, maximum=max_hull)
        self.base_max_reactor_power: int = max_reactor_power
        self.crew_power_bonus: int = 0  # recomputed each tick by species behavior
        self.rooms: dict[str, Room] = {}
        self.doors: dict[str, Door] = {}
        self.tile_graph: dict[tuple[int, int], Tile] = {}
        self.systems: dict[str, System] = {}
        self.crew: list[Crew] = []
        self.weapons: list[Weapon] = []
        self.drones: list[Drone] = []
        # Set per-tick by CombatEngine: when True, opponent is cloaked
        # and our weapons can't charge.
        self.cloak_freeze: bool = False

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
    def max_reactor_power(self) -> int:
        return self.base_max_reactor_power + self.crew_power_bonus + self.battery_bonus

    @property
    def battery_bonus(self) -> int:
        battery = self.systems.get("battery")
        if isinstance(battery, BatterySystem):
            return battery.power_bonus
        return 0

    @property
    def is_cloaked(self) -> bool:
        cloak = self.systems.get("cloaking")
        return isinstance(cloak, CloakingSystem) and cloak.is_active

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
    def medbay(self) -> MedbaySystem | None:
        s = self.systems.get("medbay")
        return s if isinstance(s, MedbaySystem) else None

    @property
    def oxygen_system(self) -> OxygenSystem | None:
        s = self.systems.get("oxygen")
        return s if isinstance(s, OxygenSystem) else None

    @property
    def teleporter(self) -> TeleporterSystem | None:
        s = self.systems.get("teleporter")
        return s if isinstance(s, TeleporterSystem) else None

    @property
    def power_used(self) -> int:
        return sum(s.current_power for s in self.systems.values())

    @property
    def power_available(self) -> int:
        return self.max_reactor_power - self.power_used

    def is_home_team(self, crew: Crew) -> bool:
        return crew.home_ship is self

    def door_between(
        self, coord_a: tuple[int, int], coord_b: tuple[int, int]
    ) -> Door | None:
        for door in self.doors.values():
            if door.connects_tiles(coord_a, coord_b):
                return door
        return None

    def room_for_tile(self, tile: Tile) -> Room | None:
        return self.rooms.get(tile.room_id)

    def evasion_chance(self) -> float:
        base = 0.0
        engines = self.engines
        if engines is not None:
            base = engines.evasion_chance
            if engines.manning_crew is not None:
                base += 0.05
        piloting = self.systems.get("piloting")
        if piloting is not None and piloting.manning_crew is not None:
            base += 0.05
        cap = 0.6
        if self.is_cloaked:
            base += 0.6
            cap = 0.95
        return min(cap, base)

    # --- ticking -------------------------------------------------------------

    def tick(self, dt: float) -> None:
        # Imported lazily to avoid a circular import (atmosphere/hazards/
        # movement all reference Ship via TYPE_CHECKING).
        from ftl.crew import movement as crew_movement
        from ftl.ships import atmosphere, hazards

        # 1. Reset crew_power_bonus; species behaviors re-accumulate it.
        self.crew_power_bonus = 0
        # 2. Atmosphere + hazards: update room state (oxygen, fire, breach).
        atmosphere.tick_atmosphere(self, dt)
        hazards.tick_hazards(self, dt)
        # 3. Crew movement + manning + repair + healing + fire-fighting.
        crew_movement.tick_movement(self, dt)
        # 4. Per-crew personal tick (species behaviors run here).
        for crew_member in self.crew:
            if crew_member.alive:
                crew_member.tick(dt)
        # 5. Systems tick (cooldowns, shield recharge, ion decay, etc.).
        for system in self.systems.values():
            system.tick(dt)
        # 6. Weapons charge — apply manning bonus from the WeaponsSystem.
        weapons_charge_mult = self._weapons_charge_multiplier()
        for weapon in self.weapons:
            weapon.tick(dt * weapons_charge_mult)
        # 7. Drones — ticked from CombatEngine (need opponent reference).

    def _weapons_charge_multiplier(self) -> float:
        if self.cloak_freeze:
            return 0.0
        ws = self.weapons_system
        if ws is None or ws.manning_crew is None:
            return 1.0
        # -10% charge time = +1/0.9 ≈ +11.1% charge rate.
        return 1.0 / 0.9

    # --- factory -------------------------------------------------------------

    @classmethod
    def from_def(
        cls,
        ship_def: ShipDef,
        registry: Registry,
    ) -> Ship:
        """Build a Ship from a canonical ShipDef + Registry."""
        ship = cls(
            name=ship_def.name,
            max_hull=ship_def.max_hull,
            max_reactor_power=ship_def.max_reactor_power,
        )

        # Build tile grid + inferred doors.
        tiles_by_room, doors = build_layout(ship_def)
        for room_layout in ship_def.rooms:
            room = Room(id=room_layout.id, tiles=tiles_by_room[room_layout.id])
            ship.add_room(room)
            for tile in room.tiles:
                ship.tile_graph[(tile.x, tile.y)] = tile

        for door in doors:
            ship.add_door(door)

        # Systems — install into the room that names them.
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

        # Drones.
        for drone_id in ship_def.starting_drones:
            drone_def = registry.drones.get(drone_id)
            if drone_def is None:
                continue
            drone_stats = DroneStats(
                id=drone_def.id,
                name=drone_def.name,
                family=drone_def.family,
                power_required=drone_def.power_required,
                speed=drone_def.speed,
                damage=drone_def.damage,
                drone_parts_cost=drone_def.drone_parts_cost,
            )
            ship.drones.append(Drone(drone_stats))

        # Doors: if the ship has a doors system, raise every door's max_hp
        # accordingly.
        doors_system = ship.systems.get("doors")
        if doors_system is not None:
            base_hp = 4 + 4 * (doors_system.level - 1)
            for door in ship.doors.values():
                door.max_hp = base_hp
                door.hp = base_hp

        # Weapons.
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

        # Crew.
        _attach_crew_from_def(ship, ship_def, registry, cls._team)

        return ship


def _attach_crew_from_def(
    ship: Ship, ship_def: ShipDef, registry: Registry, team: str
) -> None:
    """Create crew from `ship_def.starting_crew` and place them on tiles."""
    placement_rooms = _preferred_placement_rooms(ship)
    occupied: set[str] = set()
    for idx, species_id in enumerate(ship_def.starting_crew):
        species_def = registry.species.get(species_id)
        if species_def is None:
            continue
        species = Species(
            id=species_def.id,
            name=species_def.name,
            max_hp=species_def.max_hp,
            move_speed=species_def.move_speed,
            damage_mult=species_def.damage_mult,
            fire_resistance=species_def.fire_resistance,
            suffocation_mult=species_def.suffocation_mult,
            repair_speed=species_def.repair_speed,
            combat_damage=species_def.combat_damage,
            traits=list(species_def.traits),
        )
        crew_name = _CREW_NAME_POOL[idx % len(_CREW_NAME_POOL)]
        crew = Crew(
            name=crew_name,
            species=species,
            team=team,
            behavior=behavior_for(species_id),
        )
        crew.home_ship = ship
        crew.current_ship = ship
        _place_crew_on_tile(crew, ship, placement_rooms, occupied)
        ship.crew.append(crew)


def _preferred_placement_rooms(ship: Ship) -> list[str]:
    ordered: list[str] = []
    for pref in _PLACEMENT_PREFERENCE:
        for room in ship.rooms.values():
            if room.system is not None and room.system.name == pref:
                if room.id not in ordered:
                    ordered.append(room.id)
                break
    # add any leftover rooms so we never fail to place.
    for room in ship.rooms.values():
        if room.id not in ordered:
            ordered.append(room.id)
    return ordered


def _place_crew_on_tile(
    crew: Crew, ship: Ship, placement_rooms: list[str], occupied: set[str]
) -> None:
    for room_id in placement_rooms:
        if room_id in occupied:
            continue
        room = ship.rooms[room_id]
        if not room.tiles:
            continue
        crew.current_tile = room.tiles[0]
        occupied.add(room_id)
        return
    # Fallback: any room with tiles (allow stacking).
    for room in ship.rooms.values():
        if room.tiles:
            crew.current_tile = room.tiles[0]
            return


class PlayerShip(Ship):
    """Ship under player control."""

    _team: str = "player"


class EnemyShip(Ship):
    """Ship under AI control."""

    _team: str = "enemy"
