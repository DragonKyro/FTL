"""HackingSystem launch + activate + system disable + damage."""

from __future__ import annotations

from ftl.systems.hacking import ACTIVE_SECONDS, HackingSystem
from ftl.systems.weapons import WeaponsSystem


def _hack_ready() -> HackingSystem:
    h = HackingSystem()
    h.set_power(1)
    return h


def test_launch_then_latch_then_activate() -> None:
    hack = _hack_ready()
    target = WeaponsSystem()
    target.set_power(2)
    # Initially no drone in flight, no latch.
    assert hack.can_launch
    assert not hack.can_activate
    hack.begin_launch()
    # On arrival from the engine:
    hack.on_drone_arrival(target, on_ship=None)  # type: ignore[arg-type]
    assert hack.is_latched
    assert hack.can_activate
    assert hack.activate()
    assert hack.is_active
    assert target.hacked
    # During activation, target reports 0 effective_power.
    assert target.effective_power == 0


def test_active_damages_target_over_time() -> None:
    hack = _hack_ready()
    target = WeaponsSystem()
    target.set_power(4)
    hack.on_drone_arrival(target, on_ship=None)  # type: ignore[arg-type]
    hack.activate()
    starting_damage = target.damage
    for _ in range(60 * int(ACTIVE_SECONDS + 1)):
        hack.tick(1.0 / 60.0)
    assert target.damage > starting_damage
    # After active period ends, target unhacked.
    assert not target.hacked


def test_cannot_activate_without_latch() -> None:
    hack = _hack_ready()
    assert not hack.activate()
