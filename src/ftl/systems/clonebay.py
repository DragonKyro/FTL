"""ClonebaySystem — revives fallen crew after a timer.

Alternative to medbay. When a crew member dies aboard a ship that has
a clonebay, the engine routes them into the clonebay's queue. The
clonebay ticks each dead crew's `clone_progress`. When ready, the crew
is revived in the clonebay's room with 50% HP, current_ship reset to
their home_ship.

If the clonebay is destroyed (damage >= level) at any point, the queue
is *cleared* — those crew are permanently dead. Powering the clonebay
back up after a cull doesn't bring them back.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.systems.system import System

if TYPE_CHECKING:
    from ftl.crew.crew import Crew
    from ftl.ships.room import Room
    from ftl.ships.ship import Ship


CLONE_TIME_SECONDS: float = 20.0
CLONE_REVIVE_HP_FRACTION: float = 0.5


class ClonebaySystem(System):
    name = "clonebay"

    def __init__(self, max_power: int = 4, level: int = 2) -> None:
        super().__init__(max_power=max_power, level=level)
        self.clone_queue: list[Crew] = []

    def enqueue(self, crew: Crew) -> None:
        crew.clone_progress = 0.0
        if crew not in self.clone_queue:
            self.clone_queue.append(crew)

    def tick(self, dt: float) -> None:
        super().tick(dt)
        if self.damage >= self.level:
            # Catastrophic clonebay loss: the queue is gone.
            self.clone_queue.clear()
            return
        if not self.is_operational:
            return
        if not self.clone_queue:
            return
        head = self.clone_queue[0]
        head.clone_progress += dt
        # Higher level = faster clone (per FTL convention).
        time_required = CLONE_TIME_SECONDS / max(1, self.level - 1)
        if head.clone_progress >= time_required:
            self._revive(head)
            self.clone_queue.pop(0)

    def _revive(self, crew: Crew) -> None:
        if crew.home_ship is None:
            return
        home: Ship = crew.home_ship
        room = self._clonebay_room(home)
        if room is None or not room.tiles:
            return
        crew.hp = float(crew.max_hp) * CLONE_REVIVE_HP_FRACTION
        crew.current_ship = home
        crew.current_tile = room.tiles[0]
        crew.path = []
        crew.move_progress = 0.0
        crew.clone_progress = 0.0
        # Re-import to avoid circular import at module load.
        from ftl.crew.crew import CrewState

        crew.state = CrewState.IDLE
        # Re-add to ship.crew if not present.
        if crew not in home.crew:
            home.crew.append(crew)

    def _clonebay_room(self, ship: Ship) -> Room | None:
        for room in ship.rooms.values():
            if room.system is self:
                return room
        return None
