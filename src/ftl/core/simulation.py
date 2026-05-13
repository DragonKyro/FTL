"""Fixed-step simulation loop.

`Simulation.update(real_dt)` is called once per render frame with the
wall-clock delta. It accumulates time and dispatches as many fixed `dt` ticks
as fit. Pause stops the accumulator. `speed_multiplier` scales simulated time.
This decoupling keeps gameplay deterministic, testable, and pause-friendly.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ftl.config import SIM_DT


@runtime_checkable
class Tickable(Protocol):
    """Object whose simulated state advances each fixed tick."""

    def tick(self, dt: float) -> None: ...


class Simulation:
    """Owns the simulation clock and dispatches ticks to registered Tickables."""

    def __init__(self, dt: float = SIM_DT) -> None:
        self.dt: float = dt
        self.paused: bool = False
        self.speed_multiplier: float = 1.0
        self.ticks_elapsed: int = 0
        self._accumulator: float = 0.0
        self._tickables: list[Tickable] = []

    def register(self, tickable: Tickable) -> None:
        self._tickables.append(tickable)

    def unregister(self, tickable: Tickable) -> None:
        if tickable in self._tickables:
            self._tickables.remove(tickable)

    def update(self, real_dt: float) -> int:
        """Advance simulated time by `real_dt` seconds of wall clock.

        Returns the number of fixed ticks dispatched this call.
        """
        if self.paused:
            return 0
        self._accumulator += real_dt * self.speed_multiplier
        ticks = 0
        while self._accumulator >= self.dt:
            for tickable in self._tickables:
                tickable.tick(self.dt)
            self._accumulator -= self.dt
            self.ticks_elapsed += 1
            ticks += 1
        return ticks

    def reset(self) -> None:
        self._accumulator = 0.0
        self.ticks_elapsed = 0
        self.paused = False
        self.speed_multiplier = 1.0
