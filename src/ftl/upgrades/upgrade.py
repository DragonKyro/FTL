"""Upgrade transactions — buy a system/weapon/drone/augment, level up a system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.core.game import Run


@dataclass
class Upgrade:
    id: str
    name: str
    cost: int = 0
    description: str = ""

    def can_afford(self, run: Run) -> bool:
        return run.scrap >= self.cost

    def apply(self, run: Run) -> bool:
        if not self.can_afford(run):
            return False
        run.scrap -= self.cost
        self._on_apply(run)
        return True

    def _on_apply(self, run: Run) -> None:
        """Subclass-specific transaction effect (level up, install, etc.)."""
