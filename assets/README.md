# Assets

This folder holds binary game assets — sprites, sounds, music, fonts.

## During Phase 0+1

Empty / placeholder. The runtime falls back to procedurally drawn shapes
and colored rectangles when an expected asset isn't present, so the game
remains playable without art.

## Rules

- Assets are **original** to this project, or sourced under permissive
  licenses (CC0 / CC-BY with attribution, in `LICENSES.md` next to the file).
- Do **not** commit ripped or extracted assets from FTL: Faster Than Light,
  FTL Multiverse, or any other game. This is a personal project but
  cleanliness here keeps it ours.
- One sprite per file. PNG with transparent background preferred.
- Sound effects: WAV (short) or OGG (longer / music).

## Layout

- `sprites/ships/` — ship hull outlines and interior tiles
- `sprites/crew/` — per-species crew sprites
- `sprites/weapons/` — weapon mount icons, projectile/beam visuals
- `sprites/ui/` — buttons, panel chrome, icons
- `sprites/effects/` — explosions, fire, breach, shield ripples
- `sounds/sfx/` — short effects
- `sounds/music/` — ambient / combat / menu tracks
- `fonts/` — UI fonts
