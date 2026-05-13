"""JSON-based save/load for an in-progress Helixfall Run.

Saves are only meaningful **between encounters** — on the star map.
At that point the player ship is in a quiescent state: no projectiles
in flight, no active combat engine, no animated crew movement. We
serialise the small set of fields that distinguish two otherwise
equivalent runs:

- scenario / ship choice (so the ship can be reconstructed from YAML)
- sector index + chain + current beacon
- the procedurally-generated star map (so the player resumes the same
  layout, not a freshly-rolled one)
- resources (scrap / fuel / missiles / drone parts)
- hull current/max
- weapon / drone / augment loadout (ids)
- per-crew hp + skill XP
- per-system level (upgrades purchased)
- story flags
- RNG seed (so future random pulls stay deterministic)

Things we **don't** persist (because the save is taken on the star map
and these reset between encounters anyway):
- crew positions (re-placed at their preferred rooms on load)
- room oxygen / fire / breach
- system damage / ion charge / hacking state
- door open/forced states

If a save fails to load (file missing, schema mismatch) the caller
sees `None` and can fall back to a fresh run.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ftl.config import SAVES_DIR
from ftl.core.game import Game, Run
from ftl.core.rng import RNG
from ftl.map.beacon import Beacon
from ftl.map.star_map import StarMap
from ftl.ships.ship import PlayerShip


SAVE_VERSION: int = 1
SAVE_EXT: str = ".save.json"


# ---------------- Slot listing -------------------------------------------


@dataclass
class SaveSlot:
    path: Path
    name: str
    summary: str
    saved_at: str
    scenario_id: str | None
    sector_index: int


def saves_dir() -> Path:
    SAVES_DIR.mkdir(parents=True, exist_ok=True)
    return SAVES_DIR


def list_saves() -> list[SaveSlot]:
    """Return all .save.json files sorted by most-recently-modified."""
    root = saves_dir()
    out: list[SaveSlot] = []
    for path in sorted(root.glob(f"*{SAVE_EXT}"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        out.append(
            SaveSlot(
                path=path,
                name=path.stem.removesuffix(".save"),
                summary=data.get("summary", "(unknown)"),
                saved_at=data.get("saved_at", "?"),
                scenario_id=data.get("scenario_id"),
                sector_index=int(data.get("sector_index", 0)),
            )
        )
    return out


def quick_slot_name() -> str:
    """Stable name for the auto / quick-save slot."""
    return "quicksave"


# ---------------- Save ---------------------------------------------------


def save_run(run: Run, slot_name: str = "quicksave") -> Path:
    """Serialize the active run to `<slot_name>.save.json`."""
    if run.player_ship is None or run.star_map is None:
        raise ValueError("Cannot save: run has no player_ship or no star_map.")
    data = _serialize_run(run)
    root = saves_dir()
    safe = "".join(c for c in slot_name if c.isalnum() or c in "_-") or "save"
    path = root / f"{safe}{SAVE_EXT}"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def _serialize_run(run: Run) -> dict[str, Any]:
    ps: PlayerShip = run.player_ship  # type: ignore[assignment]
    sm: StarMap = run.star_map  # type: ignore[assignment]
    return {
        "version": SAVE_VERSION,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "summary": _summary(run),
        "scenario_id": run.scenario_id,
        "player_ship_id": _player_ship_id(run),
        "rng_seed": run.rng.seed,
        "sector_index": run.sector_index,
        "sectors_total": run.sectors_total,
        "sector_chain": list(run.sector_chain),
        "current_beacon_id": run.current_beacon_id,
        "star_map": _serialize_star_map(sm),
        "resources": {
            "scrap": run.scrap,
            "fuel": run.fuel,
            "missiles": run.missiles,
            "drone_parts": run.drone_parts,
        },
        "hull": {"current": ps.hull.current, "max": ps.hull.maximum},
        "augments": [aug.stats.id for aug in run.augments],
        "weapons": [
            {"id": w.stats.id, "powered": w.powered}
            for w in ps.weapons
        ],
        "drones": [d.stats.id for d in ps.drones],
        "crew": [
            {
                "name": c.name,
                "species": c.species.id,
                "hp": c.hp,
                "skills": {s.value: float(xp) for s, xp in c.skills.items()},
            }
            for c in ps.crew
            if c.alive and c.home_ship is ps
        ],
        "system_levels": {
            name: int(system.level) for name, system in ps.systems.items()
        },
        "story_flags": sorted(run.story_flags),
        "difficulty": run.difficulty,
    }


def _serialize_star_map(sm: StarMap) -> dict[str, Any]:
    return {
        "sector_id": sm.sector_id,
        "current_beacon": sm.current_beacon,
        "exit_beacon": sm.exit_beacon,
        "beacons": [
            {
                "id": b.id,
                "x": b.x,
                "y": b.y,
                "sector_id": b.sector_id,
                "visited": b.visited,
                "has_store": b.has_store,
                "has_distress": b.has_distress,
                "has_quest": b.has_quest,
                "encounter_id": b.encounter_id,
                "connections": list(b.connections),
            }
            for b in sm.beacons.values()
        ],
    }


def _player_ship_id(run: Run) -> str:
    if run.scenario_id is not None:
        return run.scenario_id  # not actually a ship id — used only as a fallback hint
    if run.player_ship is None:
        return "wayfarer"
    return "pilgrim" if run.player_ship.name.lower().startswith("pilgrim") else "wayfarer"


def _summary(run: Run) -> str:
    ship_name = run.player_ship.name if run.player_ship else "?"
    hull = run.player_ship.hull if run.player_ship else None
    hull_str = f"{hull.current}/{hull.maximum}" if hull else "?"
    sector = run.sector_index + 1
    return f"{ship_name} — Sector {sector}/{run.sectors_total} — Hull {hull_str} — Scrap {run.scrap}"


# ---------------- Load ---------------------------------------------------


def load_run(slot_path: Path, game: Game) -> Run | None:
    """Reconstruct a Run from a save file, install on `game.run`."""
    try:
        data = json.loads(slot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if int(data.get("version", 0)) != SAVE_VERSION:
        return None
    try:
        return _deserialize_run(data, game)
    except (KeyError, ValueError, TypeError):
        return None


def _deserialize_run(data: dict[str, Any], game: Game) -> Run:
    # Reset game state then build a fresh Run with the saved seed.
    game.new_run(seed=int(data["rng_seed"]))
    run: Run = game.run  # type: ignore[assignment]

    # Resolve the player ship id: prefer scenario lookup (preferred path),
    # fall back to the saved player_ship_id heuristic.
    scenario_id = data.get("scenario_id")
    player_ship_id = "wayfarer"
    if scenario_id and scenario_id in game.registry.scenarios:
        player_ship_id = game.registry.scenarios[scenario_id].player_ship
    else:
        guess = data.get("player_ship_id", "wayfarer")
        if guess in game.registry.ships:
            player_ship_id = guess

    ship_def = game.registry.ships[player_ship_id]
    run.scenario_id = scenario_id
    run.player_ship = PlayerShip.from_def(ship_def, game.registry)
    run.sector_chain = list(data.get("sector_chain", []))
    run.sector_index = int(data.get("sector_index", 0))
    run.sectors_total = int(data.get("sectors_total", 3))
    run.current_beacon_id = data.get("current_beacon_id")
    run.story_flags = set(data.get("story_flags", []))
    run.difficulty = str(data.get("difficulty", "normal"))

    resources = data.get("resources", {})
    run.scrap = int(resources.get("scrap", 0))
    run.fuel = int(resources.get("fuel", 0))
    run.missiles = int(resources.get("missiles", 0))
    run.drone_parts = int(resources.get("drone_parts", 0))

    # Restore in this order:
    #   1. loadout / systems / crew (independent of hull bonus)
    #   2. augments (which may mutate hull.maximum / drone_power_discount / etc.)
    #   3. hull (override augment-derived current/max with saved values)
    #   4. star map
    _restore_loadout(run, data, game)
    _restore_system_levels(run, data)
    _restore_crew_state(run, data)
    _restore_augments(run, data, game)

    hull = data.get("hull", {})
    if hull and run.player_ship is not None:
        run.player_ship.hull.maximum = int(hull.get("max", run.player_ship.hull.maximum))
        run.player_ship.hull.current = int(hull.get("current", run.player_ship.hull.current))

    _restore_star_map(run, data)
    return run


def _restore_loadout(run: Run, data: dict[str, Any], game: Game) -> None:
    ps = run.player_ship
    if ps is None:
        return
    saved_weapons = data.get("weapons", [])
    if saved_weapons:
        # Rebuild from registry to honor any post-save tuning of weapon stats.
        from ftl.weapons.laser import LaserWeapon
        from ftl.weapons.missile import MissileWeapon
        from ftl.weapons.weapon import Weapon, WeaponStats

        family_map: dict[str, type[Weapon]] = {
            "laser": LaserWeapon,
            "missile": MissileWeapon,
        }
        new_weapons: list[Weapon] = []
        for entry in saved_weapons:
            wid = entry.get("id")
            if not wid or wid not in game.registry.weapons:
                continue
            wdef = game.registry.weapons[wid]
            stats = WeaponStats(
                id=wdef.id, name=wdef.name, family=wdef.family,
                damage=wdef.damage, charge_time=wdef.charge_time,
                shield_pierce=wdef.shield_pierce, breach_chance=wdef.breach_chance,
                fire_chance=wdef.fire_chance, stun_seconds=wdef.stun_seconds,
                ion_damage=wdef.ion_damage, crew_damage=wdef.crew_damage,
                system_damage=wdef.system_damage, beam_length=wdef.beam_length,
                beam_room_damage=wdef.beam_room_damage,
                projectile_count=wdef.projectile_count,
                missile_cost=wdef.missile_cost, power_required=wdef.power_required,
                cost=wdef.cost, sprite_key=wdef.sprite_key, sfx_key=wdef.sfx_key,
            )
            weapon_cls = family_map.get(wdef.family, Weapon)
            w = weapon_cls(stats)
            if entry.get("powered"):
                w.powered = True
            new_weapons.append(w)
        ps.weapons = new_weapons

    saved_drones = data.get("drones", [])
    if saved_drones:
        from ftl.drones.drone import Drone, DroneStats

        new_drones: list[Drone] = []
        for did in saved_drones:
            ddef = game.registry.drones.get(did)
            if ddef is None:
                continue
            new_drones.append(Drone(DroneStats(
                id=ddef.id, name=ddef.name, family=ddef.family,
                power_required=ddef.power_required, speed=ddef.speed,
                damage=ddef.damage, drone_parts_cost=ddef.drone_parts_cost,
            )))
        ps.drones = new_drones


def _restore_system_levels(run: Run, data: dict[str, Any]) -> None:
    ps = run.player_ship
    if ps is None:
        return
    for name, lvl in data.get("system_levels", {}).items():
        sys = ps.systems.get(name)
        if sys is None:
            continue
        sys.level = int(lvl)
        sys.current_power = 0
        sys.damage = 0
        sys.ion_charge = 0.0


def _restore_crew_state(run: Run, data: dict[str, Any]) -> None:
    ps = run.player_ship
    if ps is None:
        return
    from ftl.crew.skills import Skill

    crew_payload = data.get("crew", [])
    # Match by index — ship_def crew order matches save order most of the time
    # (we save only home-team alive crew). If counts mismatch, just apply to
    # the matching prefix.
    for crew, entry in zip(ps.crew, crew_payload):
        crew.hp = float(entry.get("hp", crew.max_hp))
        skill_payload = entry.get("skills", {})
        for s in Skill:
            if s.value in skill_payload:
                crew.skills[s] = float(skill_payload[s.value])


def _restore_star_map(run: Run, data: dict[str, Any]) -> None:
    payload = data.get("star_map")
    if not payload:
        return
    sm = StarMap(
        sector_id=payload.get("sector_id", ""),
        current_beacon=payload.get("current_beacon"),
        exit_beacon=payload.get("exit_beacon"),
    )
    for b_data in payload.get("beacons", []):
        beacon = Beacon(
            id=b_data["id"],
            x=float(b_data.get("x", 0.0)),
            y=float(b_data.get("y", 0.0)),
            sector_id=b_data.get("sector_id", sm.sector_id),
            visited=bool(b_data.get("visited", False)),
            has_store=bool(b_data.get("has_store", False)),
            has_distress=bool(b_data.get("has_distress", False)),
            has_quest=bool(b_data.get("has_quest", False)),
            encounter_id=b_data.get("encounter_id"),
            connections=list(b_data.get("connections", [])),
        )
        sm.add_beacon(beacon)
    run.star_map = sm


def _restore_augments(run: Run, data: dict[str, Any], game: Game) -> None:
    if run.player_ship is None:
        return
    from ftl.augments.factory import augment_from_def

    saved_ids = data.get("augments", [])
    run.augments = []
    for aid in saved_ids:
        adef = game.registry.augments.get(aid)
        if adef is None:
            continue
        aug = augment_from_def(adef)
        if aug is None:
            continue
        aug.install(run.player_ship)
        run.augments.append(aug)
