#!/usr/bin/env python
"""Helixfall — top-level launcher.

Run `python helixfall.py` from the repo root to start the game. This file
bootstraps `src/` onto sys.path so the `ftl` package is importable without
needing `pip install -e .`, then delegates to the package's main().

For development installs use `python -m ftl` instead.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    src = Path(__file__).resolve().parent / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> None:
    _ensure_src_on_path()
    from ftl.__main__ import main as run

    run()


if __name__ == "__main__":
    main()
