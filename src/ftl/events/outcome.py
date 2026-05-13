"""The result of a Choice: rewards, combat triggers, modifiers, flag changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.core.game import Run


@dataclass
class Outcome:
    id: str
    text: str = ""
    scrap: int = 0
    fuel: int = 0
    missiles: int = 0
    drone_parts: int = 0
    hull_damage: int = 0
    starts_combat: bool = False
    enemy_ship_id: str | None = None
    set_flags: list[str] = field(default_factory=list)
    clear_flags: list[str] = field(default_factory=list)

    def apply(self, run: Run) -> None:
        """Apply this outcome's effects to the active run."""
        run.scrap += self.scrap
        run.fuel += self.fuel
        run.missiles += self.missiles
        run.drone_parts += self.drone_parts
        for flag in self.set_flags:
            run.story_flags.add(flag)
        for flag in self.clear_flags:
            run.story_flags.discard(flag)
        if self.hull_damage and run.player_ship is not None:
            run.player_ship.hull.damage(self.hull_damage)
