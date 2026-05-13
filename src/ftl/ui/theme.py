"""Placeholder color palette and font sizes.

Real art swap-in is a one-file change: real sprites/fonts get loaded here,
everything else references these constants.
"""

from __future__ import annotations

import arcade

# --- Backgrounds ---------------------------------------------------------

BG_PRIMARY: tuple[int, int, int] = arcade.color.BLACK
BG_PANEL: tuple[int, int, int] = (20, 24, 30)
BG_HUD: tuple[int, int, int] = (12, 14, 20)

# --- Text ----------------------------------------------------------------

TEXT_PRIMARY: tuple[int, int, int] = arcade.color.WHITE
TEXT_DIM: tuple[int, int, int] = (140, 140, 150)
TEXT_ACCENT: tuple[int, int, int] = (90, 200, 240)
TEXT_WARNING: tuple[int, int, int] = (255, 180, 80)
TEXT_VICTORY: tuple[int, int, int] = (120, 220, 140)
TEXT_DEFEAT: tuple[int, int, int] = (220, 90, 90)

# --- Status colors -------------------------------------------------------

COLOR_HULL: tuple[int, int, int] = (200, 80, 80)
COLOR_HULL_LOW: tuple[int, int, int] = (220, 60, 60)
COLOR_HULL_OK: tuple[int, int, int] = (120, 200, 120)
COLOR_SHIELDS: tuple[int, int, int] = (90, 200, 240)
COLOR_SHIELDS_DIM: tuple[int, int, int] = (40, 90, 120)
COLOR_OXYGEN: tuple[int, int, int] = (80, 200, 120)
COLOR_FIRE: tuple[int, int, int] = (240, 120, 60)
COLOR_BREACH: tuple[int, int, int] = (200, 60, 40)

# --- Combat visuals ------------------------------------------------------

COLOR_ROOM_FILL: tuple[int, int, int] = (40, 48, 64)
COLOR_ROOM_OUTLINE: tuple[int, int, int] = (140, 150, 170)
COLOR_ROOM_TARGETED: tuple[int, int, int] = (220, 80, 80)
COLOR_ROOM_DAMAGED: tuple[int, int, int] = (90, 50, 50)

COLOR_LASER_PROJECTILE: tuple[int, int, int] = (255, 230, 90)
COLOR_MISSILE_PROJECTILE: tuple[int, int, int] = (220, 140, 80)
COLOR_PROJECTILE_DEFAULT: tuple[int, int, int] = (220, 220, 220)

COLOR_POWER_FILLED: tuple[int, int, int] = (120, 220, 140)
COLOR_POWER_EMPTY: tuple[int, int, int] = (50, 60, 60)
COLOR_POWER_DAMAGED: tuple[int, int, int] = (160, 60, 60)
COLOR_CHARGE_BAR: tuple[int, int, int] = (200, 200, 90)

# --- Fonts ---------------------------------------------------------------

FONT_TITLE_SIZE: int = 48
FONT_BODY_SIZE: int = 16
FONT_SMALL_SIZE: int = 12
FONT_LABEL_SIZE: int = 11
