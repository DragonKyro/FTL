"""A Beacon is one jump destination on a Sector map."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Beacon:
    id: str
    x: float
    y: float
    sector_id: str
    visited: bool = False
    has_store: bool = False
    has_distress: bool = False
    has_quest: bool = False
    encounter_id: str | None = None
    connections: list[str] = field(default_factory=list)
