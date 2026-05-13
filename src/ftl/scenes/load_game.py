"""Load Game scene — lists save slots and resumes the chosen run."""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.persistence.save import SaveSlot, list_saves, load_run
from ftl.ui import art, theme

if TYPE_CHECKING:
    from ftl.core.game import Game


_ROW_H: int = 70
_ROW_W: int = 760
_ROW_GAP: int = 12


class _SlotRow:
    def __init__(self, slot: SaveSlot, cx: float, cy: float) -> None:
        self.slot = slot
        self.cx = cx
        self.cy = cy
        self._idle = art.rounded_panel(
            _ROW_W, _ROW_H, (28, 32, 44),
            radius=10, border=(70, 80, 100), border_w=1, shadow=True,
        )
        self._hot = art.rounded_panel(
            _ROW_W, _ROW_H, (38, 56, 78),
            radius=10, border=theme.TEXT_ACCENT, border_w=2, shadow=True,
        )
        self._name = arcade.Text(
            slot.name, cx - _ROW_W / 2 + 22, cy + 12,
            theme.TEXT_PRIMARY, theme.FONT_BODY_SIZE + 2,
        )
        self._summary = arcade.Text(
            slot.summary, cx - _ROW_W / 2 + 22, cy - 12,
            theme.TEXT_DIM, theme.FONT_LABEL_SIZE,
        )
        self._when = arcade.Text(
            slot.saved_at, cx + _ROW_W / 2 - 22, cy + 8,
            theme.TEXT_ACCENT, theme.FONT_LABEL_SIZE,
            anchor_x="right",
        )

    def contains(self, x: float, y: float) -> bool:
        return abs(x - self.cx) <= _ROW_W / 2 and abs(y - self.cy) <= _ROW_H / 2

    def draw(self, selected: bool) -> None:
        tex = self._hot if selected else self._idle
        art.draw_centered(tex, self.cx, self.cy)
        self._name.draw()
        self._summary.draw()
        self._when.draw()


class LoadGameScene(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game=game)
        self._title = arcade.Text(
            "LOAD GAME",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT - 40,
            theme.TEXT_PRIMARY, theme.FONT_TITLE_SIZE - 16,
            anchor_x="center",
        )
        self._subtitle = arcade.Text(
            "Pick a save, then press Enter (or click) to resume.",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80,
            theme.TEXT_DIM, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        self._hint = arcade.Text(
            "[Enter] Load    [Esc] Back to menu",
            WINDOW_WIDTH / 2, 22,
            theme.TEXT_DIM, theme.FONT_SMALL_SIZE,
            anchor_x="center",
        )
        self._rows: list[_SlotRow] = []
        self._selected: int = 0
        self._bg_tex: arcade.Texture | None = None
        self._empty_text = arcade.Text(
            "No saves yet. Start a run, jump to a beacon, then press [S].",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
            theme.TEXT_WARNING, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        self._error_text = arcade.Text(
            "Save could not be loaded.",
            WINDOW_WIDTH / 2, 60,
            theme.TEXT_DEFEAT, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        self._show_error: bool = False

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        if self.game is not None:
            self.game.simulation.paused = True
        if self._bg_tex is None:
            self._bg_tex = (
                art.disk_texture("ui/starfield_loadgame")
                or art.starfield(
                    WINDOW_WIDTH, WINDOW_HEIGHT, seed=29, nebula=(30, 50, 80),
                )
            )
        self._rebuild_rows()

    def _rebuild_rows(self) -> None:
        slots = list_saves()
        self._rows = []
        cx = WINDOW_WIDTH / 2
        first_y = WINDOW_HEIGHT - 160
        for idx, slot in enumerate(slots):
            cy = first_y - idx * (_ROW_H + _ROW_GAP)
            self._rows.append(_SlotRow(slot, cx, cy))
        self._selected = 0 if self._rows else -1

    def on_draw(self) -> None:
        self.clear()
        if self._bg_tex is not None:
            arcade.draw_texture_rect(
                self._bg_tex,
                arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            )
        self._title.draw()
        self._subtitle.draw()
        if not self._rows:
            self._empty_text.draw()
        if self._show_error:
            self._error_text.draw()
        for idx, row in enumerate(self._rows):
            row.draw(idx == self._selected)
        self._hint.draw()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        for idx, row in enumerate(self._rows):
            if row.contains(x, y):
                self._selected = idx
                return

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        for idx, row in enumerate(self._rows):
            if row.contains(x, y):
                self._selected = idx
                self._load()
                return

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            self._back()
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            if self._rows:
                self._selected = (self._selected + 1) % len(self._rows)
        elif symbol in (arcade.key.UP, arcade.key.W):
            if self._rows:
                self._selected = (self._selected - 1) % len(self._rows)
        elif symbol in (arcade.key.ENTER, arcade.key.RETURN):
            self._load()

    def _back(self) -> None:
        from ftl.scenes.main_menu import MainMenuScene

        if self.window is None:
            return
        self.window.show_view(MainMenuScene(self.game))

    def _load(self) -> None:
        if not self._rows or self.game is None or self.window is None:
            return
        if self._selected < 0 or self._selected >= len(self._rows):
            return
        slot = self._rows[self._selected].slot
        result = load_run(slot.path, self.game)
        if result is None:
            self._show_error = True
            return
        from ftl.scenes.flow import resume_run

        resume_run(self.game, self.window)
