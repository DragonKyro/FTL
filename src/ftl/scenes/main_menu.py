"""Main menu — entry point with polished starfield + button cards.

Refactored to route Play through a Hangar (scenario selector) so adding
new ships/scenarios doesn't keep cramming hotkeys onto this view. Load
opens the save-slot picker.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.ui import art, theme
from ftl.ui.text_cache import TextCache

if TYPE_CHECKING:
    from ftl.core.game import Game


_BUTTON_W: int = 260
_BUTTON_H: int = 56
_BUTTON_GAP: int = 18


class _MenuButton:
    def __init__(
        self,
        label: str,
        hotkey: str,
        center_x: float,
        center_y: float,
        fill: tuple[int, int, int],
    ) -> None:
        self.label = label
        self.hotkey = hotkey
        self.cx = center_x
        self.cy = center_y
        self.fill = fill
        self._tex = art.rounded_panel(
            _BUTTON_W, _BUTTON_H,
            (fill[0] + 18, fill[1] + 18, fill[2] + 22),
            (max(0, fill[0] - 18), max(0, fill[1] - 18), max(0, fill[2] - 22)),
            radius=14, border=(220, 230, 240), border_w=1, shadow=True,
        )
        self._tex_hot = art.rounded_panel(
            _BUTTON_W, _BUTTON_H,
            (min(255, fill[0] + 50), min(255, fill[1] + 50), min(255, fill[2] + 55)),
            (fill[0] + 10, fill[1] + 10, fill[2] + 14),
            radius=14, border=theme.TEXT_ACCENT, border_w=2, shadow=True,
        )
        self._label = arcade.Text(
            f"[{hotkey}]  {label}",
            center_x, center_y - 9,
            theme.TEXT_PRIMARY, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def contains(self, x: float, y: float) -> bool:
        return (
            abs(x - self.cx) <= _BUTTON_W / 2
            and abs(y - self.cy) <= _BUTTON_H / 2
        )

    def draw(self, hovered: bool) -> None:
        tex = self._tex_hot if hovered else self._tex
        # rounded_panel adds shadow padding (4px) — draw with that natural size.
        art.draw_centered(tex, self.cx, self.cy, size=None)
        self._label.draw()


class MainMenuScene(Scene):
    def __init__(self, game: Game | None = None) -> None:
        super().__init__(game=game)
        cx = WINDOW_WIDTH / 2
        self._title = arcade.Text(
            WINDOW_TITLE,
            cx, WINDOW_HEIGHT * 0.74,
            theme.TEXT_PRIMARY, theme.FONT_TITLE_SIZE,
            anchor_x="center",
        )
        self._title_glow = arcade.Text(
            WINDOW_TITLE,
            cx, WINDOW_HEIGHT * 0.74,
            (90, 200, 240, 60), theme.FONT_TITLE_SIZE + 6,
            anchor_x="center",
        )
        self._subtitle = arcade.Text(
            "The Helix Gates are failing. Something is coming through.",
            cx, WINDOW_HEIGHT * 0.66,
            theme.TEXT_DIM, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        # Buttons centered vertically below subtitle.
        first_y = WINDOW_HEIGHT * 0.50
        self._buttons: list[_MenuButton] = [
            _MenuButton(
                "PLAY",   "P", cx, first_y - 0 * (_BUTTON_H + _BUTTON_GAP), (40, 70, 90),
            ),
            _MenuButton(
                "LOAD",   "L", cx, first_y - 1 * (_BUTTON_H + _BUTTON_GAP), (50, 60, 80),
            ),
            _MenuButton(
                "QUIT",   "Q", cx, first_y - 2 * (_BUTTON_H + _BUTTON_GAP), (70, 40, 50),
            ),
        ]
        self._hover_idx: int = -1
        self._bg_tex: arcade.Texture | None = None
        self._text = TextCache()

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        if self.game is not None:
            self.game.simulation.paused = True
        if self._bg_tex is None:
            self._bg_tex = (
                art.disk_texture("ui/starfield_menu")
                or art.starfield(
                    WINDOW_WIDTH, WINDOW_HEIGHT, seed=7, nebula=(40, 60, 120),
                )
            )

    def on_draw(self) -> None:
        self.clear()
        if self._bg_tex is not None:
            arcade.draw_texture_rect(
                self._bg_tex,
                arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            )
        self._title_glow.draw()
        self._title.draw()
        self._subtitle.draw()
        for idx, button in enumerate(self._buttons):
            button.draw(idx == self._hover_idx)
        self._text.draw(
            "hint", "Press the bracketed key, or click a button.",
            WINDOW_WIDTH / 2, 28,
            theme.TEXT_DIM, theme.FONT_SMALL_SIZE,
            anchor_x="center",
        )

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self._hover_idx = -1
        for idx, button in enumerate(self._buttons):
            if button.contains(x, y):
                self._hover_idx = idx
                return

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        for b in self._buttons:
            if b.contains(x, y):
                self._activate(b.label)
                return

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.P:
            self._activate("PLAY")
        elif symbol == arcade.key.L:
            self._activate("LOAD")
        elif symbol in (arcade.key.Q, arcade.key.ESCAPE):
            self._activate("QUIT")

    def _activate(self, label: str) -> None:
        if self.game is None or self.window is None:
            return
        if label == "PLAY":
            from ftl.scenes.hangar import HangarScene

            self.window.show_view(HangarScene(self.game))
        elif label == "LOAD":
            from ftl.scenes.load_game import LoadGameScene

            self.window.show_view(LoadGameScene(self.game))
        elif label == "QUIT":
            self.window.close()
