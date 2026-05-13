"""Project-wide constants, paths, and broad tuning knobs.

As content matures, gameplay tuning migrates to YAML; this file stays for
constants the engine itself cares about (paths, window dims, sim rate).
"""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT: Path = Path(__file__).resolve().parent
REPO_ROOT: Path = PACKAGE_ROOT.parent.parent
CONTENT_DIR: Path = REPO_ROOT / "content"
STORY_DIR: Path = REPO_ROOT / "story"
ASSETS_DIR: Path = REPO_ROOT / "assets"
SAVES_DIR: Path = REPO_ROOT / "saves"

WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720
WINDOW_TITLE: str = "FTL (working title)"

SIM_TICKS_PER_SECOND: int = 60
SIM_DT: float = 1.0 / SIM_TICKS_PER_SECOND

DEFAULT_HULL_HP: int = 30
DEFAULT_STARTING_SCRAP: int = 30
DEFAULT_STARTING_FUEL: int = 16
DEFAULT_STARTING_MISSILES: int = 8
DEFAULT_STARTING_DRONE_PARTS: int = 0
