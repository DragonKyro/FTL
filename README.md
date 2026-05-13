# Helixfall

An original FTL-inspired roguelike spaceship sim written in Python with the
[Arcade](https://api.arcade.academy/) library. The game draws on FTL: Faster
Than Light and its FTL Multiverse mod for genre conventions and scope ambition
— many weapons, many species, lots of story arcs, multiple factions — but
tells its own story with its own names, lore, and balance.

Setting: ten thousand years after a galactic civilization (the Vyrnari)
vanished, the FTL conduit network they left behind — the **Helix Gates** —
is failing. One ship, one captain, one collapsing galaxy.

This is a personal project. The Python package is still named `ftl/` for
historical reasons; the game's title is *Helixfall*.

## Status

**Phase 0 — Framework.** The project skeleton, base classes, tooling, and
tests exist. There is no real gameplay yet.

## Stack

- Python **3.11+**
- Arcade **3.x** (pyglet 2)
- PyYAML, pydantic v2 for data-driven content
- pytest, ruff, mypy, pre-commit

## Quickstart

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# *nix:     source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

Run the game (placeholder main menu for now):

```bash
python helixfall.py     # convenience launcher (works without install)
python -m ftl           # equivalent, requires `pip install -e .` or src on PYTHONPATH
```

Run tests / lint / type-check:

```bash
pytest
ruff check .
ruff format --check .
mypy src
pre-commit run --all-files
```

## Project layout

```
src/ftl/        # game code
  core/         # game loop, fixed-step simulation, scenes, RNG
  data/         # YAML content loader + pydantic schemas
  ships/        # Ship, Hull, Room, Door, Tile
  systems/      # installed systems (weapons, shields, engines, ...)
  crew/         # Crew unit, Species, Skills, AI
  weapons/      # Weapon families + projectiles + on-hit effects
  drones/       # Drone families
  augments/     # passive augmentations w/ hook points
  combat/       # combat state, targeting, damage pipeline
  map/          # beacons, sectors, star map, galaxy, generation
  events/       # story event engine (runtime — not the stories themselves)
  upgrades/     # store / level transactions
  scenarios/    # starting-run configs
  scenes/       # arcade scenes (main menu, combat, star map, ...)
  ui/           # HUD + widgets
  save/         # save/load
  assets/       # texture/sound cache
  util/         # pathfinding, geometry, timing
content/        # data files for stats (ships, weapons, species, ...)
story/          # narrative content (events, quests, dialogue)
assets/         # binary assets (sprites, sounds, fonts) — placeholders for now
tests/          # pytest unit + integration + content-validation suites
```

## Architecture in one paragraph

Content is **hybrid**: a small set of *behavior classes* describes how a
family of things works (e.g. `BeamWeapon`, `MissileWeapon`, `Species`), and
*individual definitions* live as YAML files (e.g. a specific beam weapon's
charge time and damage). Adding new variants is a YAML edit. Adding a new
*kind* of behavior is a new class. The runtime is a fixed-step simulation
(default 60 Hz) decoupled from rendering, so pause and speed-up are clean and
gameplay is deterministic and testable.

## Roadmap

- **Phase 0** — Framework (this commit): structure, stubs, tooling, tests.
- **Phase 1** — Vertical slice: one ship, one room layout, one fight against
  a hardcoded enemy. Power, weapons charge, shields, hull damage.
- **Phase 2** — All core systems (medbay, oxygen, doors, drones, teleporter,
  cloaking, hacking, mind control, etc.) and base species set.
- **Phase 3** — Star map, sector progression, jump fuel, beacon graph.
- **Phase 4** — Story event runtime + first authored event pool.
- **Phase 5** — Feature parity with vanilla FTL (mechanics + a content base).
- **Phase 6+** — Expansion toward Multiverse-scale breadth with original
  content (factions, species, weapons, dimensions, meta-progression).

## A note on inspiration

This project takes inspiration from FTL: Faster Than Light (Subset Games)
and the FTL Multiverse mod community. It does **not** include or copy any
proprietary names, sprites, audio, or text from those games. Everything
content-side — species names, weapon names, factions, lore, art — is
original to this project.
