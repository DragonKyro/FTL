"""The damage application pipeline.

A single canonical function: `apply_damage(event, rng)`. The pipeline:

1. **Evasion roll.** Engines (and later cloaking) give a chance to miss
   entirely. Missiles can still be dodged.
2. **Shield absorption.** Lasers (any non–shield-piercing weapon) are
   absorbed one layer per hit until the shield is fully stripped. Missiles
   bypass.
3. **Hull damage.** Direct hp loss.
4. **System damage.** If the target room hosts a system, that system takes
   the same damage in bars.

Crew damage, fire, breach, ion are scaffolded on `DamageEvent` but not
applied in Phase 1 (no crew yet, no fire/oxygen simulation yet).
"""

from __future__ import annotations

from random import Random

from ftl.combat.damage import DamageEvent, DamageResult


def apply_damage(event: DamageEvent, rng: Random) -> DamageResult:
    target = event.ship
    if event.damage <= 0:
        # Pure ion / crew / fire events — Phase 2.
        return DamageResult()

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
    if room is not None:
        room.take_hit(event.damage)
        if room.system is not None:
            system_damage = event.damage

    return DamageResult(hull_damage=event.damage, system_damage=system_damage)
