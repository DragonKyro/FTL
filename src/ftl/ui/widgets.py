"""Generic UI widgets. Phase-0: type-only stubs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height
