"""Procedural beacon graph generation for a sector.

Phase 4 implementation:
- Scatter ~12 beacons in a 6×3 grid with jitter
- Connect each to its 2–3 nearest neighbors (Euclidean distance)
- Mark first as start, last as exit
- Assign per-beacon encounter type:
  60% combat / 20% event / 10% store / 10% empty
- Start + exit beacons get EMPTY (no encounter on landing)
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ftl.map.beacon import Beacon
from ftl.map.encounter_kind import EncounterKind
from ftl.map.star_map import StarMap

if TYPE_CHECKING:
    from random import Random

    from ftl.map.sector import Sector


BEACON_COUNT: int = 12
GRID_COLS: int = 6
GRID_ROWS: int = 3
GRID_SPACING_X: float = 90.0
GRID_SPACING_Y: float = 90.0
GRID_JITTER: float = 22.0
MAX_NEIGHBORS_PER_BEACON: int = 3
MAX_CONNECTION_DIST: float = 140.0


def generate_star_map(sector: Sector, rng: Random) -> StarMap:
    beacons = _scatter_beacons(sector, rng)
    _connect_beacons(beacons)
    _assign_encounters(beacons, rng)
    start = beacons[0]
    exit_ = beacons[-1]
    start.encounter_id = EncounterKind.EMPTY.value
    exit_.encounter_id = EncounterKind.EMPTY.value
    start.visited = True
    return StarMap(
        sector_id=sector.id,
        beacons={b.id: b for b in beacons},
        current_beacon=start.id,
        exit_beacon=exit_.id,
    )


def _scatter_beacons(sector: Sector, rng: Random) -> list[Beacon]:
    """Pick BEACON_COUNT cells from a 6×3 grid, jitter them within the cell."""
    cells: list[tuple[int, int]] = [
        (c, r) for c in range(GRID_COLS) for r in range(GRID_ROWS)
    ]
    rng.shuffle(cells)
    chosen: list[tuple[int, int]] = cells[:BEACON_COUNT]
    # Sort left-to-right so the leftmost ends up as start and rightmost as exit.
    chosen.sort(key=lambda cr: (cr[0], cr[1]))
    beacons: list[Beacon] = []
    for idx, (col, row) in enumerate(chosen):
        bx = col * GRID_SPACING_X + rng.uniform(-GRID_JITTER, GRID_JITTER)
        by = row * GRID_SPACING_Y + rng.uniform(-GRID_JITTER, GRID_JITTER)
        beacons.append(
            Beacon(
                id=f"{sector.id}_b{idx:02d}",
                x=bx,
                y=by,
                sector_id=sector.id,
            )
        )
    return beacons


def _connect_beacons(beacons: list[Beacon]) -> None:
    """Each beacon gets edges to its nearest neighbors within MAX_CONNECTION_DIST."""
    by_id = {b.id: b for b in beacons}
    for b in beacons:
        ranked = sorted(
            (other for other in beacons if other is not b),
            key=lambda o: math.hypot(o.x - b.x, o.y - b.y),
        )
        added = 0
        for other in ranked:
            if added >= MAX_NEIGHBORS_PER_BEACON:
                break
            dist = math.hypot(other.x - b.x, other.y - b.y)
            if dist > MAX_CONNECTION_DIST:
                break
            if other.id not in b.connections:
                b.connections.append(other.id)
            if b.id not in other.connections:
                other.connections.append(b.id)
            added += 1
    # Guarantee reachability: if exit unreachable from start, force chain.
    if not _path_exists(beacons[0], beacons[-1], by_id):
        for a, b in zip(beacons, beacons[1:]):
            if b.id not in a.connections:
                a.connections.append(b.id)
            if a.id not in b.connections:
                b.connections.append(a.id)


def _path_exists(start: Beacon, goal: Beacon, by_id: dict[str, Beacon]) -> bool:
    seen: set[str] = {start.id}
    frontier: list[str] = [start.id]
    while frontier:
        current_id = frontier.pop()
        if current_id == goal.id:
            return True
        current = by_id[current_id]
        for neighbor_id in current.connections:
            if neighbor_id not in seen:
                seen.add(neighbor_id)
                frontier.append(neighbor_id)
    return False


def _assign_encounters(beacons: list[Beacon], rng: Random) -> None:
    for b in beacons:
        r = rng.random()
        if r < 0.60:
            b.encounter_id = EncounterKind.COMBAT.value
        elif r < 0.80:
            b.encounter_id = EncounterKind.EVENT.value
        elif r < 0.90:
            b.encounter_id = EncounterKind.STORE.value
            b.has_store = True
        else:
            b.encounter_id = EncounterKind.EMPTY.value
