"""Concrete `SpeciesBehavior` implementations + factory.

`behavior_for(species_id)` returns the right subclass for a given
species. Unknown ids fall back to `SapienBehavior` (no-op baseline).
"""

from __future__ import annotations

from ftl.crew.species import SpeciesBehavior
from ftl.crew.species_behaviors.choir import ChoirBehavior
from ftl.crew.species_behaviors.ferran import FerranBehavior
from ftl.crew.species_behaviors.halene import HaleneBehavior
from ftl.crew.species_behaviors.loam import LoamBehavior
from ftl.crew.species_behaviors.mhirsa import MhirsaBehavior
from ftl.crew.species_behaviors.sapien import SapienBehavior
from ftl.crew.species_behaviors.yssari import YssariBehavior

_REGISTRY: dict[str, type[SpeciesBehavior]] = {
    "sapien": SapienBehavior,
    "halene": HaleneBehavior,
    "mhirsa": MhirsaBehavior,
    "choir": ChoirBehavior,
    "ferran": FerranBehavior,
    "loam": LoamBehavior,
    "yssari": YssariBehavior,
}


def behavior_for(species_id: str) -> SpeciesBehavior:
    cls = _REGISTRY.get(species_id, SapienBehavior)
    return cls()


__all__ = [
    "ChoirBehavior",
    "FerranBehavior",
    "HaleneBehavior",
    "LoamBehavior",
    "MhirsaBehavior",
    "SapienBehavior",
    "YssariBehavior",
    "behavior_for",
]
