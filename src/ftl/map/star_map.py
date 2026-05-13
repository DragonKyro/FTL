"""StarMap — a Sector's beacon graph plus current jump position."""

from __future__ import annotations

from dataclasses import dataclass, field

from ftl.map.beacon import Beacon


@dataclass
class StarMap:
    sector_id: str
    beacons: dict[str, Beacon] = field(default_factory=dict)
    current_beacon: str | None = None
    exit_beacon: str | None = None

    def add_beacon(self, beacon: Beacon) -> None:
        self.beacons[beacon.id] = beacon

    def neighbors(self, beacon_id: str) -> list[Beacon]:
        beacon = self.beacons.get(beacon_id)
        if beacon is None:
            return []
        return [self.beacons[bid] for bid in beacon.connections if bid in self.beacons]
