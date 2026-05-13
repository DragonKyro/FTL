"""CloakingSystem activation, active timer, cooldown."""

from __future__ import annotations

from ftl.systems.cloaking import ACTIVE_SECONDS, COOLDOWN_SECONDS, CloakingSystem


def _cloak_ready() -> CloakingSystem:
    cloak = CloakingSystem()
    cloak.set_power(1)
    return cloak


def test_activate_when_ready() -> None:
    cloak = _cloak_ready()
    assert cloak.activate()
    assert cloak.is_active
    assert cloak.active_remaining == ACTIVE_SECONDS


def test_cannot_activate_while_unpowered() -> None:
    cloak = CloakingSystem()
    cloak.set_power(0)
    assert not cloak.activate()


def test_active_decays_then_cooldown() -> None:
    cloak = _cloak_ready()
    cloak.activate()
    for _ in range(60 * int(ACTIVE_SECONDS + 1)):
        cloak.tick(1.0 / 60.0)
    assert not cloak.is_active
    assert cloak.cooldown_remaining > 0


def test_cooldown_blocks_reactivate() -> None:
    cloak = _cloak_ready()
    cloak.activate()
    # Burn through active phase.
    for _ in range(60 * int(ACTIVE_SECONDS + 1)):
        cloak.tick(1.0 / 60.0)
    assert not cloak.activate()


def test_can_reactivate_after_cooldown() -> None:
    cloak = _cloak_ready()
    cloak.activate()
    # Full active + cooldown.
    for _ in range(60 * int(ACTIVE_SECONDS + COOLDOWN_SECONDS + 1)):
        cloak.tick(1.0 / 60.0)
    assert cloak.activate()
