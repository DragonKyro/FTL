"""Combat scene — the playable view for one 1v1 fight.

Composes ShipView (×2), PowerPanel, WeaponStrip, and CombatHUD over the
CombatEngine. Handles input: spacebar pause, number keys for system power,
click weapon slot to select, click enemy room to target, F to flee, Esc to
return to main menu.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.combat.combat_state import Outcome
from ftl.config import WINDOW_HEIGHT, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.ui import theme
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

        # Lay ships out — player on left, enemy on right.
        ship_y = WINDOW_HEIGHT * 0.45
        self.player_view = ShipView(
            engine.player, player_def, WINDOW_WIDTH * 0.10, ship_y, title=engine.player.name
        )
        self.enemy_view = ShipView(
            engine.enemy, enemy_def, WINDOW_WIDTH * 0.62, ship_y, title=engine.enemy.name
        )

        # HUD + panels along the bottom.
        self.power_panel = PowerPanel(
            engine.player, origin_x=WINDOW_WIDTH * 0.05, origin_y=120
        )
        self.weapon_strip = WeaponStrip(
            engine.player,
            engine.state.player_inventory,
            origin_x=WINDOW_WIDTH * 0.05,
            origin_y=60,
        )
        self.hud = CombatHUD(engine, game.simulation, scenario_title)

        self._outcome_handled: bool = False

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
        self.player_view.draw(targeted_room_id=None)
        targeted = self._currently_targeted_enemy_room()
        self.enemy_view.draw(targeted_room_id=targeted)
        self._draw_projectiles()
        self.hud.draw()
        self.power_panel.draw()
        self.weapon_strip.draw()
        self._draw_controls_hint()

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
        elif symbol == arcade.key.F:
            self.engine.begin_flee()
        elif symbol == arcade.key.ESCAPE:
            self._return_to_menu()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        # Click a weapon slot.
        idx = self.weapon_strip.slot_at(x, y)
        if idx is not None:
            weapon = self.engine.player.weapons[idx]
            if self.weapon_strip.selected_index == idx:
                # Second click on the same slot: toggle power.
                if weapon.powered:
                    weapon.powered = False
                else:
                    self._power_weapon(weapon)
                self.weapon_strip.selected_index = None
            else:
                self.weapon_strip.selected_index = idx
            return
        # Click an enemy room while a weapon is selected: set target + auto-power.
        if self.weapon_strip.selected_index is not None:
            room_id = self.enemy_view.room_at(x, y)
            if room_id is not None:
                weapon = self.engine.player.weapons[self.weapon_strip.selected_index]
                weapon.target_room_id = room_id
                self._power_weapon(weapon)
                self.weapon_strip.selected_index = None

    # --- helpers ------------------------------------------------------------

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
            "[1-4] power: weapons / shields / engines / pilot   "
            "[click] weapon then enemy room   "
            "[Space] pause   [F] flee   [Esc] menu"
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
        from ftl.scenes.game_over import GameOverScene

        self.window.show_view(GameOverScene(self.game, outcome))

    def _return_to_menu(self) -> None:
        from ftl.scenes.main_menu import MainMenuScene

        self.window.show_view(MainMenuScene(self.game))
