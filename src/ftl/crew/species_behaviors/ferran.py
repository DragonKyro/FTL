"""Ferran — crystalline beings; can lock down their current room.

Phase 4 trait: when activated (player intent), the Ferran force-closes
every door of their current room for `LOCKDOWN_DURATION` seconds; then
a cooldown blocks re-activation. Boarders can't pass these doors
during lockdown; force-closed doors auto-restore when the lockdown
ends.

Activation is via the engine command surface (Phase 4 wires this to
a key — `L`). For now the behavior exposes `activate_lockdown(crew)`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.crew.species import SpeciesBehavior

if TYPE_CHECKING:
    from ftl.crew.crew import Crew


LOCKDOWN_DURATION: float = 6.0
LOCKDOWN_COOLDOWN: float = 25.0


class FerranBehavior(SpeciesBehavior):
    def __init__(self) -> None:
        super().__init__()
        self.lockdown_active: float = 0.0
        self.lockdown_cooldown: float = 0.0
        self._locked_door_ids: set[str] = set()

    def can_activate(self) -> bool:
        return self.lockdown_active <= 0.0 and self.lockdown_cooldown <= 0.0

    def activate_lockdown(self, crew: Crew) -> bool:
        if not self.can_activate() or not crew.alive:
            return False
        room = crew.current_room()
        ship = crew.current_ship
        if room is None or ship is None:
            return False
        # Force-close every door bordering this room.
        self._locked_door_ids.clear()
        for door in ship.doors.values():
            if door.room_a == room.id or door.room_b == room.id:
                if not door.destroyed and not door.force_closed:
                    door.force_closed = True
                    self._locked_door_ids.add(door.id)
        self.lockdown_active = LOCKDOWN_DURATION
        return True

    def on_tick(self, crew: Crew, dt: float) -> None:
        if self.lockdown_active > 0:
            self.lockdown_active -= dt
            if self.lockdown_active <= 0:
                self.lockdown_active = 0.0
                self.lockdown_cooldown = LOCKDOWN_COOLDOWN
                self._release_locked_doors(crew)
        elif self.lockdown_cooldown > 0:
            self.lockdown_cooldown = max(0.0, self.lockdown_cooldown - dt)

    def _release_locked_doors(self, crew: Crew) -> None:
        ship = crew.current_ship
        if ship is None:
            return
        for door_id in list(self._locked_door_ids):
            door = ship.doors.get(door_id)
            if door is not None and not door.destroyed:
                door.force_closed = False
        self._locked_door_ids.clear()
