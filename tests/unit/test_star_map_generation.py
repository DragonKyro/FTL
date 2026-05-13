"""Star map generation: beacon count, connectivity, encounter mix."""

from __future__ import annotations

from random import Random

from ftl.data.registry import Registry
from ftl.map.encounter_kind import EncounterKind
from ftl.map.generation import generate_star_map


def _gen():  # type: ignore[no-untyped-def]
    reg = Registry()
    reg.load_all()
    sector = reg.sectors["the_borderlands"]
    return generate_star_map(sector, Random(42))


def test_correct_beacon_count() -> None:
    m = _gen()
    assert len(m.beacons) == 12


def test_start_and_exit_marked() -> None:
    m = _gen()
    assert m.current_beacon in m.beacons
    assert m.exit_beacon in m.beacons
    assert m.current_beacon != m.exit_beacon
    # Start + exit are EMPTY.
    assert m.beacons[m.current_beacon].encounter_id == EncounterKind.EMPTY.value
    assert m.beacons[m.exit_beacon].encounter_id == EncounterKind.EMPTY.value


def test_exit_reachable_from_start() -> None:
    m = _gen()
    seen: set[str] = {m.current_beacon}
    frontier: list[str] = [m.current_beacon]
    while frontier:
        cur = frontier.pop()
        if cur == m.exit_beacon:
            assert True
            return
        for nbr in m.beacons[cur].connections:
            if nbr not in seen:
                seen.add(nbr)
                frontier.append(nbr)
    raise AssertionError("Exit beacon unreachable from start")


def test_beacons_have_connections() -> None:
    m = _gen()
    for b in m.beacons.values():
        assert len(b.connections) > 0
