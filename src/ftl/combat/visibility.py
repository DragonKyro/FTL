"""Sensors visibility — how much of the opponent ship the player sees.

The UI calls `enemy_visibility(viewer)` to decide what to draw on the
opponent's ShipView. Levels:

- 1: room outlines + hull bar only
- 2: + labels, oxygen tint, fire, breach overlays
- 3: + crew positions on the enemy
- 4: + (Phase 4+) enemy weapon charges
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship


MAX_VISIBILITY: int = 4


def enemy_visibility(viewer: Ship) -> int:
    sensors = viewer.systems.get("sensors")
    bonus = getattr(viewer, "sensors_bonus", 0)
    if sensors is None or not sensors.is_operational:
        return min(MAX_VISIBILITY, max(1, 1 + bonus))
    base = sensors.effective_power
    if sensors.manning_crew is not None:
        base += 1
    return min(MAX_VISIBILITY, max(1, base + bonus))
