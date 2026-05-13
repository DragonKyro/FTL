"""Room behavior: oxygen depletion when breached."""

from __future__ import annotations

from ftl.ships.room import Room


def test_breached_room_loses_oxygen_over_time():
    room = Room(id="cargo", breach=1, oxygen=1.0)

    # 1 second of ticking, in 60 Hz fixed-step chunks
    for _ in range(60):
        room.tick(1.0 / 60.0)

    assert room.oxygen < 1.0


def test_unbreached_room_keeps_oxygen():
    room = Room(id="bridge", breach=0, oxygen=1.0)

    for _ in range(60):
        room.tick(1.0 / 60.0)

    assert room.oxygen == 1.0


def test_oxygen_clamped_at_zero():
    room = Room(id="cargo", breach=5, oxygen=0.01)

    for _ in range(600):  # plenty of time
        room.tick(1.0 / 60.0)

    assert room.oxygen >= 0.0
