"""Save / load. Phase-0 stub — Phase-2+ chooses format (JSON likely)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.core.game import Run


class SaveManager:
    def __init__(self, root: Path) -> None:
        self.root: Path = root

    def save(self, run: Run, slot: str = "auto") -> None:
        return None

    def load(self, slot: str = "auto") -> Run | None:
        return None
