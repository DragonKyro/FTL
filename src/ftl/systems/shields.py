"""ShieldsSystem — each 2 power = 1 shield layer.

Layers recharge over time when `current_layers < max_layers`. Damage drops
a layer (handled by the damage pipeline). Losing power drops layers down to
the new cap immediately.
"""

from __future__ import annotations

from ftl.systems.system import System

# Seconds per shield layer regenerated.
RECHARGE_TIME_PER_LAYER: float = 2.0


class ShieldsSystem(System):
    name = "shields"

    def __init__(self, max_power: int = 8, level: int = 2) -> None:
        # Default level = 2 (2 power slots = 1 layer). Phase 2+ ship YAMLs
        # will set starting levels per-ship.
        super().__init__(max_power=max_power, level=level)
        self.current_layers: int = 0
        self.recharge_progress: float = 0.0

    @property
    def max_layers(self) -> int:
        return self.effective_power // 2

    def on_power_changed(self) -> None:
        # Power went up or down. Clamp current layers to the new cap.
        if self.current_layers > self.max_layers:
            self.current_layers = self.max_layers
            self.recharge_progress = 0.0

    def on_damaged(self) -> None:
        # Damage reduces effective_power; might reduce max_layers below current.
        if self.current_layers > self.max_layers:
            self.current_layers = self.max_layers
            self.recharge_progress = 0.0

    def tick(self, dt: float) -> None:
        super().tick(dt)
        if self.current_layers >= self.max_layers:
            self.recharge_progress = 0.0
            return
        if not self.is_operational:
            self.recharge_progress = 0.0
            return
        # Manning the shields room speeds recharge by ~11% (-10% recharge time).
        manning_mult = 1.0 / 0.9 if self.manning_crew is not None else 1.0
        self.recharge_progress += dt * manning_mult
        while (
            self.recharge_progress >= RECHARGE_TIME_PER_LAYER
            and self.current_layers < self.max_layers
        ):
            self.current_layers += 1
            self.recharge_progress -= RECHARGE_TIME_PER_LAYER
        if self.current_layers >= self.max_layers:
            self.recharge_progress = 0.0
