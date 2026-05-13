"""Doors connect adjacent rooms.

Phase 2 doors are inferred from room geometry. Each door sits on the
edge between two adjacent rooms and connects exactly one tile pair
(one tile in each room).

Phase 3 gives doors HP. A door is conceptually always "open" unless
the player has explicitly `force_closed` it. Force-closed doors block
hostile movement, oxygen flow, and fire spread; the home team walks
through them (the door auto-opens for them).

Hostile crew blocked by a force-closed door **attack the door** each
tick until its HP reaches 0, at which point the door is *destroyed*
(force_closed permanently False; passable to everyone, forever).

DoorsSystem at the ship level controls the *default* HP cap when the
ship is built. Higher levels = stronger doors / blast doors.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Door:
    id: str
    room_a: str
    room_b: str
    tile_a: tuple[int, int]  # global coord of the room_a-side tile
    tile_b: tuple[int, int]  # global coord of the room_b-side tile
    force_closed: bool = False
    level: int = 1
    hp: int = 4
    max_hp: int = 4
    destroyed: bool = False
    ionized: bool = False
    damage_accum: float = 0.0

    @property
    def is_open(self) -> bool:
        return self.destroyed or not self.force_closed

    def passable_for(self, is_home_team: bool) -> bool:
        """Can a crew of the given team pass this door right now?

        Destroyed doors are passable to all. Force-closed doors are
        passable to the home team only (auto-open), boarders bounce off.
        """
        if self.destroyed:
            return True
        if self.force_closed and not is_home_team:
            return False
        return True

    def take_door_hit(self, amount: float) -> bool:
        """Apply melee damage to this door. Returns True if it just broke.

        Sub-1.0 damage accumulates so that small per-tick fractions add up
        across many ticks. Callers don't have to track their own accumulator.
        """
        if self.destroyed:
            return False
        self.damage_accum += amount
        whole = int(self.damage_accum)
        if whole > 0:
            self.damage_accum -= whole
            self.hp -= whole
            if self.hp <= 0:
                self.hp = 0
                self.destroyed = True
                self.force_closed = False
                return True
        return False

    def toggle(self) -> None:
        if self.destroyed:
            return
        self.force_closed = not self.force_closed

    def connects_tiles(self, coord_a: tuple[int, int], coord_b: tuple[int, int]) -> bool:
        pair = {coord_a, coord_b}
        return pair == {self.tile_a, self.tile_b}
