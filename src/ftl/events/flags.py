"""Persistent story flags — set by event outcomes, checked by triggers/choices."""

from __future__ import annotations


class StoryFlags:
    """Thin wrapper over a set so we can swap implementations later."""

    def __init__(self) -> None:
        self._flags: set[str] = set()

    def set(self, flag: str) -> None:
        self._flags.add(flag)

    def clear(self, flag: str) -> None:
        self._flags.discard(flag)

    def has(self, flag: str) -> bool:
        return flag in self._flags

    def all(self) -> frozenset[str]:
        return frozenset(self._flags)
