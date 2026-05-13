"""Ship hull HP — the thing that kills you when it hits zero."""

from __future__ import annotations

from dataclasses import dataclass

from ftl.config import DEFAULT_HULL_HP


@dataclass
class Hull:
    current: int = DEFAULT_HULL_HP
    maximum: int = DEFAULT_HULL_HP

    def damage(self, amount: int) -> None:
        self.current = max(0, self.current - amount)

    def repair(self, amount: int) -> None:
        self.current = min(self.maximum, self.current + amount)

    @property
    def destroyed(self) -> bool:
        return self.current <= 0
