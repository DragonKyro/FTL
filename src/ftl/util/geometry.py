"""Geometry helpers."""

from __future__ import annotations

import math


def distance(ax: float, ay: float, bx: float, by: float) -> float:
    return math.hypot(bx - ax, by - ay)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
