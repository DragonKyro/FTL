"""SensorsSystem — passive visibility for the *opposing* ship.

Visibility level (from this ship's sensors) determines how much
information about the enemy ship the player sees. Higher manned
sensors see deeper.

The visibility scale used by the UI:
- 1: enemy room outlines + hull bar only
- 2: + room labels, oxygen tint, fire, breach overlays
- 3: + crew positions on the enemy
- 4: + (Phase 4+) enemy weapon charge bars

The actual integer is computed by `combat.visibility.enemy_visibility`.
"""

from __future__ import annotations

from ftl.systems.system import System


class SensorsSystem(System):
    name = "sensors"

    def __init__(self, max_power: int = 4, level: int = 4) -> None:
        # Default level = 4 → up to four power slots → full visibility at
        # full power. Phase 4+ ship YAML can override per-ship.
        super().__init__(max_power=max_power, level=level)

    @property
    def visibility_level(self) -> int:
        """Effective visibility, before manning bonus."""
        if not self.is_operational:
            return 1
        return max(1, self.effective_power)
