"""ClonebaySystem revive queue + timer."""

from __future__ import annotations

from ftl.data.registry import Registry
from ftl.ships.ship import PlayerShip
from ftl.systems.clonebay import CLONE_REVIVE_HP_FRACTION


def _pilgrim() -> PlayerShip:
    reg = Registry()
    reg.load_all()
    return PlayerShip.from_def(reg.ships["pilgrim"], reg)


def test_pilgrim_has_clonebay_not_medbay() -> None:
    ship = _pilgrim()
    assert "clonebay" in ship.systems
    assert "medbay" not in ship.systems


def test_clonebay_enqueues_dead_crew() -> None:
    ship = _pilgrim()
    clonebay = ship.systems["clonebay"]
    crew = ship.crew[0]
    crew.hp = 0
    clonebay.enqueue(crew)  # type: ignore[attr-defined]
    assert crew in clonebay.clone_queue  # type: ignore[attr-defined]


def test_clonebay_revives_after_time() -> None:
    ship = _pilgrim()
    clonebay = ship.systems["clonebay"]
    clonebay.set_power(2)
    crew = ship.crew[0]
    crew.hp = 0
    ship.crew.remove(crew)
    clonebay.enqueue(crew)  # type: ignore[attr-defined]

    # Tick long enough — clone time / max(1, level-1) seconds.
    dt = 1.0 / 60.0
    for _ in range(60 * 60):  # 60s should be more than enough
        clonebay.tick(dt)
        if crew.alive:
            break
    assert crew.alive
    assert crew.hp == float(crew.max_hp) * CLONE_REVIVE_HP_FRACTION
    assert crew in ship.crew


def test_destroyed_clonebay_clears_queue() -> None:
    ship = _pilgrim()
    clonebay = ship.systems["clonebay"]
    crew = ship.crew[0]
    crew.hp = 0
    clonebay.enqueue(crew)  # type: ignore[attr-defined]
    clonebay.damage = clonebay.level
    clonebay.tick(1.0 / 60.0)
    assert clonebay.clone_queue == []  # type: ignore[attr-defined]
