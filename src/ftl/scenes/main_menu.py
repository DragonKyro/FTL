"""Main menu — entry point.

Phase 3 exposes two starting scenarios via hotkey:
- [N] First Encounter (Wayfarer vs Vein Skiff, medbay path)
- [P] Pilgrim Path (Pilgrim — Wayfarer with clonebay — vs Vein Skiff)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.scenarios.loader import build_combat_from_scenario
from ftl.scenes.combat_scene import CombatScene
from ftl.ui import theme

if TYPE_CHECKING:
    from ftl.core.game import Game


_FIRST_ENCOUNTER_ID: str = "first_encounter"
_PILGRIM_PATH_ID: str = "pilgrim_path"


class MainMenuScene(Scene):
    def __init__(self, game: Game | None = None) -> None:
        super().__init__(game=game)
        self._title = arcade.Text(
            WINDOW_TITLE,
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.70,
            theme.TEXT_PRIMARY,
            theme.FONT_TITLE_SIZE,
            anchor_x="center",
        )
        self._subtitle = arcade.Text(
            "Phase 3 — Every room lives",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.62,
            theme.TEXT_DIM,
            theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        self._hint = arcade.Text(
            "[N] First Encounter   [P] Pilgrim Path   [Esc] Quit",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.30,
            theme.TEXT_ACCENT,
            theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        if self.game is not None:
            self.game.simulation.paused = True

    def on_draw(self) -> None:
        self.clear()
        self._title.draw()
        self._subtitle.draw()
        self._hint.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.N and self.game is not None:
            self._start_scenario(_FIRST_ENCOUNTER_ID)
        elif symbol == arcade.key.P and self.game is not None:
            self._start_scenario(_PILGRIM_PATH_ID)
        elif symbol == arcade.key.ESCAPE and self.window is not None:
            self.window.close()

    def _start_scenario(self, scenario_id: str) -> None:
        if self.game is None or self.window is None:
            return
        run = self.game.new_run()
        registry = self.game.registry
        scenario = registry.scenarios[scenario_id]
        rng = run.rng.stream("combat:0")
        engine = build_combat_from_scenario(
            scenario, registry, rng, event_bus=self.game.event_bus
        )
        player_def = registry.ships[scenario.player_ship]
        enemy_def = registry.ships[scenario.enemy_ship]
        scene = CombatScene(
            self.game, engine, player_def, enemy_def, scenario_title=scenario.name
        )
        self.window.show_view(scene)
