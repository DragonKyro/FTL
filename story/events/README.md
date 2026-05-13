# Story events

Story events are the narrative beats the player encounters at beacons:
distress calls, ambushes, derelict ships, civilian encounters, faction
intrigue, quest hooks. Each event lives as a YAML file under one of the
faction subfolders here (or `generic/` for faction-agnostic encounters).

**Read [the worldbuilding canon](../worldbuilding/) before authoring
events.** Start with [SETTING.md](../worldbuilding/SETTING.md) and
[conflicts.md](../worldbuilding/conflicts.md). Faction-specific events
must follow the faction's profile in
[worldbuilding/factions/](../worldbuilding/factions/).

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

Outcomes are referenced by `outcome_id` and wired up by the event engine
in `src/ftl/events/`. Outcome details (scrap, fuel, hull damage, combat
starts, story flags) will live alongside the event in later phases.

## Folder layout

Folders here mirror the **canonical factions** in
[../worldbuilding/factions/](../worldbuilding/factions/):

- `generic/` — faction-agnostic encounters (any sector).
- `civilian/` — neutral civilians, refugees, traders.
- `pirate/` — Black Vein Syndicate operations.
- `rebel/` — legacy folder; new Iron Concordat content should prefer
  a renamed folder once we settle the canonical short name.
- `faction_a/` … `faction_e/` — **renaming planned.** These placeholder
  folders will be reorganized into canonical names below as content
  arrives:
  - `consilium/` — Consilium of Stars
  - `concordat/` — Iron Concordat
  - `verge/` — Mercatile Verge
  - `black_vein/` — Black Vein Syndicate
  - `choral/` — Choral Order
  - `unmade/` — The Unmade
  - `verdantis/` — The Verdantis
  - `splice/` — The Splice
  - `mhirsa/` — Mhirsa Compact
  - `andrachen/` — House Andrachen-in-Exile
  - `drift/` — Drift Communes
  - `lattice/` — The Lattice
  - `wardens/` — Quarantine Wardens
  - `vassirin/` — Twin Houses (Vellis & Lirath)
- `abandoned/` — derelicts, hulks, ghost ships, ex-Andrachen
  breeder-stations, sealed-Gate wrecks.

Outerlight events have no dedicated folder — they appear as
decorating overlays on other encounters near failing Gates.

## Authoring guidance

- **Voice should match the faction's profile.** A Choral Order event
  reads mystical, thoughtful, ambiguously prophetic. A Black Vein
  event reads cynical, transactional, dangerous. A Mhirsa event reads
  earned, watchful, never quite at rest. See the faction profiles in
  [../worldbuilding/factions/](../worldbuilding/factions/).
- **No FTL/Multiverse names anywhere.** Use the canonical names:
  Sapien, Choir, Halene, Ferran, Mhirsa, Argonite, Yssari, Vor,
  Drevant, Karrukai, Loam, Vellisian, Lirathi, Hollow, Whisperborn,
  Spliced. Faction names as listed above.
- **Outcomes should be meaningful.** A choice that gives 5 scrap is
  weaker than a choice that costs 5 scrap and grants a Choral Order
  story flag. Story flags compound across the run.
- **Most events should *not* trigger combat.** Combat is one outcome
  among many; surprise, friendship, betrayal, and mystery are others.
  Vanilla FTL is roughly 30% combat-events. Helixfall should aim
  lower — closer to 20% — to let the world breathe.
