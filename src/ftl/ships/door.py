"""Doors connect adjacent rooms. Closed doors slow oxygen flow and fire spread."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Door:
    id: str
    room_a: str
    room_b: str
    open: bool = False
    level: int = 1
    hp: int = 4
    ionized: bool = False
