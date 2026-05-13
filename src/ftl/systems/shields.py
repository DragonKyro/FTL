"""ShieldsSystem — each 2 power = 1 shield layer."""

from __future__ import annotations

from ftl.systems.system import System


class ShieldsSystem(System):
    name = "shields"

    def __init__(self, max_power: int = 8, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.current_layers: int = 0
        self.recharge_progress: float = 0.0

    @property
    def max_layers(self) -> int:
        return self.effective_power // 2
