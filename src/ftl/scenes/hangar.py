"""Hangar — scenario / starting-ship selector.

Replaces the cramped N/P hotkeys on the old main menu. Each scenario
loaded from `content/scenarios/` is rendered as a clickable card with
ship name, description, hull/reactor stats, weapons, crew. Arrow keys
or click to pick; Enter or LAUNCH button to start the run.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.ui import art, theme
from ftl.ui.text_cache import TextCache

if TYPE_CHECKING:
    from ftl.core.game import Game
    from ftl.data.schemas import ScenarioDef, ShipDef


_CARD_W: int = 360
_CARD_H: int = 420
_CARD_GAP: int = 32
_PANEL_FILL: tuple[int, int, int] = (28, 34, 48)
_PANEL_FILL_HOT: tuple[int, int, int] = (38, 56, 78)


class _ScenarioCard:
    def __init__(
        self,
        scenario: ScenarioDef,
        ship: ShipDef,
        center_x: float,
        center_y: float,
    ) -> None:
        self.scenario = scenario
        self.ship = ship
        self.cx = center_x
        self.cy = center_y
        self._tex_idle = art.rounded_panel(
            _CARD_W, _CARD_H, _PANEL_FILL,
            radius=18, border=(80, 100, 130), border_w=1, shadow=True,
        )
        self._tex_hot = art.rounded_panel(
            _CARD_W, _CARD_H, _PANEL_FILL_HOT,
            radius=18, border=theme.TEXT_ACCENT, border_w=2, shadow=True,
        )
        # Prefer the disk-baked ship silhouette; fall back to a tinted orb.
        sigil_outer = (50, 110, 160) if scenario.player_ship == "wayfarer" else (140, 90, 170)
        sigil_inner = (180, 220, 255) if scenario.player_ship == "wayfarer" else (230, 200, 255)
        self._sigil = (
            art.disk_texture(f"ships/{scenario.player_ship}")
            or art.radial_orb(
                120, sigil_inner, sigil_outer, rim=(20, 25, 35),
                halo=1.6, highlight=True,
            )
        )
        self._title = arcade.Text(
            scenario.name, center_x, center_y + _CARD_H / 2 - 50,
            theme.TEXT_PRIMARY, theme.FONT_BODY_SIZE + 8,
            anchor_x="center",
        )
        self._ship_name = arcade.Text(
            f"Ship: {ship.name}", center_x, center_y + _CARD_H / 2 - 84,
            theme.TEXT_ACCENT, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        # Description wrapped manually to fit card.
        self._desc_lines: list[arcade.Text] = []
        desc = scenario.description or ship.description or ""
        for i, line in enumerate(_wrap(desc, 40)[:3]):
            self._desc_lines.append(
                arcade.Text(
                    line, center_x, center_y + 30 - i * 18,
                    theme.TEXT_DIM, theme.FONT_LABEL_SIZE,
                    anchor_x="center",
                )
            )
        self._stat_lines: list[arcade.Text] = []
        stats = [
            f"Hull {ship.max_hull}",
            f"Reactor {ship.max_reactor_power}",
            f"Crew {len(ship.starting_crew)} ({', '.join(ship.starting_crew)})",
            f"Weapons: {', '.join(ship.starting_weapons) or '—'}",
            f"Drones: {', '.join(ship.starting_drones) or '—'}",
        ]
        base_y = center_y - 40
        for i, s in enumerate(stats):
            self._stat_lines.append(
                arcade.Text(
                    s, center_x - _CARD_W / 2 + 22, base_y - i * 20,
                    theme.TEXT_PRIMARY, theme.FONT_LABEL_SIZE,
                )
            )
        self._launch_text = arcade.Text(
            "► LAUNCH ◄",
            center_x, center_y - _CARD_H / 2 + 18,
            theme.TEXT_VICTORY, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def contains(self, x: float, y: float) -> bool:
        return (
            abs(x - self.cx) <= _CARD_W / 2
            and abs(y - self.cy) <= _CARD_H / 2
        )

    def draw(self, selected: bool) -> None:
        tex = self._tex_hot if selected else self._tex_idle
        art.draw_centered(tex, self.cx, self.cy)
        art.draw_centered(
            self._sigil,
            self.cx, self.cy + _CARD_H / 2 - 150,
            size=180, fit=True,
        )
        self._title.draw()
        self._ship_name.draw()
        for line in self._desc_lines:
            line.draw()
        for line in self._stat_lines:
            line.draw()
        if selected:
            self._launch_text.draw()


def _wrap(text: str, max_chars: int) -> list[str]:
    """Naïve word-wrap, returns at most `_wrap(text, n)` lines split by words."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur:
        lines.append(cur)
    return lines


def _eligible_scenarios(game: Game) -> list[ScenarioDef]:
    """Show scenarios whose `player_ship` resolves to a known ship."""
    out: list[ScenarioDef] = []
    for sc in game.registry.scenarios.values():
        if sc.player_ship in game.registry.ships:
            out.append(sc)
    out.sort(key=lambda s: s.name)
    return out


class HangarScene(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game=game)
        self._title = arcade.Text(
            "HANGAR",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT - 40,
            theme.TEXT_PRIMARY, theme.FONT_TITLE_SIZE - 16,
            anchor_x="center",
        )
        self._subtitle = arcade.Text(
            "Choose a scenario. Arrow keys to browse, Enter to launch.",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80,
            theme.TEXT_DIM, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        self._hint = arcade.Text(
            "[Enter] Launch    [Esc] Back to menu",
            WINDOW_WIDTH / 2, 22,
            theme.TEXT_DIM, theme.FONT_SMALL_SIZE,
            anchor_x="center",
        )
        self._cards: list[_ScenarioCard] = []
        self._selected: int = 0
        self._bg_tex: arcade.Texture | None = None
        self._empty_text = arcade.Text(
            "No scenarios available.",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
            theme.TEXT_WARNING, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        if self.game is not None:
            self.game.simulation.paused = True
        if self._bg_tex is None:
            self._bg_tex = (
                art.disk_texture("ui/starfield_hangar")
                or art.starfield(
                    WINDOW_WIDTH, WINDOW_HEIGHT, seed=13, nebula=(80, 40, 110),
                )
            )
        self._rebuild_cards()

    def _rebuild_cards(self) -> None:
        if self.game is None:
            return
        scenarios = _eligible_scenarios(self.game)
        if not scenarios:
            return
        total_w = len(scenarios) * _CARD_W + (len(scenarios) - 1) * _CARD_GAP
        start_x = (WINDOW_WIDTH - total_w) / 2 + _CARD_W / 2
        cy = WINDOW_HEIGHT * 0.46
        self._cards = []
        for idx, sc in enumerate(scenarios):
            ship = self.game.registry.ships[sc.player_ship]
            cx = start_x + idx * (_CARD_W + _CARD_GAP)
            self._cards.append(_ScenarioCard(sc, ship, cx, cy))
        self._selected = min(self._selected, len(self._cards) - 1)

    def on_draw(self) -> None:
        self.clear()
        if self._bg_tex is not None:
            arcade.draw_texture_rect(
                self._bg_tex,
                arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            )
        self._title.draw()
        self._subtitle.draw()
        if not self._cards:
            self._empty_text.draw()
        for idx, card in enumerate(self._cards):
            card.draw(idx == self._selected)
        self._hint.draw()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        for idx, card in enumerate(self._cards):
            if card.contains(x, y):
                self._selected = idx
                return

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        for idx, card in enumerate(self._cards):
            if card.contains(x, y):
                self._selected = idx
                self._launch()
                return

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            self._back()
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            if self._cards:
                self._selected = (self._selected + 1) % len(self._cards)
        elif symbol in (arcade.key.LEFT, arcade.key.A):
            if self._cards:
                self._selected = (self._selected - 1) % len(self._cards)
        elif symbol in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.SPACE):
            self._launch()

    def _back(self) -> None:
        if self.window is None:
            return
        from ftl.scenes.main_menu import MainMenuScene

        self.window.show_view(MainMenuScene(self.game))

    def _launch(self) -> None:
        if not self._cards or self.game is None or self.window is None:
            return
        scenario = self._cards[self._selected].scenario
        from ftl.scenes.flow import start_run_from_scenario

        start_run_from_scenario(self.game, self.window, scenario.id)
