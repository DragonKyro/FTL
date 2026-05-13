"""Combat scene — the playable view for one 1v1 fight (Phase 2 wiring).

Composes ShipView (×2), CrewPanel, PowerPanel, WeaponStrip, CombatHUD.
Handles input: pause, system power, weapon selection + targeting, crew
selection + movement, door toggle, teleporter send + recall, flee.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.combat.combat_state import Outcome
from ftl.combat.visibility import enemy_visibility
from ftl.config import WINDOW_HEIGHT, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.crew.crew import CrewState
from ftl.ships.pathfinding import find_path
from ftl.ui import theme
from ftl.ui.crew_panel import CrewPanel
from ftl.ui.hud import CombatHUD
from ftl.ui.power_panel import PowerPanel
from ftl.ui.ship_view import ShipView
from ftl.ui.weapon_strip import WeaponStrip

if TYPE_CHECKING:
    from ftl.combat.engine import CombatEngine
    from ftl.core.game import Game
    from ftl.data.schemas import ShipDef
    from ftl.weapons.weapon import Weapon


PROJECTILE_RADIUS: float = 4.0


class CombatScene(Scene):
    def __init__(
        self,
        game: Game,
        engine: CombatEngine,
        player_def: ShipDef,
        enemy_def: ShipDef,
        scenario_title: str = "First Encounter",
    ) -> None:
        super().__init__(game=game)
        self.engine: CombatEngine = engine
        self.scenario_title: str = scenario_title

        ship_y = WINDOW_HEIGHT * 0.40
        self.player_view = ShipView(
            engine.player, player_def, 280, ship_y, title=engine.player.name
        )
        self.enemy_view = ShipView(
            engine.enemy, enemy_def, 760, ship_y, title=engine.enemy.name
        )
        self.crew_panel = CrewPanel(engine, origin_x=12, origin_y=WINDOW_HEIGHT - 60)
        self.power_panel = PowerPanel(
            engine.player, origin_x=280, origin_y=140
        )
        self.weapon_strip = WeaponStrip(
            engine.player,
            engine.state.player_inventory,
            origin_x=280,
            origin_y=80,
        )
        self.hud = CombatHUD(engine, game.simulation, scenario_title)

        self._outcome_handled: bool = False
        self._targeting_action: str | None = None  # "teleport" | "mind" | "hack" | "boarding"

    # --- arcade lifecycle ---------------------------------------------------

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        self.game.simulation.register(self.engine)
        self.game.simulation.paused = False

    def on_hide_view(self) -> None:
        try:
            self.game.simulation.unregister(self.engine)
        except ValueError:
            pass

    def on_draw(self) -> None:
        self.clear()
        selected_crew = self.crew_panel.selected_crew()
        # Show the weapon-targeted room outlined in red on the enemy ship.
        weapon_target = self._currently_targeted_enemy_room()
        visibility = enemy_visibility(self.engine.player)
        self.player_view.draw(
            targeted_room_id=None,
            selected_crew=selected_crew,
            visibility=4,
        )
        self.enemy_view.draw(
            targeted_room_id=weapon_target,
            selected_crew=selected_crew,
            visibility=visibility,
        )
        self._draw_projectiles()
        self.hud.draw()
        self.crew_panel.draw()
        self.power_panel.draw()
        self.weapon_strip.draw()
        self._draw_targeting_banner()
        self._draw_active_status()
        self._draw_controls_hint()

    def _draw_targeting_banner(self) -> None:
        if self._targeting_action is None:
            return
        label = {
            "teleport": "TELEPORT — click an enemy room",
            "mind": "MIND CONTROL — click an enemy crew member",
            "hack": "HACKING — click an enemy system room",
            "boarding": "BOARDING DRONE — click an enemy room",
        }.get(self._targeting_action, "TARGETING")
        arcade.draw_text(
            label,
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT - 90,
            theme.TEXT_WARNING,
            theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def _draw_active_status(self) -> None:
        """Tiny status line showing active-system cooldowns."""
        parts: list[str] = []
        for name, label in (
            ("cloaking", "CLOAK"),
            ("battery", "BATT"),
            ("mind_control", "MIND"),
            ("hacking", "HACK"),
        ):
            system = self.engine.player.systems.get(name)
            if system is None:
                continue
            if getattr(system, "is_active", False):
                rem = getattr(system, "active_remaining", 0.0)
                parts.append(f"{label} {rem:.0f}s")
            elif getattr(system, "cooldown_remaining", 0.0) > 0:
                rem = getattr(system, "cooldown_remaining", 0.0)
                parts.append(f"{label} cd{rem:.0f}s")
        if parts:
            arcade.draw_text(
                "  ".join(parts),
                WINDOW_WIDTH - 16,
                WINDOW_HEIGHT - 64,
                theme.TEXT_ACCENT,
                theme.FONT_LABEL_SIZE,
                anchor_x="right",
            )

    def on_update(self, delta_time: float) -> None:
        if not self._outcome_handled and self.engine.outcome is not Outcome.FIGHTING:
            self._outcome_handled = True
            self._goto_game_over(self.engine.outcome)

    # --- input --------------------------------------------------------------

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.SPACE:
            self.game.simulation.paused = not self.game.simulation.paused
        elif symbol == arcade.key.KEY_1:
            self._cycle_power("weapons")
        elif symbol == arcade.key.KEY_2:
            self._cycle_power("shields")
        elif symbol == arcade.key.KEY_3:
            self._cycle_power("engines")
        elif symbol == arcade.key.KEY_4:
            self._cycle_power("piloting")
        elif symbol == arcade.key.KEY_5:
            self._cycle_power("medbay")
        elif symbol == arcade.key.KEY_6:
            self._cycle_power("oxygen")
        elif symbol == arcade.key.KEY_7:
            self._cycle_power("teleporter")
        elif symbol == arcade.key.F:
            self.engine.begin_flee()
        elif symbol == arcade.key.T:
            self._toggle_targeting("teleport")
        elif symbol == arcade.key.R:
            self.engine.recall_boarders()
        elif symbol == arcade.key.C:
            self.engine.activate_cloak()
        elif symbol == arcade.key.B:
            self.engine.activate_battery()
        elif symbol == arcade.key.M:
            self._toggle_targeting("mind")
        elif symbol == arcade.key.H:
            self._toggle_targeting("hack")
        elif symbol == arcade.key.D:
            self._toggle_targeting("boarding")
        elif symbol == arcade.key.A:
            self.engine.try_deploy_ap_drone()
        elif symbol == arcade.key.ESCAPE:
            self._return_to_menu()

    def _toggle_targeting(self, action: str) -> None:
        if self._targeting_action == action:
            self._targeting_action = None
        else:
            self._targeting_action = action

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        # Crew panel click → select crew member.
        crew_idx = self.crew_panel.crew_at(x, y)
        if crew_idx is not None:
            self.crew_panel.selected_index = crew_idx
            self.weapon_strip.selected_index = None
            return

        # Targeting modes — click on the enemy ship resolves the action.
        if self._targeting_action is not None:
            self._handle_targeting_click(x, y)
            return

        # Door toggle (player ship only).
        door = self.player_view.door_at(x, y)
        if door is not None:
            door.toggle()
            return

        # Selected crew + click on a tile of player or enemy → move there.
        selected = self.crew_panel.selected_crew()
        if selected is not None:
            player_tile = self.player_view.tile_at(x, y)
            enemy_tile = self.enemy_view.tile_at(x, y)
            tile = player_tile if player_tile is not None else enemy_tile
            if tile is not None and selected.current_ship is not None:
                hosting_ship = (
                    self.engine.player if player_tile is not None else self.engine.enemy
                )
                if (
                    hosting_ship is selected.current_ship
                    and selected.current_tile is not None
                ):
                    is_home = hosting_ship.is_home_team(selected)
                    path = find_path(
                        hosting_ship, selected.current_tile, tile, is_home
                    )
                    if path is not None:
                        selected.path = path
                        selected.move_progress = 0.0
                        if path:
                            selected.state = CrewState.MOVING
                return

        # Weapon slot click — same as Phase 1.
        idx = self.weapon_strip.slot_at(x, y)
        if idx is not None:
            weapon = self.engine.player.weapons[idx]
            if self.weapon_strip.selected_index == idx:
                if weapon.powered:
                    weapon.powered = False
                else:
                    self._power_weapon(weapon)
                self.weapon_strip.selected_index = None
            else:
                self.weapon_strip.selected_index = idx
                self.crew_panel.selected_index = None
            return

        # Weapon target on enemy room.
        if self.weapon_strip.selected_index is not None:
            room_id = self.enemy_view.room_at(x, y)
            if room_id is not None:
                weapon = self.engine.player.weapons[self.weapon_strip.selected_index]
                weapon.target_room_id = room_id
                self._power_weapon(weapon)
                self.weapon_strip.selected_index = None

    # --- targeting handler ------------------------------------------------

    def _handle_targeting_click(self, x: int, y: int) -> None:
        action = self._targeting_action
        self._targeting_action = None  # one-shot
        if action is None:
            return
        room_id = self.enemy_view.room_at(x, y)
        target_room = self.engine.enemy.rooms.get(room_id) if room_id else None

        if action == "teleport":
            if target_room is not None:
                pad_crew = self._teleporter_pad_crew()
                self.engine.send_boarders(pad_crew, target_room)
        elif action == "mind":
            # Find an enemy crew on the clicked tile.
            tile = self.enemy_view.tile_at(x, y)
            if tile is not None:
                target_crew = next(
                    (
                        c for c in self.engine.enemy.crew
                        if c.alive
                        and c.current_tile is not None
                        and c.current_tile.x == tile.x
                        and c.current_tile.y == tile.y
                        and c.team == "enemy"
                    ),
                    None,
                )
                if target_crew is not None:
                    self.engine.try_mind_control(target_crew)
        elif action == "hack":
            if target_room is not None and target_room.system is not None:
                self.engine.try_hack(target_room.system, self.engine.enemy)
        elif action == "boarding":
            if target_room is not None:
                self.engine.try_deploy_boarding_drone(target_room)

    # --- helpers ------------------------------------------------------------

    def _teleporter_pad_crew(self) -> list:  # type: ignore[type-arg]
        tele = self.engine.player.teleporter
        if tele is None:
            return []
        pad_room = next(
            (r for r in self.engine.player.rooms.values() if r.system is tele),
            None,
        )
        if pad_room is None:
            return []
        pad_coords = {(t.x, t.y) for t in pad_room.tiles}
        return [
            c for c in self.engine.player.crew
            if c.alive
            and c.current_tile is not None
            and (c.current_tile.x, c.current_tile.y) in pad_coords
        ]

    def _cycle_power(self, system_name: str) -> None:
        ship = self.engine.player
        system = ship.systems.get(system_name)
        if system is None:
            return
        new_power = system.current_power + 1
        if new_power > system.level:
            new_power = 0
        budget = ship.max_reactor_power - (ship.power_used - system.current_power)
        if new_power > budget:
            new_power = 0
        system.set_power(new_power)
        if system_name == "weapons":
            self._sync_weapon_power_to_system()

    def _power_weapon(self, weapon: Weapon) -> bool:
        weapons_system = self.engine.player.systems.get("weapons")
        if weapons_system is None:
            return False
        in_use = sum(
            w.stats.power_required for w in self.engine.player.weapons if w.powered
        )
        if in_use + weapon.stats.power_required > weapons_system.effective_power:
            return False
        weapon.powered = True
        return True

    def _sync_weapon_power_to_system(self) -> None:
        weapons_system = self.engine.player.systems.get("weapons")
        budget = weapons_system.effective_power if weapons_system else 0
        for weapon in self.engine.player.weapons:
            if weapon.powered:
                if budget >= weapon.stats.power_required:
                    budget -= weapon.stats.power_required
                else:
                    weapon.powered = False

    def _currently_targeted_enemy_room(self) -> str | None:
        idx = self.weapon_strip.selected_index
        if idx is None:
            return None
        return self.engine.player.weapons[idx].target_room_id

    def _draw_projectiles(self) -> None:
        for projectile in self.engine.projectiles:
            source_view = (
                self.player_view
                if projectile.source_ship is self.engine.player
                else self.enemy_view
            )
            target_view = (
                self.player_view
                if projectile.target_ship is self.engine.player
                else self.enemy_view
            )
            start = source_view.center()
            target_center = target_view.room_center(projectile.target_room_id)
            end = target_center if target_center is not None else target_view.center()
            t = projectile.progress
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            if projectile.weapon_family == "missile":
                color = theme.COLOR_MISSILE_PROJECTILE
            elif projectile.weapon_family == "laser":
                color = theme.COLOR_LASER_PROJECTILE
            else:
                color = theme.COLOR_PROJECTILE_DEFAULT
            arcade.draw_circle_filled(x, y, PROJECTILE_RADIUS, color)
            if projectile.weapon_family == "missile":
                arcade.draw_line(start[0], start[1], x, y, color, 2)

    def _draw_controls_hint(self) -> None:
        hint = (
            "[1-7] power  [click crew/tile] move  [click door] toggle  "
            "[T] teleport  [R] recall  [C] cloak  [B] battery  "
            "[M] mind  [H] hack  [D] boarding drone  [A] AP drone  "
            "[Space] pause  [F] flee  [Esc] menu"
        )
        arcade.draw_text(
            hint,
            WINDOW_WIDTH / 2,
            16,
            theme.TEXT_DIM,
            theme.FONT_SMALL_SIZE,
            anchor_x="center",
        )

    def _goto_game_over(self, outcome: Outcome) -> None:
        # Phase 4: route through the scene-flow controller so wins return
        # to the star map and losses → game over. Boss flag stored by the
        # flow controller when it created this scene.
        from ftl.scenes.flow import after_combat_loss, after_combat_win
        from ftl.scenes.game_over import GameOverScene

        is_boss = getattr(self, "_is_boss", False)
        if self.window is None or self.game is None:
            return
        if outcome is Outcome.WON:
            after_combat_win(self.game, self.window, is_boss)
        elif outcome is Outcome.LOST:
            after_combat_loss(self.game, self.window)
        else:  # FLED or any other terminal
            self.window.show_view(GameOverScene(self.game, outcome))

    def _return_to_menu(self) -> None:
        from ftl.scenes.main_menu import MainMenuScene

        self.window.show_view(MainMenuScene(self.game))
