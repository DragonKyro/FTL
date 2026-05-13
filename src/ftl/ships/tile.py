"""A single grid cell within a Room. Crew stand on tiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.crew.crew import Crew


@dataclass
class Tile:
    x: int
    y: int
    occupant: Crew | None = None
