"""EncounterKind — what kind of encounter a beacon triggers."""

from __future__ import annotations

from enum import Enum


class EncounterKind(str, Enum):
    COMBAT = "combat"
    EVENT = "event"
    STORE = "store"
    EMPTY = "empty"
    FINAL_BOSS = "final_boss"
