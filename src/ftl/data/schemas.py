"""Pydantic schemas for YAML content.

Every content category (weapons, ships, species, ...) has a schema. The
loader picks the schema based on which `content/` or `story/` subdirectory
the YAML file lives in. New schemas register themselves in `CONTENT_SCHEMAS`
or `STORY_SCHEMAS` below.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ContentDef(BaseModel):
    """Base for all content definitions."""

    id: str
    name: str
    description: str = ""


# --- Weapons -----------------------------------------------------------------

WeaponFamily = Literal["beam", "laser", "missile", "bomb", "ion", "flak"]


class WeaponDef(ContentDef):
    family: WeaponFamily
    damage: int = 0
    charge_time: float = 10.0
    shield_pierce: int = 0
    breach_chance: float = 0.0
    fire_chance: float = 0.0
    stun_seconds: float = 0.0
    ion_damage: int = 0
    crew_damage: int = 0
    system_damage: int = 0
    beam_length: int = 0
    beam_room_damage: int = 0
    projectile_count: int = 1
    missile_cost: int = 0
    power_required: int = 1
    cost: int = 50
    sprite_key: str = ""
    sfx_key: str = ""


# --- Drones ------------------------------------------------------------------

DroneFamily = Literal[
    "combat", "defense", "boarding", "repair", "hacking", "anti_personnel"
]


class DroneDef(ContentDef):
    family: DroneFamily
    power_required: int = 1
    speed: float = 1.0
    damage: int = 0
    drone_parts_cost: int = 1
    cost: int = 50


# --- Augments ----------------------------------------------------------------


class AugmentDef(ContentDef):
    effect_id: str = ""
    value: float = 0.0
    rarity: int = 1
    cost: int = 50


# --- Species -----------------------------------------------------------------


class SpeciesDef(ContentDef):
    max_hp: int = 100
    move_speed: float = 1.0
    damage_mult: float = 1.0
    fire_resistance: float = 0.0
    suffocation_mult: float = 1.0
    repair_speed: float = 1.0
    combat_damage: float = 1.0
    traits: list[str] = Field(default_factory=list)


# --- Systems -----------------------------------------------------------------


class SystemDef(ContentDef):
    base_power_cost: int = 1
    max_level: int = 8
    max_power: int = 8
    install_cost: int = 50


# --- Ships -------------------------------------------------------------------


class RoomLayout(BaseModel):
    id: str
    x: int
    y: int
    width: int = 1
    height: int = 1
    system: str | None = None


class ShipDef(ContentDef):
    rooms: list[RoomLayout] = Field(default_factory=list)
    starting_systems: list[str] = Field(default_factory=list)
    starting_weapons: list[str] = Field(default_factory=list)
    starting_drones: list[str] = Field(default_factory=list)
    starting_augments: list[str] = Field(default_factory=list)
    starting_crew: list[str] = Field(default_factory=list)
    max_hull: int = 30
    max_reactor_power: int = 5
    starting_missiles: int = 0


# --- Factions ----------------------------------------------------------------


class FactionDef(ContentDef):
    hostile_to: list[str] = Field(default_factory=list)


# --- Sectors -----------------------------------------------------------------


class SectorDef(ContentDef):
    faction: str = ""
    theme: str = ""
    event_pools: list[str] = Field(default_factory=list)
    min_beacons: int = 15
    max_beacons: int = 25


# --- Events ------------------------------------------------------------------


class EventChoiceDef(BaseModel):
    text: str
    outcome_id: str | None = None
    requires_species: str | None = None  # only show if this species is aboard


class OutcomeDef(BaseModel):
    text: str = ""
    scrap: int = 0
    fuel: int = 0
    missiles: int = 0
    drone_parts: int = 0
    hull_damage: int = 0
    hull_repair: int = 0
    starts_combat: bool = False
    enemy_ship_id: str | None = None
    set_flags: list[str] = Field(default_factory=list)
    clear_flags: list[str] = Field(default_factory=list)
    recruit_species_id: str | None = None


class EventDef(ContentDef):
    text: str = ""
    choices: list[EventChoiceDef] = Field(default_factory=list)
    outcomes: dict[str, OutcomeDef] = Field(default_factory=dict)
    triggers: list[str] = Field(default_factory=list)
    species_locked: str | None = None  # only spawn if a crew of this species is aboard


# --- Scenarios ---------------------------------------------------------------


class ScenarioDef(ContentDef):
    """A starting-run config: which ships fight, which AI profile drives the enemy."""

    player_ship: str
    enemy_ship: str
    ai_profile: str = "skiff"
    player_missiles: int | None = None
    enemy_missiles: int | None = None


# --- Registries --------------------------------------------------------------

CONTENT_SCHEMAS: dict[str, type[ContentDef]] = {
    "weapons": WeaponDef,
    "drones": DroneDef,
    "augments": AugmentDef,
    "species": SpeciesDef,
    "systems": SystemDef,
    "ships": ShipDef,
    "factions": FactionDef,
    "sectors": SectorDef,
    "scenarios": ScenarioDef,
}

STORY_SCHEMAS: dict[str, type[ContentDef]] = {
    "events": EventDef,
}
