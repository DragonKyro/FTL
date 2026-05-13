"""Base class for ship systems.

A System wraps power, level (cap on power), damage (bars taken), ion
charge (temporary disable), an optional manning crew member, and a
"hacked" flag set by an enemy HackingSystem while it's active. Subclasses
model specific systems (weapons, shields, engines, ...).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.crew.crew import Crew


class System:
    """Base system."""

    name: str = "system"

    def __init__(self, max_power: int = 8, level: int = 1) -> None:
        self.max_power: int = max_power
        self.level: int = level
        self.current_power: int = 0
        self.damage: int = 0
        self.ion_charge: float = 0.0
        self.hacked: bool = False
        self.manning_crew: Crew | None = None

    @property
    def effective_power(self) -> int:
        if self.hacked:
            return 0
        return max(0, self.current_power - self.damage)

    @property
    def is_operational(self) -> bool:
        return self.effective_power > 0 and self.ion_charge <= 0 and not self.hacked

    def set_power(self, value: int) -> None:
        self.current_power = max(0, min(value, self.max_power, self.level))
        self.on_power_changed()

    def take_damage(self, amount: int) -> None:
        self.damage = min(self.level, self.damage + amount)
        self.on_damaged()

    def repair(self, amount: int) -> None:
        self.damage = max(0, self.damage - amount)

    def on_power_changed(self) -> None:
        """Override hook."""

    def on_damaged(self) -> None:
        """Override hook."""

    def tick(self, dt: float) -> None:
        if self.ion_charge > 0:
            self.ion_charge = max(0.0, self.ion_charge - dt)
