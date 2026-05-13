"""Heuristic enemy pilot AI.

Phase 1 AI ("skiff" profile):
- Allocates power once at init: 1 weapons, 2 shields, 1 piloting (cap at
  what the ship has and what fits the reactor budget).
- Picks a target room on the opponent each tick. Preference order:
  weapons room → shield room → engines → random.
- Sets that room as every powered weapon's target. Re-targets only when
  the current target's system is fully damaged.

The CombatEngine handles actual firing; the AI just sets targets.
"""

from __future__ import annotations

from random import Random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import Ship
    from ftl.weapons.weapon import Weapon


# Room id preference order (matches our content/ship YAMLs).
_PREFERRED_TARGETS: tuple[str, ...] = (
    "gun_bay",
    "shield_room",
    "engine_room",
    "bridge",
)


class EnemyPilot:
    def __init__(self, self_ship: Ship, opponent: Ship, rng: Random) -> None:
        self.self_ship: Ship = self_ship
        self.opponent: Ship = opponent
        self.rng: Random = rng
        self._init_power()
        self._power_weapons()

    def _init_power(self) -> None:
        """Default allocation: shields-1, weapons-1, piloting-1, then fill shields up."""
        budget = self.self_ship.max_reactor_power

        def assign(system_name: str, amount: int) -> int:
            system = self.self_ship.systems.get(system_name)
            if system is None or amount <= 0:
                return 0
            allowed = min(amount, system.max_power, budget)
            system.set_power(allowed)
            return allowed

        budget -= assign("piloting", 1)
        budget -= assign("weapons", 1)
        budget -= assign("shields", min(2, budget))
        # Anything left, top up shields.
        if budget > 0:
            shields = self.self_ship.systems.get("shields")
            if shields is not None:
                current = shields.current_power
                allowed = min(current + budget, shields.max_power)
                shields.set_power(allowed)

    def _power_weapons(self) -> None:
        """Power every weapon the weapons system can support."""
        weapons_system = self.self_ship.systems.get("weapons")
        if weapons_system is None:
            return
        budget = weapons_system.effective_power
        for weapon in self.self_ship.weapons:
            if budget >= weapon.stats.power_required:
                weapon.powered = True
                budget -= weapon.stats.power_required
            else:
                weapon.powered = False

    def _pick_target(self) -> str | None:
        for room_id in _PREFERRED_TARGETS:
            room = self.opponent.rooms.get(room_id)
            if room is None:
                continue
            if room.system is None:
                continue
            if room.system.damage >= room.system.level:
                # System fully damaged — skip; move to next preference.
                continue
            return room_id
        room_ids = list(self.opponent.rooms.keys())
        if not room_ids:
            return None
        return self.rng.choice(room_ids)

    def tick(self, dt: float) -> None:
        # Re-sync weapon power against the weapons system in case damage
        # has reduced its capacity.
        self._power_weapons()
        target_id = self._pick_target()
        if target_id is None:
            return
        for weapon in self.self_ship.weapons:
            if not weapon.powered:
                continue
            if weapon.target_room_id is None or self._should_retarget(weapon):
                weapon.target_room_id = target_id

    def _should_retarget(self, weapon: Weapon) -> bool:
        if weapon.target_room_id is None:
            return True
        current = self.opponent.rooms.get(weapon.target_room_id)
        if current is None or current.system is None:
            return True
        return current.system.damage >= current.system.level
