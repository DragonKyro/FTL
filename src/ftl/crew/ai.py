"""Crew AI stubs — what a friendly crew or boarder does when not explicitly ordered."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.crew.crew import Crew


class CrewAI:
    """Chooses tasks for friendly crew not under direct order (auto-fight, auto-repair)."""

    def update(self, crew: Crew, dt: float) -> None:
        return None


class BoarderAI:
    """Drives hostile boarders: pick target room/system, engage, retreat if losing."""

    def update(self, crew: Crew, dt: float) -> None:
        return None
