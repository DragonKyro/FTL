"""Shield layers — energy bubbles stripped by lasers, ignored by missiles/bombs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ShieldLayer:
    strength: int = 1
