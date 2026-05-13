"""Live combat encounter state."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftl.ships.ship import EnemyShip, PlayerShip


class CombatState:
    """One active combat encounter between the player and a single enemy ship."""

    def __init__(self, player: PlayerShip, enemy: EnemyShip) -> None:
        self.player: PlayerShip = player
        self.enemy: EnemyShip = enemy

    @property
    def player_won(self) -> bool:
        return self.enemy.hull.destroyed and not self.player.hull.destroyed

    @property
    def player_lost(self) -> bool:
        return self.player.hull.destroyed

    @property
    def over(self) -> bool:
        return self.player_won or self.player_lost
