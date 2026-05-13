"""Live combat encounter state.

A `CombatState` holds the *snapshot* of an active fight: which two ships,
which side has which inventory (missiles, drone parts), and the current
outcome. The `CombatEngine` owns the per-tick logic and mutates state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import EnemyShip, PlayerShip


class Outcome(str, Enum):
    FIGHTING = "fighting"
    WON = "won"
    LOST = "lost"
    FLED = "fled"


@dataclass
class Inventory:
    missiles: int = 0
    drone_parts: int = 0


class CombatState:
    """Snapshot of one active fight between the player and a single enemy."""

    def __init__(
        self,
        player: PlayerShip,
        enemy: EnemyShip,
        player_missiles: int = 8,
        enemy_missiles: int = 0,
    ) -> None:
        self.player: PlayerShip = player
        self.enemy: EnemyShip = enemy
        self.player_inventory: Inventory = Inventory(missiles=player_missiles)
        self.enemy_inventory: Inventory = Inventory(missiles=enemy_missiles)
        self.outcome: Outcome = Outcome.FIGHTING
        self.flee_active: bool = False
        self.flee_progress: float = 0.0
        self.flee_charge_time: float = 15.0

    @property
    def over(self) -> bool:
        return self.outcome is not Outcome.FIGHTING

    @property
    def player_won(self) -> bool:
        return self.outcome is Outcome.WON

    @property
    def player_lost(self) -> bool:
        return self.outcome is Outcome.LOST

    @property
    def player_fled(self) -> bool:
        return self.outcome is Outcome.FLED
