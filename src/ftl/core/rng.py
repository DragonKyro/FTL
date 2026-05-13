"""Seeded RNG for deterministic runs and reproducible encounters.

A run has a master seed. Subsystems (sector layout, encounter rolls, loot,
AI tie-breaks) draw from named child streams derived from the master, so
adding new RNG consumers doesn't ripple-change earlier values within a seed.
"""

from __future__ import annotations

import random


class RNG:
    """Master seed + named child streams."""

    def __init__(self, seed: int | None = None) -> None:
        self.seed: int = (
            seed if seed is not None else random.SystemRandom().randrange(2**63)
        )
        self._master = random.Random(self.seed)
        self._streams: dict[str, random.Random] = {}

    def stream(self, name: str) -> random.Random:
        if name not in self._streams:
            self._streams[name] = random.Random(f"{self.seed}:{name}")
        return self._streams[name]

    def reset(self) -> None:
        self._master = random.Random(self.seed)
        self._streams.clear()
