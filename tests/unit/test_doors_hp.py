"""Door HP, take_door_hit, destroyed → permanently passable."""

from __future__ import annotations

from ftl.ships.door import Door


def _door() -> Door:
    return Door(
        id="d", room_a="a", room_b="b", tile_a=(0, 0), tile_b=(1, 0),
        force_closed=True, hp=4, max_hp=4,
    )


def test_closed_door_blocks_boarders() -> None:
    door = _door()
    assert not door.passable_for(is_home_team=False)
    assert door.passable_for(is_home_team=True)


def test_take_door_hit_breaks_at_zero_hp() -> None:
    door = _door()
    assert not door.take_door_hit(1)
    assert not door.take_door_hit(1)
    assert not door.take_door_hit(1)
    broke = door.take_door_hit(1)
    assert broke
    assert door.destroyed
    assert door.hp == 0
    assert not door.force_closed
    assert door.is_open
    # Destroyed door is passable to all.
    assert door.passable_for(is_home_team=False)


def test_sub_one_damage_accumulates() -> None:
    door = _door()
    for _ in range(8):
        door.take_door_hit(0.5)
    assert door.destroyed


def test_destroyed_door_ignores_toggle() -> None:
    door = _door()
    for _ in range(4):
        door.take_door_hit(1)
    door.toggle()
    assert door.destroyed
    assert not door.force_closed
