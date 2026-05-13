"""Galaxy — the cross-sector route the player threads through over a run.

In FTL the route is linear (sectors 1..8). For our Multiverse-scale ambition
we leave room for a richer graph: multiple "dimensions" / branches the
player can choose between when leaving a sector.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GalaxyNode:
    sector_id: str
    next_sectors: list[str] = field(default_factory=list)


@dataclass
class Galaxy:
    nodes: dict[str, GalaxyNode] = field(default_factory=dict)
    start_sector: str = ""

    def add_node(self, node: GalaxyNode) -> None:
        self.nodes[node.sector_id] = node
