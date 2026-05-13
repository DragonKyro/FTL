"""Choir — silver-pupiled mystics; precognition advantage at the helm.

Phase 4 trait: when manning piloting, contributes an extra +25% evasion
bonus on top of the baseline manning bonus. This is the only species-
specific manning bonus in the game so far.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.crew.species import SpeciesBehavior

if TYPE_CHECKING:
    from ftl.crew.crew import Crew


class ChoirBehavior(SpeciesBehavior):
    def manning_bonus(self, crew: Crew, system_name: str) -> float:
        if system_name == "piloting":
            return 0.25
        return 0.0
