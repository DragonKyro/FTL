"""Weapon targeting — which enemy room a weapon is aimed at."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Target:
    room_id: str
    locked: bool = True
