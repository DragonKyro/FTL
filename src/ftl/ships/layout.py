"""Build a ship's tile grid + door list from its `ShipDef`.

Each room is expanded into a W×H block of tiles indexed by their global
(x, y) ship-grid coordinate. Doors are inferred from any pair of tiles
in different rooms that share a 4-directional grid edge.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ftl.ships.door import Door
from ftl.ships.tile import Tile

if TYPE_CHECKING:
    from ftl.data.schemas import ShipDef


_NEIGHBOR_OFFSETS: tuple[tuple[int, int], ...] = ((1, 0), (-1, 0), (0, 1), (0, -1))


def build_layout(
    ship_def: ShipDef,
) -> tuple[dict[str, list[Tile]], list[Door]]:
    """Return (`tiles_by_room`, `doors`) for the given ship definition."""
    tiles_by_room: dict[str, list[Tile]] = {}
    tile_by_coord: dict[tuple[int, int], Tile] = {}

    for room in ship_def.rooms:
        room_tiles: list[Tile] = []
        for dx in range(room.width):
            for dy in range(room.height):
                tx = room.x + dx
                ty = room.y + dy
                tile = Tile(x=tx, y=ty, room_id=room.id)
                room_tiles.append(tile)
                tile_by_coord[(tx, ty)] = tile
        tiles_by_room[room.id] = room_tiles

    doors: list[Door] = []
    seen_pairs: set[frozenset[tuple[int, int]]] = set()

    for room in ship_def.rooms:
        for tile in tiles_by_room[room.id]:
            for ox, oy in _NEIGHBOR_OFFSETS:
                neighbor_coord = (tile.x + ox, tile.y + oy)
                neighbor = tile_by_coord.get(neighbor_coord)
                if neighbor is None or neighbor.room_id == tile.room_id:
                    continue
                pair: frozenset[tuple[int, int]] = frozenset(
                    {(tile.x, tile.y), neighbor_coord}
                )
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                room_a, room_b = sorted([room.id, neighbor.room_id])
                # tile_a always corresponds to room_a (lower-sorted id)
                if room.id == room_a:
                    tile_a = (tile.x, tile.y)
                    tile_b = neighbor_coord
                else:
                    tile_a = neighbor_coord
                    tile_b = (tile.x, tile.y)
                doors.append(
                    Door(
                        id=f"{room_a}-{room_b}-{tile_a[0]}-{tile_a[1]}",
                        room_a=room_a,
                        room_b=room_b,
                        tile_a=tile_a,
                        tile_b=tile_b,
                    )
                )

    return tiles_by_room, doors
