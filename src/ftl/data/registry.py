"""In-memory registry of all content definitions.

Populated at startup by walking `content/` and `story/`. Code looks up
definitions by id, e.g. `registry.weapons["pulse_lance_mk1"]`.
"""

from __future__ import annotations

from pathlib import Path

from ftl.config import CONTENT_DIR, STORY_DIR
from ftl.data.loader import iter_yaml_files, load_def
from ftl.data.schemas import (
    CONTENT_SCHEMAS,
    STORY_SCHEMAS,
    AugmentDef,
    ContentDef,
    DroneDef,
    EventDef,
    FactionDef,
    SectorDef,
    ShipDef,
    SpeciesDef,
    SystemDef,
    WeaponDef,
)


class Registry:
    """Holds parsed content keyed by category and id."""

    def __init__(self) -> None:
        self.weapons: dict[str, WeaponDef] = {}
        self.drones: dict[str, DroneDef] = {}
        self.augments: dict[str, AugmentDef] = {}
        self.species: dict[str, SpeciesDef] = {}
        self.systems: dict[str, SystemDef] = {}
        self.ships: dict[str, ShipDef] = {}
        self.factions: dict[str, FactionDef] = {}
        self.sectors: dict[str, SectorDef] = {}
        self.events: dict[str, EventDef] = {}

    def load_all(
        self,
        content_root: Path = CONTENT_DIR,
        story_root: Path = STORY_DIR,
    ) -> None:
        for subdir, schema in CONTENT_SCHEMAS.items():
            self._load_dir(content_root / subdir, schema)
        for subdir, schema in STORY_SCHEMAS.items():
            self._load_dir(story_root / subdir, schema)

    def _load_dir(self, root: Path, schema: type[ContentDef]) -> None:
        for path in iter_yaml_files(root):
            definition = load_def(path, schema)
            self._register(definition)

    def _register(self, definition: ContentDef) -> None:
        if isinstance(definition, WeaponDef):
            self.weapons[definition.id] = definition
        elif isinstance(definition, DroneDef):
            self.drones[definition.id] = definition
        elif isinstance(definition, AugmentDef):
            self.augments[definition.id] = definition
        elif isinstance(definition, SpeciesDef):
            self.species[definition.id] = definition
        elif isinstance(definition, SystemDef):
            self.systems[definition.id] = definition
        elif isinstance(definition, ShipDef):
            self.ships[definition.id] = definition
        elif isinstance(definition, FactionDef):
            self.factions[definition.id] = definition
        elif isinstance(definition, SectorDef):
            self.sectors[definition.id] = definition
        elif isinstance(definition, EventDef):
            self.events[definition.id] = definition
