"""Drone base + DroneStats.

Same hybrid pattern as weapons: DroneStats from YAML, behavior in the
`drones/runtime.py` driver (which dispatches per-family). Family
subclasses exist as identity markers; they don't override `tick`.

Drones tick from `CombatEngine` (via `drone_runtime.tick_drones`), not
from `Ship.tick`, because they need a reference to the opposing ship.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DroneStats:
    id: str
    name: str
    family: str
    power_required: int = 1
    speed: float = 1.0
    damage: int = 0
    drone_parts_cost: int = 1
    charge_time: float = 7.0
    intercept_chance: float = 0.5
    hp: int = 4


class Drone:
    """Runtime drone instance."""

    def __init__(self, stats: DroneStats) -> None:
        self.stats: DroneStats = stats
        self.powered: bool = False
        self.alive: bool = True
        self.hp: int = stats.hp

        # Combat drone state
        self.charge_progress: float = 0.0
        # Defense drone state
        self.intercept_cooldown: float = 0.0
        # Hull repair drone state
        self.repair_progress: float = 0.0

    def tick(self, dt: float) -> None:
        # No-op here — the real tick logic lives in `drones/runtime.py`,
        # which has access to the opposing ship and the CombatEngine.
        return None
