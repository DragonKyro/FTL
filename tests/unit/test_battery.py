"""BatterySystem activation + power_bonus."""

from __future__ import annotations

from ftl.systems.battery import ACTIVE_SECONDS, BatterySystem


def _battery_ready(level: int = 1) -> BatterySystem:
    b = BatterySystem(level=level)
    b.set_power(1)
    return b


def test_activate_grants_power_bonus() -> None:
    b = _battery_ready(level=1)
    assert b.power_bonus == 0
    assert b.activate()
    assert b.is_active
    assert b.power_bonus == 2


def test_higher_level_bigger_bonus() -> None:
    b = _battery_ready(level=2)
    b.activate()
    assert b.power_bonus == 4


def test_active_decays_into_cooldown() -> None:
    b = _battery_ready()
    b.activate()
    for _ in range(60 * int(ACTIVE_SECONDS + 1)):
        b.tick(1.0 / 60.0)
    assert not b.is_active
    assert b.cooldown_remaining > 0
    assert b.power_bonus == 0
