"""Tile graph + door inference from ShipDef geometry."""

from __future__ import annotations

from ftl.data.schemas import RoomLayout, ShipDef
from ftl.ships.layout import build_layout


def _def(rooms: list[RoomLayout]) -> ShipDef:
    return ShipDef(id="s", name="s", rooms=rooms)


def test_single_room_one_tile() -> None:
    ship_def = _def([RoomLayout(id="a", x=0, y=0)])
    tiles, doors = build_layout(ship_def)
    assert len(tiles["a"]) == 1
    assert tiles["a"][0].x == 0 and tiles["a"][0].y == 0
    assert tiles["a"][0].room_id == "a"
    assert doors == []


def test_two_horizontal_rooms_get_one_door() -> None:
    ship_def = _def(
        [
            RoomLayout(id="a", x=0, y=0),
            RoomLayout(id="b", x=1, y=0),
        ]
    )
    tiles, doors = build_layout(ship_def)
    assert len(tiles["a"]) == 1
    assert len(tiles["b"]) == 1
    assert len(doors) == 1
    door = doors[0]
    assert {door.room_a, door.room_b} == {"a", "b"}
    assert {door.tile_a, door.tile_b} == {(0, 0), (1, 0)}


def test_non_adjacent_rooms_no_door() -> None:
    ship_def = _def(
        [
            RoomLayout(id="a", x=0, y=0),
            RoomLayout(id="b", x=2, y=0),
        ]
    )
    _, doors = build_layout(ship_def)
    assert doors == []


def test_2x1_room_expands_to_two_tiles() -> None:
    ship_def = _def([RoomLayout(id="a", x=0, y=0, width=2)])
    tiles, doors = build_layout(ship_def)
    assert len(tiles["a"]) == 2
    coords = {(t.x, t.y) for t in tiles["a"]}
    assert coords == {(0, 0), (1, 0)}
    assert doors == []


def test_wayfarer_inferred_doors() -> None:
    """End-to-end: the canonical Wayfarer layout should infer 7 doors."""
    ship_def = _def(
        [
            RoomLayout(id="bridge", x=0, y=0),
            RoomLayout(id="gun_bay", x=1, y=0),
            RoomLayout(id="shield_room", x=2, y=0),
            RoomLayout(id="medbay", x=0, y=1),
            RoomLayout(id="engine_room", x=1, y=1),
            RoomLayout(id="oxygen_room", x=2, y=1),
            RoomLayout(id="teleporter_pad", x=0, y=2),
        ]
    )
    _, doors = build_layout(ship_def)
    # bridge↔gun_bay, gun_bay↔shield_room, bridge↔medbay, gun_bay↔engine_room,
    # shield_room↔oxygen_room, medbay↔engine_room, engine_room↔oxygen_room,
    # medbay↔teleporter_pad. That's 8.
    assert len(doors) == 8
