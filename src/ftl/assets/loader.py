"""Texture / sound cache with placeholder fallback.

Phase-0 stub. When real assets exist, this returns them; otherwise it falls
back to procedurally drawn placeholders (colored rects, simple shapes) so
the rest of the engine can stay agnostic.
"""

from __future__ import annotations

from pathlib import Path

import arcade

from ftl.config import ASSETS_DIR


class AssetCache:
    def __init__(self, root: Path = ASSETS_DIR) -> None:
        self.root: Path = root
        self._textures: dict[str, arcade.Texture] = {}

    def texture(self, key: str) -> arcade.Texture | None:
        if key in self._textures:
            return self._textures[key]
        path = self.root / "sprites" / f"{key}.png"
        if not path.exists():
            return None
        tex: arcade.Texture = arcade.load_texture(path)
        self._textures[key] = tex
        return tex
