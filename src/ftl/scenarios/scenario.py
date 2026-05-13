"""A Scenario describes the starting configuration of a run.

Pick a Scenario at run start: which ship, which loadout, which difficulty,
which starting sector. Scenarios are authored as YAML under `content/ships/`
(the ship + loadout) and resolved into a Scenario object here.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Scenario:
    id: str
    name: str
    ship_id: str
    starting_weapons: list[str] = field(default_factory=list)
    starting_drones: list[str] = field(default_factory=list)
    starting_augments: list[str] = field(default_factory=list)
    starting_crew: list[str] = field(default_factory=list)
    starting_scrap: int = 30
    starting_fuel: int = 16
    starting_missiles: int = 8
    starting_drone_parts: int = 0
    difficulty: str = "normal"
