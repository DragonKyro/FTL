"""Faction descriptor — who controls a sector and who they're hostile to."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Faction:
    id: str
    name: str
    hostile_to: list[str] = field(default_factory=list)
