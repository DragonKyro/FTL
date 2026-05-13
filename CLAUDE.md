# Claude Code guidance — Helixfall

This file orients future Claude Code sessions to the repo. Read this first
before doing non-trivial work.

## What this project is

**Helixfall** — an original FTL-inspired roguelike. FTL: Faster Than Light
and FTL Multiverse are **reference material for ideas and scope** (genre
conventions, system breadth, trait archetypes, mechanic design) — they are
not a content source.

### The setting (one-line summary)

Ten thousand years after the Vyrnari civilization vanished, their FTL
network — the **Helix Gates** — is failing. Civilizations born from
their uplift program (Sapien, Choir, Halene, Ferran, Mhirsa, Argonite,
Yssari, Vor, Drevant, Karrukai, Loam, Vellisian/Lirathi, Hollow,
Whisperborn) fight over what comes next. Something is coming through
the failing Gates: the **Outerlight**.

### Canon location

Worldbuilding lives under [story/worldbuilding/](story/worldbuilding/).
**Read these before writing events, ships, or species:**

- [SETTING.md](story/worldbuilding/SETTING.md) — era and central conceit
- [conflicts.md](story/worldbuilding/conflicts.md) — the eight conflict tiers
- [species.md](story/worldbuilding/species.md) — the fifteen species
- [factions/](story/worldbuilding/factions/) — fifteen faction profiles
- [storylines.md](story/worldbuilding/storylines.md) — the twelve playable arcs
- [glossary.md](story/worldbuilding/glossary.md) — terminology

### Package naming

The Python package is named `ftl/` for historical reasons (the repo
predates the title). The game is *Helixfall*; the package stays `ftl`.

### Originality rule

When generating species, weapons, events, factions, or lore: **invent
original names and flavor**. Do not paste in FTL/Multiverse identifiers
("Kestrel", "Engi", "Zoltan", "Mantis", "Federation", "Rebels", etc.).
Use the canonical names listed above. Use FTL trait archetypes as
*design inspiration* — "oxygen-draining metallic species" is a pattern,
not a name; the canonical such species is the *Argonite*.

## Architecture

**Hybrid content model.** Behavior is in Python classes; instance data is in
YAML.

- To add a new variant within an existing family (e.g. a new beam weapon),
  add a YAML file under `content/weapons/`. No code change.
- To add a new behavior family (e.g. a never-before-seen weapon type), add a
  new class in `src/ftl/weapons/`. Then drive instances via YAML.

**Fixed-step simulation.** Game logic ticks at a fixed rate (default 60 Hz),
independent of frame rate. Pause stops ticking. Anything tickable implements
`core.simulation.Tickable.tick(dt)`. Don't put gameplay timing in
`on_update` / `on_draw` — put it in `tick`.

**Decoupled events.** Cross-system communication goes through
`core.event_bus.EventBus` with typed event dataclasses. Don't hard-wire UI
to combat or save to gameplay.

## Directory cheat sheet

| Need to... | Go to |
|---|---|
| Add a weapon variant | `content/weapons/*.yaml` |
| Add a weapon family | `src/ftl/weapons/*.py` |
| Add a species | `content/species/*.yaml` (+ `crew/species.py` if behavior hooks) |
| Add an event | `story/events/<faction>/*.yaml` |
| Tune simulation rate | `src/ftl/core/simulation.py` / `src/ftl/config.py` |
| Add a scene | `src/ftl/scenes/` and register in `app.py` |
| Validate content | `tests/content/test_content_validation.py` runs every YAML through schemas |

## Coding standards

- Python **3.11+**, fully type-hinted.
- `ruff` formats and lints. `mypy --strict` for `src/ftl/`.
- Prefer `dataclass` / `pydantic.BaseModel` over dicts for structured data.
- Avoid premature abstraction. Stubs are fine in Phase 0; flesh them out when
  Phase 1+ work needs them.
- No copyrighted FTL/Multiverse text, names, sprites, or audio in `content/`,
  `story/`, or `assets/`.

## Commands

```bash
pip install -e ".[dev]"       # install
python helixfall.py           # run (convenience launcher, no install needed)
python -m ftl                 # run (after install)
pytest                        # tests
ruff check . && ruff format --check .   # lint
mypy src                      # types
pre-commit run --all-files    # everything pre-commit does
```

## Where the plan lives

The Phase 0 plan that produced this skeleton is at
`C:\Users\klui\.claude\plans\validated-hopping-candy.md`. Subsequent phases
should get their own plans.
