"""Procedural generation of beacon graphs and encounter assignments.

Phase-0 stub. Phase-3 implements real layout (scatter points, connect with
edge constraints, sample encounters from sector event pools).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.map.star_map import StarMap

if TYPE_CHECKING:
    from random import Random

    from ftl.map.sector import Sector


def generate_star_map(sector: Sector, rng: Random) -> StarMap:
    """Generate a beacon graph for the given sector. Stub: empty map."""
    return StarMap(sector_id=sector.id)
