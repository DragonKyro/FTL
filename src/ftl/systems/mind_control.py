"""MindControlSystem — temporarily turn an enemy crew member.

Activation:
- Player presses M → enters targeting mode → clicks an enemy crew dot.
- CombatEngine.try_mind_control(target_crew) does the work:
  - Saves target's original team
  - Flips team to caller's team for `ACTIVE_SECONDS`
  - When duration ends, restoration restores the original team
- Cooldown after duration ends.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.systems.system import System

if TYPE_CHECKING:
    from ftl.crew.crew import Crew

ACTIVE_SECONDS: float = 10.0
COOLDOWN_SECONDS: float = 30.0


class MindControlSystem(System):
    name = "mind_control"

    def __init__(self, max_power: int = 3, level: int = 1) -> None:
        super().__init__(max_power=max_power, level=level)
        self.active_remaining: float = 0.0
        self.cooldown_remaining: float = 0.0
        self.target_crew: Crew | None = None
        self._original_team: str | None = None

    @property
    def is_active(self) -> bool:
        return self.active_remaining > 0.0

    def begin(self, target: Crew) -> bool:
        if not self.is_operational:
            return False
        if self.cooldown_remaining > 0.0:
            return False
        if self.is_active:
            return False
        if getattr(target.behavior, "mind_control_immune", False):
            return False
        self.target_crew = target
        self._original_team = target.team
        target.team = self._opposite_team(target.team)
        self.active_remaining = ACTIVE_SECONDS
        return True

    @staticmethod
    def _opposite_team(team: str) -> str:
        return "player" if team == "enemy" else "enemy"

    def _restore(self) -> None:
        if self.target_crew is not None and self._original_team is not None:
            # Only restore if alive; dead targets stay dead.
            if self.target_crew.alive:
                self.target_crew.team = self._original_team
        self.target_crew = None
        self._original_team = None

    def tick(self, dt: float) -> None:
        super().tick(dt)
        if self.active_remaining > 0.0:
            # Target died? End early.
            if self.target_crew is not None and not self.target_crew.alive:
                self.active_remaining = 0.0
                self._restore()
                self.cooldown_remaining = COOLDOWN_SECONDS
                return
            self.active_remaining = max(0.0, self.active_remaining - dt)
            if self.active_remaining <= 0.0:
                self._restore()
                self.cooldown_remaining = COOLDOWN_SECONDS
        elif self.cooldown_remaining > 0.0:
            self.cooldown_remaining = max(0.0, self.cooldown_remaining - dt)
