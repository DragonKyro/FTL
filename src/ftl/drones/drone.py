"""Drone base + DroneStats.

Same hybrid pattern as weapons: DroneStats from YAML, behavior from family
subclasses (`CombatDrone`, `DefenseDrone`, ...).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DroneStats:
    id: str
    name: str
    family: str  # "combat" | "defense" | "boarding" | "repair" | "hacking"
    power_required: int = 1
    speed: float = 1.0
    damage: int = 0
    drone_parts_cost: int = 1


class Drone:
    """Runtime drone instance."""

    def __init__(self, stats: DroneStats) -> None:
        self.stats: DroneStats = stats
        self.powered: bool = False
        self.alive: bool = True

    def tick(self, dt: float) -> None:
        return None
