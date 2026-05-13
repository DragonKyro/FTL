"""The damage application pipeline.

A single canonical function: `apply_damage(event, rng)`. The pipeline:

1. **Evasion roll.** Engines (and piloting manning) give a chance to miss.
2. **Shield absorption.** Lasers (any non-shield-piercing weapon) are
   absorbed one layer per hit. Missiles bypass.
3. **Hull damage.** Direct hp loss.
4. **System damage.** If the target room hosts a system, that system takes
   the same damage in bars.
5. **Fire / breach rolls.** Per-weapon chance to ignite a fire or open a
   hull breach in the target room. Phase 2 lights the simulation.

Crew damage from fire and suffocation are applied in `ships.hazards`
and `ships.atmosphere`, not here.
"""

from __future__ import annotations

from random import Random

from ftl.combat.damage import DamageEvent, DamageResult

FIRE_IGNITION_VALUE: float = 25.0
BREACH_INCREMENT: float = 50.0


def apply_damage(event: DamageEvent, rng: Random) -> DamageResult:
    target = event.ship

    # Zero-damage events (pure ion / crew / fire-only) skip hull math but
    # may still roll fire / breach.
    if event.damage <= 0:
        return _apply_status_only(event, rng)

    # 1. Evasion
    evasion = target.evasion_chance() if hasattr(target, "evasion_chance") else 0.0
    if evasion > 0.0 and rng.random() < evasion:
        return DamageResult(missed=True)

    # 2. Shields
    shields = getattr(target, "shields", None)
    if (
        shields is not None
        and not event.shield_piercing
        and shields.current_layers > 0
    ):
        shields.current_layers -= 1
        return DamageResult(shield_absorbed=True)

    # 3. Hull damage
    target.hull.damage(event.damage)

    # 4. System damage on target room
    room = target.rooms.get(event.room_id)
    system_damage = 0
    started_fire = False
    started_breach = False
    if room is not None:
        room.take_hit(event.damage)
        if room.system is not None:
            system_damage = event.damage
        # 5. Status rolls
        if event.fire_chance > 0 and rng.random() < event.fire_chance:
            room.fire = max(room.fire, FIRE_IGNITION_VALUE)
            started_fire = True
        if event.breach_chance > 0 and rng.random() < event.breach_chance:
            room.breach = min(100.0, room.breach + BREACH_INCREMENT)
            started_breach = True

    return DamageResult(
        hull_damage=event.damage,
        system_damage=system_damage,
        started_fire=started_fire,
        started_breach=started_breach,
    )


def _apply_status_only(event: DamageEvent, rng: Random) -> DamageResult:
    """Zero-damage event: skip hull but still roll fire / breach."""
    target = event.ship
    room = target.rooms.get(event.room_id)
    if room is None:
        return DamageResult()
    started_fire = False
    started_breach = False
    if event.fire_chance > 0 and rng.random() < event.fire_chance:
        room.fire = max(room.fire, FIRE_IGNITION_VALUE)
        started_fire = True
    if event.breach_chance > 0 and rng.random() < event.breach_chance:
        room.breach = min(100.0, room.breach + BREACH_INCREMENT)
        started_breach = True
    return DamageResult(started_fire=started_fire, started_breach=started_breach)
