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
from ftl.crew.combat import tick_crew_combat
from ftl.crew.crew import CrewState
from ftl.weapons.projectile import Projectile

if TYPE_CHECKING:
    from ftl.ai.enemy_pilot import EnemyPilot
    from ftl.core.event_bus import EventBus
    from ftl.crew.crew import Crew
    from ftl.ships.room import Room
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

    def send_boarders(self, crew_list: list[Crew], target_room: Room) -> bool:
        """Teleport up to `pad_capacity` crew currently on the teleporter pad
        to `target_room` on the enemy ship. Returns True on success.
        """
        tele = self.state.player.teleporter
        if tele is None or not tele.is_ready:
            return False
        pad_room = self._teleporter_pad_room(self.state.player)
        if pad_room is None or not pad_room.tiles:
            return False
        pad_coords = {(t.x, t.y) for t in pad_room.tiles}
        eligible = [
            c for c in crew_list
            if c.alive
            and c.current_ship is self.state.player
            and c.current_tile is not None
            and (c.current_tile.x, c.current_tile.y) in pad_coords
        ][: tele.pad_capacity]
        if not eligible:
            return False
        dest_tile = target_room.tiles[0] if target_room.tiles else None
        if dest_tile is None:
            return False
        for crew in eligible:
            self.state.player.crew.remove(crew)
            self.state.enemy.crew.append(crew)
            crew.current_ship = self.state.enemy
            crew.current_tile = dest_tile
            crew.path = []
            crew.move_progress = 0.0
        tele.begin_cooldown()
        return True

    def recall_boarders(self) -> bool:
        """Recall all player crew currently on the enemy ship to the pad."""
        tele = self.state.player.teleporter
        if tele is None or not tele.is_ready:
            return False
        pad_room = self._teleporter_pad_room(self.state.player)
        if pad_room is None or not pad_room.tiles:
            return False
        boarders = [
            c for c in self.state.enemy.crew
            if c.home_ship is self.state.player and c.alive
        ]
        if not boarders:
            return False
        dest_tile = pad_room.tiles[0]
        for crew in boarders:
            self.state.enemy.crew.remove(crew)
            self.state.player.crew.append(crew)
            crew.current_ship = self.state.player
            crew.current_tile = dest_tile
            crew.path = []
            crew.move_progress = 0.0
        tele.begin_cooldown()
        return True

    def has_boarders_on_enemy(self) -> bool:
        return any(c.home_ship is self.state.player for c in self.state.enemy.crew)

    def _teleporter_pad_room(self, ship: Ship) -> Room | None:
        tele = ship.teleporter
        if tele is None:
            return None
        for room in ship.rooms.values():
            if room.system is tele:
                return room
        return None

    # --- the tick --------------------------------------------------------

    def tick(self, dt: float) -> None:
        if self.state.outcome is not Outcome.FIGHTING:
            return

        self.ai.tick(dt)
        self.state.player.tick(dt)
        self.state.enemy.tick(dt)

        # Crew combat resolves *after* ship ticks (which moved everyone).
        tick_crew_combat(self.state.player, dt)
        tick_crew_combat(self.state.enemy, dt)

        self._try_fire_weapons(self.state.player, self.state.enemy, self.state.player_inventory)
        self._try_fire_weapons(self.state.enemy, self.state.player, self.state.enemy_inventory)

        self._tick_projectiles(dt)

        # Sweep dead crew once per tick.
        self._sweep_dead(self.state.player)
        self._sweep_dead(self.state.enemy)

        if self.state.flee_active:
            self.state.flee_progress = min(
                self.state.flee_charge_time,
                self.state.flee_progress + dt,
            )
            if self.state.flee_progress >= self.state.flee_charge_time:
                self._set_outcome(Outcome.FLED)
                return

        # Win/lose checks.
        if self.state.enemy.hull.destroyed:
            self._set_outcome(Outcome.WON)
            return
        if self.state.player.hull.destroyed:
            self._set_outcome(Outcome.LOST)
            return
        # Crew-extinction loss: all *home* player crew on the player ship are dead.
        if self._player_crew_extinct():
            self._set_outcome(Outcome.LOST)
            return
        # If the enemy has no home crew left AND no weapons, treat as captured.
        if self._enemy_crew_extinct() and not self._enemy_can_fight():
            self._set_outcome(Outcome.WON)

    def _player_crew_extinct(self) -> bool:
        # If the player never had any crew (Phase-1 style), don't trigger.
        home_crew = [
            c for c in self.state.player.crew + self.state.enemy.crew
            if c.home_ship is self.state.player
        ]
        if not home_crew:
            return False
        return all(not c.alive for c in home_crew)

    def _enemy_crew_extinct(self) -> bool:
        home_crew = [
            c for c in self.state.enemy.crew + self.state.player.crew
            if c.home_ship is self.state.enemy
        ]
        if not home_crew:
            return False
        return all(not c.alive for c in home_crew)

    def _enemy_can_fight(self) -> bool:
        # Considered "can still fight" if their weapons system is operational
        # and they have at least one undamaged weapon.
        ws = self.state.enemy.weapons_system
        if ws is None or not ws.is_operational:
            return False
        return any(w.stats.damage > 0 for w in self.state.enemy.weapons)

    def _sweep_dead(self, ship: Ship) -> None:
        for crew in list(ship.crew):
            if crew.state is CrewState.DEAD or (not crew.alive):
                # Clear from any system manning slot.
                for system in ship.systems.values():
                    if system.manning_crew is crew:
                        system.manning_crew = None
                # Drop them from this ship; the home_ship retains the
                # reference for "they died on the away mission" if we
                # ever want a postmortem panel.
                ship.crew.remove(crew)

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
            fire_chance=weapon.stats.fire_chance,
            breach_chance=weapon.stats.breach_chance,
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
            fire_chance=projectile.fire_chance,
            breach_chance=projectile.breach_chance,
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
