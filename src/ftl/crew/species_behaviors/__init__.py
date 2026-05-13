"""Concrete `SpeciesBehavior` implementations + factory.

The factory `behavior_for(species_id)` returns the right subclass for a
given species. Unknown ids fall back to `SapienBehavior` (the no-op
baseline) so the game never crashes on missing trait code.
"""

from __future__ import annotations

from ftl.crew.species import SpeciesBehavior
from ftl.crew.species_behaviors.halene import HaleneBehavior
from ftl.crew.species_behaviors.mhirsa import MhirsaBehavior
from ftl.crew.species_behaviors.sapien import SapienBehavior

_REGISTRY: dict[str, type[SpeciesBehavior]] = {
    "sapien": SapienBehavior,
    "halene": HaleneBehavior,
    "mhirsa": MhirsaBehavior,
}


def behavior_for(species_id: str) -> SpeciesBehavior:
    cls = _REGISTRY.get(species_id, SapienBehavior)
    return cls()


__all__ = [
    "HaleneBehavior",
    "MhirsaBehavior",
    "SapienBehavior",
    "behavior_for",
]
