"""CombatEngine — the per-tick orchestrator of a fight.

The engine owns:
- The CombatState (ships + inventories + outcome + flee state)
- The enemy AI
- The list of in-flight projectiles
- The RNG used for evasion / AI tie-breaks
- An optional EventBus for UI notifications

Each fixed simulation tick the engine:
1. Bails if the outcome is no longer FIGHTING.
2. Ticks the AI (which sets enemy weapon targets).
3. Ticks both ships (systems, shields recharge, weapon charge progress).
4. Tries to fire any ready, targeted weapon — spawns Projectile, deducts
   missile ammo, resets charge.
5. Ticks every in-flight projectile; resolves arrivals via the damage
   pipeline.
6. Advances flee progress.
7. Checks for win / loss / flee → updates outcome.
"""

from __future__ import annotations

from random import Random
from typing import TYPE_CHECKING

from ftl.combat.combat_state import CombatState, Inventory, Outcome
from ftl.combat.damage import DamageEvent
from ftl.combat.pipeline import apply_damage
from ftl.weapons.projectile import Projectile

if TYPE_CHECKING:
    from ftl.ai.enemy_pilot import EnemyPilot
    from ftl.core.event_bus import EventBus
    from ftl.ships.ship import Ship
    from ftl.weapons.weapon import Weapon


# Time (seconds) between weapon fire and projectile arrival. Constant for
# all weapons in Phase 1; tuned per-weapon-family in Phase 2+.
PROJECTILE_TRAVEL_TIME: float = 1.5


class WeaponFired:
    """Event: a weapon launched a projectile."""

    def __init__(self, projectile: Projectile) -> None:
        self.projectile: Projectile = projectile


class HitResolved:
    """Event: a projectile arrived and went through the damage pipeline."""

    def __init__(
        self,
        target: Ship,
        room_id: str,
        damage_dealt: int,
        missed: bool,
        shield_absorbed: bool,
    ) -> None:
        self.target: Ship = target
        self.room_id: str = room_id
        self.damage_dealt: int = damage_dealt
        self.missed: bool = missed
        self.shield_absorbed: bool = shield_absorbed


class OutcomeReached:
    """Event: the fight ended with the given outcome."""

    def __init__(self, outcome: Outcome) -> None:
        self.outcome: Outcome = outcome


class CombatEngine:
    """Orchestrates one fight. Implements Tickable."""

    def __init__(
        self,
        state: CombatState,
        ai: EnemyPilot,
        rng: Random,
        event_bus: EventBus | None = None,
    ) -> None:
        self.state: CombatState = state
        self.ai: EnemyPilot = ai
        self.rng: Random = rng
        self.event_bus: EventBus | None = event_bus
        self.projectiles: list[Projectile] = []

    # --- exposed for tests / UI -------------------------------------------

    @property
    def outcome(self) -> Outcome:
        return self.state.outcome

    @property
    def player(self) -> Ship:
        return self.state.player

    @property
    def enemy(self) -> Ship:
        return self.state.enemy

    # --- player-driven actions -------------------------------------------

    def begin_flee(self) -> None:
        if self.state.outcome is Outcome.FIGHTING:
            self.state.flee_active = True

    def cancel_flee(self) -> None:
        self.state.flee_active = False
        self.state.flee_progress = 0.0

    # --- the tick --------------------------------------------------------

    def tick(self, dt: float) -> None:
        if self.state.outcome is not Outcome.FIGHTING:
            return

        self.ai.tick(dt)
        self.state.player.tick(dt)
        self.state.enemy.tick(dt)

        self._try_fire_weapons(self.state.player, self.state.enemy, self.state.player_inventory)
        self._try_fire_weapons(self.state.enemy, self.state.player, self.state.enemy_inventory)

        self._tick_projectiles(dt)

        if self.state.flee_active:
            self.state.flee_progress = min(
                self.state.flee_charge_time,
                self.state.flee_progress + dt,
            )
            if self.state.flee_progress >= self.state.flee_charge_time:
                self._set_outcome(Outcome.FLED)
                return

        if self.state.enemy.hull.destroyed:
            self._set_outcome(Outcome.WON)
        elif self.state.player.hull.destroyed:
            self._set_outcome(Outcome.LOST)

    # --- internals -------------------------------------------------------

    def _try_fire_weapons(
        self, shooter: Ship, target_ship: Ship, inventory: Inventory
    ) -> None:
        for weapon in shooter.weapons:
            if not weapon.ready:
                continue
            if weapon.target_room_id is None:
                continue
            if weapon.target_room_id not in target_ship.rooms:
                continue
            if weapon.consumes_missile and inventory.missiles < weapon.stats.missile_cost:
                continue
            projectile = self._spawn_projectile(weapon, shooter, target_ship)
            weapon.reset_charge()
            if weapon.consumes_missile:
                inventory.missiles -= weapon.stats.missile_cost
            self.projectiles.append(projectile)
            self._publish(WeaponFired(projectile))

    def _spawn_projectile(
        self, weapon: Weapon, shooter: Ship, target_ship: Ship
    ) -> Projectile:
        # weapon.target_room_id is guaranteed not-None by _try_fire_weapons.
        target_room_id = weapon.target_room_id
        assert target_room_id is not None
        return Projectile(
            source_ship=shooter,
            target_ship=target_ship,
            target_room_id=target_room_id,
            damage=weapon.stats.damage,
            shield_piercing=weapon.bypasses_shields,
            weapon_family=weapon.stats.family,
            travel_time=PROJECTILE_TRAVEL_TIME,
        )

    def _tick_projectiles(self, dt: float) -> None:
        for projectile in list(self.projectiles):
            projectile.tick(dt)
            if projectile.arrived:
                self._resolve_hit(projectile)
                self.projectiles.remove(projectile)

    def _resolve_hit(self, projectile: Projectile) -> None:
        event = DamageEvent(
            ship=projectile.target_ship,
            room_id=projectile.target_room_id,
            damage=projectile.damage,
            shield_piercing=projectile.shield_piercing,
        )
        result = apply_damage(event, self.rng)
        self._publish(
            HitResolved(
                target=projectile.target_ship,
                room_id=projectile.target_room_id,
                damage_dealt=result.hull_damage,
                missed=result.missed,
                shield_absorbed=result.shield_absorbed,
            )
        )

    def _set_outcome(self, outcome: Outcome) -> None:
        if self.state.outcome is Outcome.FIGHTING:
            self.state.outcome = outcome
            self._publish(OutcomeReached(outcome))

    def _publish(self, event: object) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(event)
