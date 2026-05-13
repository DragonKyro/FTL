"""The damage application pipeline.

A single canonical function: `apply_damage(event, rng)`. The pipeline:

1. **Evasion roll.** Engines (and piloting manning) give a chance to miss.
2. **Shield absorption.** Non-shield-piercing weapons are absorbed one
   layer per hit. Missiles + bombs bypass.
3. **Hull damage.** Direct hp loss (skipped for ion-only weapons).
4. **System damage.** Target room's system takes the same damage bars.
5. **Ion damage.** If `event.ion_damage > 0`, the target room's system
   gains `ion_damage * 2.0` seconds of ion charge.
6. **Fire / breach rolls.** Per-weapon chance to ignite or breach.

Crew damage from fire and suffocation are applied in `ships.hazards`
and `ships.atmosphere`, not here. Beam multi-room damage lives in
`combat/engine.py:_resolve_beam`.
"""

from __future__ import annotations

from random import Random

from ftl.combat.damage import DamageEvent, DamageResult

FIRE_IGNITION_VALUE: float = 25.0
BREACH_INCREMENT: float = 50.0
ION_DURATION_PER_POINT: float = 2.0


def apply_damage(event: DamageEvent, rng: Random) -> DamageResult:
    target = event.ship

    # Pure status events (no damage, no ion) skip the pipeline.
    if event.damage <= 0 and event.ion_damage <= 0:
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

    # 3. Hull damage (skipped for ion-only weapons)
    hull_damage = 0
    if event.damage > 0 and not event.ion_only:
        target.hull.damage(event.damage)
        hull_damage = event.damage

    # 4 + 5. Room effects
    room = target.rooms.get(event.room_id)
    system_damage = 0
    started_fire = False
    started_breach = False
    if room is not None:
        if hull_damage > 0:
            room.take_hit(hull_damage)
            if room.system is not None:
                system_damage = hull_damage
        # 5. Ion damage path
        if event.ion_damage > 0 and room.system is not None:
            room.system.ion_charge += event.ion_damage * ION_DURATION_PER_POINT
        # 6. Status rolls
        if event.fire_chance > 0 and rng.random() < event.fire_chance:
            room.fire = max(room.fire, FIRE_IGNITION_VALUE)
            started_fire = True
        if event.breach_chance > 0 and rng.random() < event.breach_chance:
            room.breach = min(100.0, room.breach + BREACH_INCREMENT)
            started_breach = True

    return DamageResult(
        hull_damage=hull_damage,
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
