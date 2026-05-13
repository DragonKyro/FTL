"""In-flight projectile and beam-sweep state."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Projectile:
    """A weapon's in-flight projectile."""

    x: float
    y: float
    vx: float
    vy: float
    damage: int
    target_room_id: str
    alive: bool = True

    def tick(self, dt: float) -> None:
        if not self.alive:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt


@dataclass
class BeamSweep:
    """An in-progress beam sweep crossing one or more rooms."""

    start_x: float
    start_y: float
    end_x: float
    end_y: float
    progress: float = 0.0
    speed: float = 1.0
    alive: bool = True

    def tick(self, dt: float) -> None:
        if not self.alive:
            return
        self.progress = min(1.0, self.progress + self.speed * dt)
        if self.progress >= 1.0:
            self.alive = False
