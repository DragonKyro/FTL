"""Bake every procedural sprite art.py can produce into a real PNG on
disk under `assets/sprites/`.

Usage:
    python -m ftl.tools.bake_sprites

What gets baked:
- `beacons/<kind>.png` — one orb per encounter kind
- `crew/<species>.png` — one orb per known species, tinted by species color
- `rooms/tile_<state>.png` — room tile panels for full-oxygen, suffocating, foggy variants
- `weapons/<family>_icon.png` — small family-coded weapon icons
- `ships/<id>_silhouette.png` — soft drop shadow + hull silhouette per ship YAML
- `ui/shield_layer.png` — soft halo
- `ui/drop_shadow.png` — soft drop shadow
- `ui/starfield_<key>.png` — pre-baked starfield backgrounds for menu / hangar / star map

The runtime uses these via `AssetCache.texture(key)` when available, and
falls back to procedural generation otherwise. Re-running this script
is safe: it overwrites existing files."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from ftl.config import ASSETS_DIR, CONTENT_DIR
from ftl.data.registry import Registry
from ftl.map.encounter_kind import EncounterKind
from ftl.ui import art


# Color tables mirror what star_map_scene / ship_view consume at runtime.
_BEACON_OUTER: dict[str, tuple[int, int, int]] = {
    EncounterKind.COMBAT.value: (200, 80, 80),
    EncounterKind.EVENT.value: (90, 200, 240),
    EncounterKind.STORE.value: (120, 200, 120),
    EncounterKind.EMPTY.value: (140, 140, 150),
    EncounterKind.FINAL_BOSS.value: (220, 90, 90),
}
_BEACON_INNER: dict[str, tuple[int, int, int]] = {
    EncounterKind.COMBAT.value: (255, 200, 200),
    EncounterKind.EVENT.value: (210, 240, 255),
    EncounterKind.STORE.value: (210, 255, 210),
    EncounterKind.EMPTY.value: (210, 210, 220),
    EncounterKind.FINAL_BOSS.value: (255, 200, 200),
}

_SPECIES_OUTER: dict[str, tuple[int, int, int]] = {
    "sapien": (90, 160, 220),
    "halene": (220, 220, 240),
    "mhirsa": (220, 130, 80),
    "choir": (180, 220, 250),
    "yssari": (140, 220, 180),
    "ferran": (180, 130, 220),
    "loam": (160, 200, 130),
    "drevant": (210, 170, 110),
}

_WEAPON_FAMILY_COLOR: dict[str, tuple[int, int, int]] = {
    "laser":   (255, 230, 90),
    "missile": (220, 140, 80),
    "beam":    (255, 90, 160),
    "bomb":    (140, 220, 240),
    "ion":     (120, 200, 255),
    "flak":    (240, 200, 130),
}


def _lighten(c: tuple[int, int, int], amount: float = 0.55) -> tuple[int, int, int]:
    return (
        min(255, int(c[0] + (255 - c[0]) * amount)),
        min(255, int(c[1] + (255 - c[1]) * amount)),
        min(255, int(c[2] + (255 - c[2]) * amount)),
    )


def _save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG")


def bake_beacons(root: Path) -> int:
    n = 0
    for kind, outer in _BEACON_OUTER.items():
        inner = _BEACON_INNER[kind]
        tex = art.radial_orb(
            128, inner, outer,
            rim=(20, 20, 30), halo=1.6, highlight=True,
        )
        _save(tex.image, root / "sprites" / "beacons" / f"{kind}.png")
        n += 1
    return n


def bake_crew(root: Path) -> int:
    """Build species-flavored crew silhouettes (humanoid / insectoid / etc.)."""
    n = 0
    for species, color in _SPECIES_OUTER.items():
        tex = art.crew_sprite(species, 96, color)
        _save(tex.image, root / "sprites" / "crew" / f"{species}.png")
        n += 1
    return n


def bake_room_tiles(root: Path) -> int:
    """One panel per atmospheric state (full / hypoxic / vacuum / foggy)."""
    states: dict[str, tuple[int, int, int]] = {
        "full":    (40, 48, 64),
        "hypoxic": (60, 40, 50),
        "vacuum":  (60, 30, 30),
        "foggy":   (32, 36, 44),
    }
    n = 0
    for state, fill in states.items():
        top = (min(255, fill[0] + 18), min(255, fill[1] + 18), min(255, fill[2] + 22))
        bottom = (max(0, fill[0] - 10), max(0, fill[1] - 10), max(0, fill[2] - 12))
        tex = art.rounded_panel(
            80, 80, top, bottom,
            radius=8, border=(20, 24, 32), border_w=1, shadow=False,
        )
        _save(tex.image, root / "sprites" / "rooms" / f"tile_{state}.png")
        n += 1
    return n


def bake_weapon_icons(root: Path) -> int:
    """One icon per weapon family — a small glowing orb tinted by family."""
    n = 0
    for family, color in _WEAPON_FAMILY_COLOR.items():
        inner = _lighten(color, 0.60)
        tex = art.radial_orb(
            64, inner, color,
            rim=(15, 15, 20), halo=1.3, highlight=True,
        )
        _save(tex.image, root / "sprites" / "weapons" / f"{family}_icon.png")
        n += 1
    return n


# Per-ship art tuning: silhouette class + hull / accent palette.
# Class controls overall geometry (wings, engines, gun pods). The colors
# tint the hull and the bridge canopy.
_SHIP_PROFILES: dict[str, tuple[str, tuple[int, int, int], tuple[int, int, int]]] = {
    # ship_id -> (class, hull_color, accent_color)
    "wayfarer":         ("courier",     (90, 110, 140), (120, 200, 240)),
    "pilgrim":          ("courier",     (160, 130, 180), (230, 200, 255)),
    "vein_skiff":       ("courier",     (140, 60, 60), (255, 90, 80)),
    "verge_corvette":   ("gunship",     (140, 110, 80), (255, 200, 110)),
    "consilium_lancer": ("lancer",      (90, 150, 180), (220, 240, 255)),
    "concordat_seraph": ("corvette",    (120, 80, 100), (220, 90, 110)),
    "throne_of_ash":    ("dreadnought", (90, 60, 70), (240, 90, 90)),
}


def bake_ship_silhouettes(root: Path) -> int:
    """Paint a hull-shaped silhouette per ship — pointed nose, wings,
    bridge canopy, engine plumes. The shape is driven by a per-ship class
    declared in `_SHIP_PROFILES`."""
    registry = Registry()
    registry.load_all(content_root=CONTENT_DIR)
    if not registry.ships:
        return 0

    n = 0
    width = 320
    height = 200
    default = ("courier", (90, 110, 140), (120, 200, 240))
    for ship_id in registry.ships:
        cls, hull_color, accent = _SHIP_PROFILES.get(ship_id, default)
        tex = art.ship_silhouette(cls, width, height, hull_color, accent)
        _save(tex.image, root / "sprites" / "ships" / f"{ship_id}.png")
        n += 1
    return n


def bake_ui(root: Path) -> int:
    n = 0
    # Shield halo (canonical mid-size).
    tex = art.shield_halo(220, (90, 200, 240), intensity=1.0)
    _save(tex.image, root / "sprites" / "ui" / "shield_layer.png")
    n += 1
    # Generic drop shadow tile (used under ships).
    tex = art.drop_shadow(160, 120, radius=12)
    _save(tex.image, root / "sprites" / "ui" / "drop_shadow.png")
    n += 1
    # Starfields for the three top-level scenes.
    for key, (seed, nebula) in {
        "menu":     (7,  (40, 60, 120)),
        "hangar":   (13, (80, 40, 110)),
        "starmap":  (11, (60, 30, 80)),
        "loadgame": (29, (30, 50, 80)),
    }.items():
        tex = art.starfield(640, 360, seed=seed, nebula=nebula, density=0.0014)
        _save(tex.image, root / "sprites" / "ui" / f"starfield_{key}.png")
        n += 1
    return n


def bake_all(root: Path = ASSETS_DIR) -> None:
    totals: dict[str, int] = {}
    totals["beacons"] = bake_beacons(root)
    totals["crew"] = bake_crew(root)
    totals["rooms"] = bake_room_tiles(root)
    totals["weapons"] = bake_weapon_icons(root)
    totals["ships"] = bake_ship_silhouettes(root)
    totals["ui"] = bake_ui(root)
    print(f"Baked sprites into {root / 'sprites'}:")
    for k, v in totals.items():
        print(f"  {k:8s}  {v} files")
    print(f"  total    {sum(totals.values())} files")


if __name__ == "__main__":
    bake_all()
