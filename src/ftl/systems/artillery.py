"""ArtillerySystem — auto-firing built-in weapon (ship-specific)."""

from __future__ import annotations

from ftl.systems.system import System


class ArtillerySystem(System):
    name = "artillery"

    def __init__(self, max_power: int = 4, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.charge_progress: float = 0.0
