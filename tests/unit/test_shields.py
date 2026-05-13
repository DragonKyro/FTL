"""ShieldsSystem layer math, recharge, and damage interactions."""

from __future__ import annotations

from ftl.systems.shields import RECHARGE_TIME_PER_LAYER, ShieldsSystem


def test_max_layers_is_power_div_two():
    shields = ShieldsSystem(level=4)
    shields.set_power(4)
    assert shields.max_layers == 2

    shields.set_power(2)
    assert shields.max_layers == 1

    shields.set_power(1)
    assert shields.max_layers == 0


def test_recharge_tick_grows_layer_after_threshold():
    shields = ShieldsSystem(level=2)
    shields.set_power(2)
    assert shields.current_layers == 0

    shields.tick(RECHARGE_TIME_PER_LAYER + 0.01)
    assert shields.current_layers == 1


def test_recharge_stops_at_max_layers():
    shields = ShieldsSystem(level=2)
    shields.set_power(2)
    for _ in range(10):
        shields.tick(RECHARGE_TIME_PER_LAYER)
    assert shields.current_layers == shields.max_layers


def test_losing_power_drops_excess_layers():
    shields = ShieldsSystem(level=4)
    shields.set_power(4)
    shields.tick(RECHARGE_TIME_PER_LAYER * 2 + 0.01)
    assert shields.current_layers == 2

    shields.set_power(2)
    assert shields.current_layers == 1


def test_unpowered_shields_have_zero_max_layers():
    shields = ShieldsSystem(level=2)
    shields.set_power(0)
    assert shields.max_layers == 0
    # Pre-set layers should drop on next tick / power change.
    shields.current_layers = 1
    shields.set_power(0)
    assert shields.current_layers == 0


def test_recharge_carries_leftover_progress():
    """A tick longer than one threshold counts toward the next layer."""
    shields = ShieldsSystem(level=4)
    shields.set_power(4)
    shields.tick(RECHARGE_TIME_PER_LAYER + 0.5)
    assert shields.current_layers == 1
    # The 0.5s of overshoot accumulates toward the next layer.
    assert 0.4 <= shields.recharge_progress <= 0.6


def test_recharge_progress_zeroes_when_full():
    shields = ShieldsSystem(level=2)
    shields.set_power(2)
    shields.tick(RECHARGE_TIME_PER_LAYER * 5)
    assert shields.current_layers == 1
    assert shields.recharge_progress == 0.0
