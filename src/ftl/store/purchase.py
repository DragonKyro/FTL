"""Store purchase actions — mutate the active Run + player ship."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.augments.factory import augment_from_def
from ftl.crew.crew import Crew
from ftl.crew.species import Species
from ftl.crew.species_behaviors import behavior_for
from ftl.store.inventory import HIRE_COST, REPAIR_UNIT_COST
from ftl.weapons.weapon import Weapon, WeaponStats

if TYPE_CHECKING:
    from ftl.core.game import Run
    from ftl.data.schemas import (
        AugmentDef,
        DroneDef,
        SpeciesDef,
        WeaponDef,
    )
    from ftl.store.inventory import SystemUpgradeOffer


def can_afford(run: Run, cost: int) -> bool:
    return run.scrap >= cost


def buy_weapon(run: Run, weapon_def: WeaponDef) -> bool:
    if run.player_ship is None or not can_afford(run, weapon_def.cost):
        return False
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
        beam_room_damage=weapon_def.beam_room_damage,
        projectile_count=weapon_def.projectile_count,
        missile_cost=weapon_def.missile_cost,
        power_required=weapon_def.power_required,
        cost=weapon_def.cost,
        sprite_key=weapon_def.sprite_key,
        sfx_key=weapon_def.sfx_key,
    )
    run.scrap -= weapon_def.cost
    run.player_ship.weapons.append(Weapon(stats))
    return True


def buy_drone(run: Run, drone_def: DroneDef) -> bool:
    if run.player_ship is None or not can_afford(run, drone_def.cost):
        return False
    from ftl.drones.drone import Drone, DroneStats

    stats = DroneStats(
        id=drone_def.id,
        name=drone_def.name,
        family=drone_def.family,
        power_required=drone_def.power_required,
        speed=drone_def.speed,
        damage=drone_def.damage,
        drone_parts_cost=drone_def.drone_parts_cost,
    )
    run.scrap -= drone_def.cost
    run.player_ship.drones.append(Drone(stats))
    return True


def buy_augment(run: Run, aug_def: AugmentDef) -> bool:
    if run.player_ship is None or not can_afford(run, aug_def.cost):
        return False
    augment = augment_from_def(aug_def)
    if augment is None:
        return False
    run.scrap -= aug_def.cost
    augment.install(run.player_ship)
    run.augments.append(augment)
    return True


def buy_repair(run: Run, hp: int) -> int:
    """Buy up to `hp` hull repair. Returns the number of HP actually repaired."""
    if run.player_ship is None or hp <= 0:
        return 0
    hull = run.player_ship.hull
    needed = hull.maximum - hull.current
    actual = min(hp, needed, run.scrap // REPAIR_UNIT_COST)
    if actual <= 0:
        return 0
    run.scrap -= actual * REPAIR_UNIT_COST
    hull.repair(actual)
    return actual


def hire_crew(run: Run, species_def: SpeciesDef) -> bool:
    if run.player_ship is None or not can_afford(run, HIRE_COST):
        return False
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
    crew = Crew(
        name=f"Hire-{len(run.player_ship.crew) + 1}",
        species=species,
        team="player",
        behavior=behavior_for(species_def.id),
    )
    crew.home_ship = run.player_ship
    crew.current_ship = run.player_ship
    # Place on first available room with tiles.
    for room in run.player_ship.rooms.values():
        if room.tiles:
            crew.current_tile = room.tiles[0]
            break
    run.scrap -= HIRE_COST
    run.player_ship.crew.append(crew)
    return True


def upgrade_system(run: Run, offer: SystemUpgradeOffer) -> bool:
    if run.player_ship is None or not can_afford(run, offer.cost):
        return False
    system = run.player_ship.systems.get(offer.system_name)
    if system is None or system.level >= system.max_power:
        return False
    system.level = offer.new_level
    run.scrap -= offer.cost
    return True
