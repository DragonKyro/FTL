"""Yssari — bioluminescent telepathic amphibians; mind-control-immune.

Phase 4 trait: cannot be mind-controlled. The MindControlSystem checks
`behavior.mind_control_immune` before flipping a target's team.
"""

from __future__ import annotations

from ftl.crew.species import SpeciesBehavior


class YssariBehavior(SpeciesBehavior):
    @property
    def mind_control_immune(self) -> bool:
        return True
