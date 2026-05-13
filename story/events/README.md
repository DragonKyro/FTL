# Story events

Story events are the narrative beats the player encounters at beacons:
distress calls, ambushes, derelict ships, civilian encounters, faction
intrigue, quest hooks, etc. Each event lives as a YAML file under one of
the faction subfolders here (or `generic/` for faction-agnostic encounters).

## Schema

```yaml
id: unique_event_id          # required
name: Display Name           # required
description: optional internal note
text: |
  The text shown to the player when this event triggers.
choices:
  - text: First option visible to the player.
    outcome_id: outcome_key
  - text: Second option.
    outcome_id: another_outcome_key
triggers: []                 # optional flag/condition gating
```

Outcomes are referenced by `outcome_id` and wired up by the event engine in
`src/ftl/events/`. Outcome details (scrap, fuel, hull damage, combat starts,
story flags) will live in a sibling YAML file in a later phase.

## Worldbuilding scratchpad

This project's setting is original. Don't import names, races, or factions
from FTL or FTL Multiverse — invent equivalents.

- **Sapien** — baseline humanoid; the "default" species.
- **Free Traders** — independent merchant caravans of the borderlands.
- (More to come as the world fleshes out.)

## Folder layout

- `generic/` — faction-agnostic encounters that can appear in any sector.
- `civilian/` — neutral civilian encounters.
- `pirate/`, `rebel/` — hostile factions.
- `faction_a/` … `faction_e/` — placeholder folders for original factions
  still being designed. Rename as the world-building takes shape.
- `abandoned/` — derelicts, hulks, ghost ships.
