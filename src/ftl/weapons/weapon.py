"""Weapon base + WeaponStats.

The hybrid content model in one file: `WeaponStats` is the immutable
description of a weapon (loaded from YAML); `Weapon` is the stateful runtime
wrapper around it (charge progress, powered/unpowered, target room, firing).

Family subclasses (`BeamWeapon`, `LaserWeapon`, ...) exist for future
behavioral differentiation. Phase 1 firing logic lives in
`combat.engine.CombatEngine`; family classes are pass-throughs for now.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeaponStats:
    id: str
    name: str
    family: str  # "beam" | "laser" | "missile" | "bomb" | "ion" | "flak"
    damage: int = 0
    charge_time: float = 10.0
    shield_pierce: int = 0
    breach_chance: float = 0.0
    fire_chance: float = 0.0
    stun_seconds: float = 0.0
    ion_damage: int = 0
    crew_damage: int = 0
    system_damage: int = 0
    beam_length: int = 0          # how many rooms a beam crosses
    beam_room_damage: int = 0     # damage applied per room a beam touches
    projectile_count: int = 1     # >1 for flak / multi-shot
    missile_cost: int = 0
    power_required: int = 1
    cost: int = 50
    sprite_key: str = ""
    sfx_key: str = ""


class Weapon:
    """Runtime wrapper around a WeaponStats.

    Charges over time while `powered`. The CombatEngine fires it when
    `ready` and resets charge via `reset_charge()`. Targeting is sticky:
    once `target_room_id` is set, the weapon reuses it across shots until
    the player or AI reassigns.
    """

    def __init__(self, stats: WeaponStats) -> None:
        self.stats: WeaponStats = stats
        self.powered: bool = False
        self.charge_progress: float = 0.0
        self.target_room_id: str | None = None

    @property
    def ready(self) -> bool:
        return self.powered and self.charge_progress >= self.stats.charge_time

    @property
    def consumes_missile(self) -> bool:
        return self.stats.missile_cost > 0

    @property
    def bypasses_shields(self) -> bool:
        return self.stats.shield_pierce >= 5

    def tick(self, dt: float) -> None:
        if self.powered and self.charge_progress < self.stats.charge_time:
            self.charge_progress = min(
                self.stats.charge_time, self.charge_progress + dt
            )
        elif not self.powered and self.charge_progress > 0.0:
            # Unpowering a weapon loses charge progress (FTL canon).
            self.charge_progress = 0.0

    def reset_charge(self) -> None:
        self.charge_progress = 0.0
