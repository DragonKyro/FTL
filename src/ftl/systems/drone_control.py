"""DroneControlSystem — powers active drones in the ship's drone slots.

`level` is the number of drone slots available. `current_power` is the
total power budget for active drones. Each drone has
`stats.power_required`; a drone is "powered" if and only if the system
has enough remaining capacity when budgeting in slot order.

Powering individual drones works the same way the weapons system gates
its weapons. The CombatEngine's drone_runtime asks each drone if it's
powered before doing anything.
"""

from __future__ import annotations

from ftl.systems.system import System


class DroneControlSystem(System):
    name = "drone_control"

    def __init__(self, max_power: int = 8, level: int = 4) -> None:
        super().__init__(max_power=max_power, level=level)
