"""A Sector groups a set of beacons under a faction + theme + event pools."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Sector:
    id: str
    name: str
    faction: str = ""
    theme: str = ""
    event_pools: list[str] = field(default_factory=list)
