"""Cached `arcade.Text` factory.

Calling `arcade.draw_text(...)` every frame is slow — Arcade rebuilds
the text glyph buffer each call and warns about it. `arcade.Text`
objects keep the buffer between draws.

This module hands out per-scene caches: every call site picks a stable
`key`, the cache builds the `Text` object once, and subsequent calls
just update `.text` / `.x` / `.y` / `.color` in place. The first call
is no faster than `draw_text`; the 60+ frames per second that follow
are cheap.
"""

from __future__ import annotations

from typing import Any

import arcade


class TextCache:
    """Mapping of stable key → reusable `arcade.Text` instance."""

    def __init__(self) -> None:
        self._items: dict[Any, arcade.Text] = {}

    def draw(
        self,
        key: Any,
        text: str,
        x: float,
        y: float,
        color: tuple[int, int, int] | tuple[int, int, int, int],
        font_size: float,
        *,
        anchor_x: str = "left",
        anchor_y: str = "baseline",
        bold: bool = False,
    ) -> arcade.Text:
        """Draw `text` at (x, y), reusing a cached Text object.

        Mutates the cached instance to match the requested params, then
        draws it. The first call for a given key builds the Text; later
        calls are O(1) updates."""
        item = self._items.get(key)
        if item is None:
            item = arcade.Text(
                text, x, y, color, font_size,
                anchor_x=anchor_x, anchor_y=anchor_y, bold=bold,
            )
            self._items[key] = item
        else:
            if item.text != text:
                item.text = text
            if item.x != x:
                item.x = x
            if item.y != y:
                item.y = y
            if item.color != color:
                item.color = color
            if item.font_size != font_size:
                item.font_size = font_size
        item.draw()
        return item

    def clear(self) -> None:
        self._items.clear()
