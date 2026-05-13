"""Fixed-step simulation: tick rate, pause, speed multiplier."""

from __future__ import annotations

from ftl.config import SIM_DT
from ftl.core.simulation import Simulation


class _Counter:
    """Minimal Tickable that counts how many times it was ticked."""

    def __init__(self) -> None:
        self.count = 0
        self.last_dt = 0.0

    def tick(self, dt: float) -> None:
        self.count += 1
        self.last_dt = dt


def test_single_fixed_tick_dispatches_once():
    sim = Simulation()
    counter = _Counter()
    sim.register(counter)

    dispatched = sim.update(SIM_DT)

    assert dispatched == 1
    assert counter.count == 1
    assert counter.last_dt == SIM_DT


def test_many_fixed_ticks_in_one_update():
    sim = Simulation()
    counter = _Counter()
    sim.register(counter)

    dispatched = sim.update(SIM_DT * 5)

    assert dispatched == 5
    assert counter.count == 5


def test_pause_stops_advance():
    sim = Simulation()
    counter = _Counter()
    sim.register(counter)
    sim.paused = True

    dispatched = sim.update(SIM_DT * 10)

    assert dispatched == 0
    assert counter.count == 0


def test_speed_multiplier_scales_advance():
    sim = Simulation()
    counter = _Counter()
    sim.register(counter)
    sim.speed_multiplier = 2.0

    dispatched = sim.update(SIM_DT * 3)

    assert dispatched == 6
    assert counter.count == 6


def test_accumulator_retains_leftover_time():
    sim = Simulation()
    counter = _Counter()
    sim.register(counter)

    # 1.5 * SIM_DT should fire once and accumulate 0.5*SIM_DT
    sim.update(SIM_DT * 1.5)
    assert counter.count == 1
    # Another 0.5*SIM_DT brings the accumulator over and fires once more
    sim.update(SIM_DT * 0.5)
    assert counter.count == 2


def test_unregister_stops_ticking():
    sim = Simulation()
    counter = _Counter()
    sim.register(counter)
    sim.unregister(counter)

    sim.update(SIM_DT * 5)

    assert counter.count == 0
