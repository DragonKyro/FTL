"""Scene flow controller — orchestrates sector / encounter transitions.

Phase 4 lifecycle:

```
MainMenu
   ↓ start_run
StarMap  ← (return) ← Combat (win) | Event (resolved) | Store (left)
   ↓ jump (click beacon)
[start_encounter dispatch by encounter_id]
   → Combat | Event | Store | Empty
   ↓ resolve
StarMap  (unless reached exit)
   ↓ jump to exit beacon
[advance_sector or final boss]
   ↓ win/lose
GameOver
```

The Run object on `Game.run` carries the canonical player ship, the
current `star_map`, the current `current_beacon_id`, and the resource
pool across encounters.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.ai.enemy_pilot import EnemyPilot
from ftl.combat.combat_state import CombatState, Outcome
from ftl.combat.engine import CombatEngine
from ftl.map.encounter_kind import EncounterKind
from ftl.map.generation import generate_star_map
from ftl.ships.ship import EnemyShip, PlayerShip
from ftl.store.inventory import generate_store_inventory

if TYPE_CHECKING:
    import arcade

    from ftl.core.game import Game
    from ftl.data.schemas import OutcomeDef
    from ftl.map.beacon import Beacon


# Sector chain in order.
_SECTOR_CHAIN: tuple[str, ...] = (
    "the_borderlands",
    "inner_spiral_edge",
    "concordat_warfront",
)

# Enemy pool per sector (random pick on combat encounter).
_ENEMY_POOL_BY_SECTOR: dict[str, tuple[str, ...]] = {
    "the_borderlands":   ("vein_skiff", "verge_corvette"),
    "inner_spiral_edge": ("vein_skiff", "consilium_lancer"),
    "concordat_warfront": ("concordat_seraph", "concordat_seraph"),
}

# Event-pool faction directories live under story/events/<faction>/.
_EVENT_DIRS_BY_SECTOR: dict[str, tuple[str, ...]] = {
    "the_borderlands":    ("generic", "civilian", "pirate"),
    "inner_spiral_edge":  ("generic", "consilium"),
    "concordat_warfront": ("generic", "concordat"),
}


# --- run start --------------------------------------------------------


def start_run(
    game: Game,
    window: arcade.Window,
    player_ship_id: str,
    *,
    scenario_id: str | None = None,
) -> None:
    run = game.new_run()
    run.scenario_id = scenario_id
    run.sector_chain = list(_SECTOR_CHAIN)
    run.sector_index = 0
    run.sectors_total = len(_SECTOR_CHAIN)
    # Build the player ship from the chosen scenario ship YAML.
    player_def = game.registry.ships[player_ship_id]
    run.player_ship = PlayerShip.from_def(player_def, game.registry)
    run.missiles = player_def.starting_missiles
    run.scrap = 30
    run.fuel = 16
    run.drone_parts = 2
    _open_current_sector(game, window)


def start_run_from_scenario(
    game: Game, window: arcade.Window, scenario_id: str
) -> None:
    """Hangar entry point: pick a scenario by id, launch its starting ship."""
    scenario = game.registry.scenarios[scenario_id]
    start_run(game, window, scenario.player_ship, scenario_id=scenario_id)


def resume_run(game: Game, window: arcade.Window) -> None:
    """Drop the player back onto the current sector's star map.

    Used by save/load: persistence reconstructs `game.run`; this just
    hands off to the star map scene."""
    from ftl.scenes.star_map_scene import StarMapScene

    if game.run is None:
        return
    window.show_view(StarMapScene(game))


def _open_current_sector(game: Game, window: arcade.Window) -> None:
    from ftl.scenes.star_map_scene import StarMapScene

    run = game.run
    if run is None:
        return
    sector_id = run.sector_chain[run.sector_index]
    sector = game.registry.sectors[sector_id]
    rng = run.rng.stream(f"sector:{run.sector_index}")
    run.star_map = generate_star_map(sector, rng)
    run.current_beacon_id = run.star_map.current_beacon
    window.show_view(StarMapScene(game))


# --- encounter dispatch ----------------------------------------------


def start_encounter(beacon: Beacon, game: Game, window: arcade.Window) -> None:
    run = game.run
    if run is None:
        return
    # Reaching the exit beacon → advance sector (or final boss).
    if run.star_map and beacon.id == run.star_map.exit_beacon:
        _advance_sector_or_boss(game, window)
        return
    kind = beacon.encounter_id or EncounterKind.EMPTY.value
    if kind == EncounterKind.COMBAT.value:
        _start_combat_for_beacon(game, window)
    elif kind == EncounterKind.EVENT.value:
        _start_event_for_beacon(game, window)
    elif kind == EncounterKind.STORE.value:
        _start_store_for_beacon(game, window)
    else:
        # Empty beacon: stay on star map.
        from ftl.scenes.star_map_scene import StarMapScene

        window.show_view(StarMapScene(game))


def _start_combat_for_beacon(game: Game, window: arcade.Window) -> None:
    run = game.run
    if run is None or run.player_ship is None or run.star_map is None:
        return
    sector_id = run.sector_chain[run.sector_index]
    pool = _ENEMY_POOL_BY_SECTOR.get(sector_id, ("vein_skiff",))
    rng = run.rng.stream(f"combat:{run.sector_index}:{run.current_beacon_id}")
    enemy_id = rng.choice(list(pool))
    _start_combat_with_enemy(game, window, enemy_id, is_boss=False)


def _start_combat_with_enemy(
    game: Game, window: arcade.Window, enemy_id: str, is_boss: bool
) -> None:
    from ftl.scenes.combat_scene import CombatScene

    run = game.run
    if run is None or run.player_ship is None:
        return
    enemy_def = game.registry.ships[enemy_id]
    enemy = EnemyShip.from_def(enemy_def, game.registry)
    rng = run.rng.stream(
        f"enemy:{run.sector_index}:{run.current_beacon_id}:{enemy_id}"
    )
    state = CombatState(
        player=run.player_ship,
        enemy=enemy,
        player_missiles=run.missiles,
        enemy_missiles=enemy_def.starting_missiles,
    )
    state.player_inventory.drone_parts = run.drone_parts
    ai = EnemyPilot(enemy, run.player_ship, rng)
    engine = CombatEngine(
        state=state, ai=ai, rng=rng,
        event_bus=game.event_bus, registry=game.registry,
    )
    if is_boss:
        # Boss fights disable flee.
        engine.state.flee_charge_time = 1_000_000.0
    player_def = game.registry.ships[_player_ship_id_for_run(run)]
    scene = CombatScene(
        game, engine, player_def, enemy_def,
        scenario_title=("FINAL BOSS" if is_boss else "Encounter"),
    )
    setattr(scene, "_is_boss", is_boss)  # consumed by after_combat_win
    window.show_view(scene)


def _player_ship_id_for_run(run) -> str:  # type: ignore[no-untyped-def]
    # The player ship can be either wayfarer or pilgrim depending on scenario.
    if run.player_ship is None:
        return "wayfarer"
    # Match by name; falls back to wayfarer.
    return "pilgrim" if run.player_ship.name.lower().startswith("pilgrim") else "wayfarer"


def _start_event_for_beacon(game: Game, window: arcade.Window) -> None:
    from ftl.scenes.event_scene import EventScene

    run = game.run
    if run is None:
        return
    sector_id = run.sector_chain[run.sector_index]
    folders = _EVENT_DIRS_BY_SECTOR.get(sector_id, ("generic",))
    rng = run.rng.stream(f"event:{run.sector_index}:{run.current_beacon_id}")
    # Build candidate pool from event YAMLs whose path includes any of the folders.
    candidates = [
        e for e_id, e in game.registry.events.items()
        if any(folder in e_id or True for folder in folders)  # use folder hint via id heuristics later
    ]
    if not candidates:
        # Fall back to staying on the star map.
        from ftl.scenes.star_map_scene import StarMapScene

        window.show_view(StarMapScene(game))
        return
    chosen = rng.choice(candidates)
    window.show_view(EventScene(game, chosen))


def _start_store_for_beacon(game: Game, window: arcade.Window) -> None:
    from ftl.scenes.store_scene import StoreScene

    run = game.run
    if run is None:
        return
    rng = run.rng.stream(f"store:{run.sector_index}:{run.current_beacon_id}")
    inventory = generate_store_inventory(game.registry, rng)
    if run.player_ship is not None:
        from ftl.store.inventory import build_upgrade_offers

        inventory.system_upgrades = build_upgrade_offers(run.player_ship, game.registry)
    window.show_view(StoreScene(game, inventory))


# --- after-encounter callbacks ---------------------------------------


def after_combat_win(game: Game, window: arcade.Window, is_boss: bool) -> None:
    from ftl.scenes.game_over import GameOverScene
    from ftl.scenes.star_map_scene import StarMapScene

    run = game.run
    if run is None:
        return
    # Boss win → run victory.
    if is_boss:
        window.show_view(GameOverScene(game, Outcome.WON))
        return
    # Otherwise, reward + back to star map.
    run.scrap += 18
    if game.run and game.run.player_ship is not None:
        # The post-combat player ship state already lives on run.player_ship.
        pass
    window.show_view(StarMapScene(game))


def after_combat_loss(game: Game, window: arcade.Window) -> None:
    from ftl.scenes.game_over import GameOverScene

    window.show_view(GameOverScene(game, Outcome.LOST))


def after_event_resolved(
    game: Game, window: arcade.Window, outcome: OutcomeDef
) -> None:
    if outcome.starts_combat and outcome.enemy_ship_id:
        _start_combat_with_enemy(game, window, outcome.enemy_ship_id, is_boss=False)
        return
    from ftl.scenes.star_map_scene import StarMapScene

    window.show_view(StarMapScene(game))


def after_store_left(game: Game, window: arcade.Window) -> None:
    from ftl.scenes.star_map_scene import StarMapScene

    # Sync inventory back to run from player ship if needed (Phase 5+).
    window.show_view(StarMapScene(game))


# --- sector progression ---------------------------------------------


def _advance_sector_or_boss(game: Game, window: arcade.Window) -> None:
    run = game.run
    if run is None:
        return
    run.sector_index += 1
    if run.sector_index >= len(run.sector_chain):
        # End of last sector → final boss.
        _start_combat_with_enemy(game, window, "throne_of_ash", is_boss=True)
        return
    _open_current_sector(game, window)
    _autosave_silently(run)


def _autosave_silently(run) -> None:  # type: ignore[no-untyped-def]
    """Best-effort autosave on sector entry. Failures are swallowed —
    we don't want a write hiccup to interrupt the run."""
    try:
        from ftl.persistence.save import save_run

        save_run(run, "autosave")
    except (OSError, ValueError):
        pass
