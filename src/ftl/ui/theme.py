"""Placeholder color palette and font sizes.

Real art swap-in is a one-file change: real sprites/fonts get loaded here,
everything else references these constants.
"""

from __future__ import annotations

import arcade

BG_PRIMARY: tuple[int, int, int] = arcade.color.BLACK
BG_PANEL: tuple[int, int, int] = (20, 24, 30)

TEXT_PRIMARY: tuple[int, int, int] = arcade.color.WHITE
TEXT_DIM: tuple[int, int, int] = (140, 140, 150)
TEXT_ACCENT: tuple[int, int, int] = (90, 200, 240)

COLOR_HULL: tuple[int, int, int] = (200, 80, 80)
COLOR_SHIELDS: tuple[int, int, int] = (90, 200, 240)
COLOR_OXYGEN: tuple[int, int, int] = (80, 200, 120)
COLOR_FIRE: tuple[int, int, int] = (240, 120, 60)
COLOR_BREACH: tuple[int, int, int] = (200, 60, 40)

FONT_TITLE_SIZE: int = 48
FONT_BODY_SIZE: int = 16
FONT_SMALL_SIZE: int = 12
