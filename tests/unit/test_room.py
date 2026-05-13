"""Room is now a passive data container. The active atmosphere + hazards
simulation lives in `ships.atmosphere` and `ships.hazards`; their tests
exercise the oxygen/fire/breach behavior end-to-end.
"""

from __future__ import annotations

from ftl.ships.room import Room


def test_room_take_hit_propagates_to_system():
    from ftl.systems.weapons import WeaponsSystem

    system = WeaponsSystem()
    room = Room(id="gun_bay", system=system)
    room.take_hit(2)
    assert system.damage == 2


def test_room_take_hit_with_no_system_is_noop():
    room = Room(id="empty")
    room.take_hit(2)
    assert room.fire == 0
    assert room.breach == 0
