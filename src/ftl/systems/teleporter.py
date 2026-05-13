"""TeleporterSystem — sends crew to enemy ship and back.

Phase 2 implementation: tracks a cooldown timer between sends, exposes
`pad_capacity` (default 2 — how many crew can teleport per dispatch),
and provides `begin_cooldown()` to be called by the CombatEngine after
a successful teleport. The actual crew-movement bookkeeping lives in
`CombatEngine.send_boarders` / `recall_boarders`.

The cooldown is paused when the system is non-operational (no power /
ionized), matching FTL.
"""

from __future__ import annotations

from ftl.systems.system import System

TELEPORTER_COOLDOWN_SECONDS: float = 15.0
TELEPORTER_PAD_CAPACITY: int = 2


class TeleporterSystem(System):
    name = "teleporter"

    def __init__(self, max_power: int = 4, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.cooldown_remaining: float = 0.0
        self.pad_capacity: int = TELEPORTER_PAD_CAPACITY

    @property
    def is_ready(self) -> bool:
        return self.is_operational and self.cooldown_remaining <= 0.0

    def begin_cooldown(self) -> None:
        self.cooldown_remaining = TELEPORTER_COOLDOWN_SECONDS

    def tick(self, dt: float) -> None:
        super().tick(dt)
        # Cooldown only ticks down when system is powered + un-ionized.
        if not self.is_operational:
            return
        if self.cooldown_remaining > 0:
            self.cooldown_remaining = max(0.0, self.cooldown_remaining - dt)
