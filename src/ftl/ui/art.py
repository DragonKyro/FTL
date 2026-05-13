"""Procedural sprite/texture generator.

Previously every visual was a flat arcade primitive (draw_circle_filled,
draw_lbwh_rectangle_filled). This module bakes richer PIL images at
load-time — radial gradients, soft drop shadows, rounded corners,
multi-stop glows — and wraps them as `arcade.Texture` so they can be
drawn anywhere a rect-and-texture call accepts them.

Textures are cached by parameter tuple so we don't rebuild them per
frame. Callers can request a beacon glow, a rounded room panel, a crew
blob with drop shadow, a soft shield halo, or a starfield background.
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Tuple

import arcade
from PIL import Image, ImageDraw, ImageFilter

from ftl.config import ASSETS_DIR

Color = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]


_TEX_CACHE: dict[tuple, arcade.Texture] = {}
_DISK_CACHE: dict[str, arcade.Texture | None] = {}


def disk_texture(rel_key: str) -> arcade.Texture | None:
    """Load `assets/sprites/<rel_key>.png` as a Texture if it exists.

    Result is cached; returns `None` if the file doesn't exist or fails
    to load. Callers should fall back to procedural generation in that
    case."""
    cached = _DISK_CACHE.get(rel_key)
    if cached is not None or rel_key in _DISK_CACHE:
        return cached
    path = Path(ASSETS_DIR) / "sprites" / f"{rel_key}.png"
    if not path.exists():
        _DISK_CACHE[rel_key] = None
        return None
    try:
        img = Image.open(path).convert("RGBA")
        tex = arcade.Texture(img, hash=f"disk:{rel_key}")
        _DISK_CACHE[rel_key] = tex
        return tex
    except (OSError, ValueError):
        _DISK_CACHE[rel_key] = None
        return None


def _as_rgba(color: Color, alpha: int = 255) -> RGBA:
    return color[0], color[1], color[2], alpha


def _lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def _lerp_color(c1: Color, c2: Color, t: float) -> Color:
    return _lerp(c1[0], c2[0], t), _lerp(c1[1], c2[1], t), _lerp(c1[2], c2[2], t)


def _wrap(image: Image.Image, key: tuple) -> arcade.Texture:
    tex = arcade.Texture(image, hash=f"helixfall:{hash(key) & 0xFFFFFFFF:x}")
    _TEX_CACHE[key] = tex
    return tex


# ---------- Radial orb (beacons, crew, projectiles, generic glows) ---------

def radial_orb(
    size: int,
    inner: Color,
    outer: Color,
    *,
    rim: Color | None = None,
    halo: float = 1.4,
    highlight: bool = True,
) -> arcade.Texture:
    """Soft glowing orb with optional darker rim and inner highlight.

    `halo` widens the outer falloff for a glow aura (>1.0 produces
    visible glow past the orb's nominal radius)."""
    key = ("orb", size, inner, outer, rim, round(halo, 2), highlight)
    cached = _TEX_CACHE.get(key)
    if cached is not None:
        return cached

    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = img.load()
    cx = cy = (s - 1) / 2.0
    r_core = s * 0.42
    r_glow = r_core * halo
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - cx, y - cy)
            if d > r_glow:
                continue
            if d <= r_core:
                t = d / r_core
                col = _lerp_color(inner, outer, t)
                a = 255
            else:
                t = (d - r_core) / max(1e-3, r_glow - r_core)
                col = outer
                a = int(180 * (1.0 - t) ** 2)
            px[x, y] = (col[0], col[1], col[2], a)

    if rim is not None:
        ring = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        rim_w = max(1, int(s * 0.05))
        rd.ellipse(
            (cx - r_core, cy - r_core, cx + r_core, cy + r_core),
            outline=_as_rgba(rim, 180), width=rim_w,
        )
        ring = ring.filter(ImageFilter.GaussianBlur(0.6))
        img = Image.alpha_composite(img, ring)

    if highlight:
        glare = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glare)
        hx, hy = cx - r_core * 0.35, cy - r_core * 0.45
        hr = r_core * 0.42
        gd.ellipse(
            (hx - hr, hy - hr, hx + hr, hy + hr),
            fill=(255, 255, 255, 110),
        )
        glare = glare.filter(ImageFilter.GaussianBlur(r_core * 0.18))
        img = Image.alpha_composite(img, glare)

    return _wrap(img, key)


# ---------- Rounded panel with gradient + inner shadow --------------------

def rounded_panel(
    width: int,
    height: int,
    fill_top: Color,
    fill_bottom: Color | None = None,
    *,
    radius: int = 8,
    border: Color | None = None,
    border_w: int = 1,
    shadow: bool = True,
) -> arcade.Texture:
    """Rounded rectangle with a vertical gradient and soft inner shadow.

    Used for room tiles, store cards, panel chrome."""
    if fill_bottom is None:
        fill_bottom = (
            max(0, fill_top[0] - 18),
            max(0, fill_top[1] - 18),
            max(0, fill_top[2] - 24),
        )
    key = ("panel", width, height, fill_top, fill_bottom, radius, border, border_w, shadow)
    cached = _TEX_CACHE.get(key)
    if cached is not None:
        return cached

    pad = 4 if shadow else 0
    w = width + pad * 2
    h = height + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # gradient fill on a mask of the rounded rect
    grad = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for y in range(height):
        t = y / max(1, height - 1)
        col = _lerp_color(fill_top, fill_bottom, t)
        ImageDraw.Draw(grad).line([(0, y), (width, y)], fill=_as_rgba(col, 255))
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, width - 1, height - 1), radius=radius, fill=255,
    )
    panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    panel.paste(grad, (0, 0), mask)

    # subtle inner shadow at top edge
    inner = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    id_ = ImageDraw.Draw(inner)
    id_.rounded_rectangle(
        (0, 0, width - 1, height - 1), radius=radius,
        outline=(0, 0, 0, 110), width=2,
    )
    inner = inner.filter(ImageFilter.GaussianBlur(1.2))
    panel = Image.alpha_composite(panel, inner)

    if border is not None:
        bd = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(bd).rounded_rectangle(
            (0, 0, width - 1, height - 1), radius=radius,
            outline=_as_rgba(border, 255), width=border_w,
        )
        panel = Image.alpha_composite(panel, bd)

    if shadow:
        shadow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(shadow_img).rounded_rectangle(
            (pad, pad + 2, pad + width - 1, pad + height - 1),
            radius=radius, fill=(0, 0, 0, 130),
        )
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(3.0))
        img = Image.alpha_composite(img, shadow_img)
        img.paste(panel, (pad, pad), panel)
    else:
        img.paste(panel, (0, 0), panel)

    return _wrap(img, key)


# ---------- Soft shield halo (single layer) -------------------------------

def shield_halo(diameter: int, color: Color, *, intensity: float = 1.0) -> arcade.Texture:
    """Soft, multi-stop glowing ring used for shield layers.

    The ring is bright at the boundary and fades inward + outward."""
    key = ("shield", diameter, color, round(intensity, 2))
    cached = _TEX_CACHE.get(key)
    if cached is not None:
        return cached

    s = diameter
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = img.load()
    cx = cy = (s - 1) / 2.0
    r_mid = s * 0.46
    r_band = s * 0.07
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - cx, y - cy)
            if d > r_mid + r_band * 3:
                continue
            dr = (d - r_mid) / r_band
            falloff = math.exp(-dr * dr)
            a = int(220 * intensity * falloff)
            if a <= 0:
                continue
            px[x, y] = (color[0], color[1], color[2], min(255, a))

    img = img.filter(ImageFilter.GaussianBlur(0.5))
    return _wrap(img, key)


# ---------- Soft drop-shadow blob (under ships) ---------------------------

def drop_shadow(width: int, height: int, *, radius: int = 10) -> arcade.Texture:
    key = ("shadow", width, height, radius)
    cached = _TEX_CACHE.get(key)
    if cached is not None:
        return cached
    pad = 18
    w = width + pad * 2
    h = height + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle(
        (pad, pad, pad + width - 1, pad + height - 1),
        radius=radius, fill=(0, 0, 0, 160),
    )
    img = img.filter(ImageFilter.GaussianBlur(8.0))
    return _wrap(img, key)


# ---------- Starfield background ------------------------------------------

def starfield(
    width: int,
    height: int,
    *,
    seed: int = 1,
    density: float = 0.0012,
    bg_top: Color = (8, 10, 18),
    bg_bottom: Color = (2, 3, 8),
    nebula: Color | None = (60, 30, 80),
) -> arcade.Texture:
    """Dark vertical-gradient background sprinkled with stars (some twinkly,
    some dim) and a faint nebula bloom for depth."""
    key = ("stars", width, height, seed, round(density, 5), bg_top, bg_bottom, nebula)
    cached = _TEX_CACHE.get(key)
    if cached is not None:
        return cached

    img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    for y in range(height):
        t = y / max(1, height - 1)
        col = _lerp_color(bg_top, bg_bottom, t)
        ImageDraw.Draw(img).line([(0, y), (width, y)], fill=_as_rgba(col, 255))

    if nebula is not None:
        bloom = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bloom)
        rng_n = random.Random(seed * 31 + 7)
        for _ in range(3):
            bx = rng_n.randint(int(width * 0.15), int(width * 0.85))
            by = rng_n.randint(int(height * 0.15), int(height * 0.85))
            br = rng_n.randint(int(width * 0.12), int(width * 0.22))
            bd.ellipse(
                (bx - br, by - br, bx + br, by + br),
                fill=_as_rgba(nebula, 60),
            )
        bloom = bloom.filter(ImageFilter.GaussianBlur(width * 0.06))
        img = Image.alpha_composite(img, bloom)

    rng = random.Random(seed)
    n_stars = int(width * height * density)
    draw = ImageDraw.Draw(img)
    for _ in range(n_stars):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        b = rng.random()
        if b > 0.985:
            # bright sparkle with glow
            r = rng.randint(2, 3)
            glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse(
                (x - r * 3, y - r * 3, x + r * 3, y + r * 3),
                fill=(180, 200, 255, 60),
            )
            glow = glow.filter(ImageFilter.GaussianBlur(2.0))
            img = Image.alpha_composite(img, glow)
            draw = ImageDraw.Draw(img)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(230, 240, 255, 255))
        elif b > 0.9:
            draw.point((x, y), fill=(200, 215, 240, 220))
        else:
            v = rng.randint(120, 200)
            draw.point((x, y), fill=(v, v + 10, v + 25, 180))

    return _wrap(img, key)


# ---------- Soft circle (generic glow) ------------------------------------

# ---------- Ship silhouettes (hull-shaped, hangar art) --------------------


def _draw_engine_plume(
    img: Image.Image,
    cx: float,
    cy: float,
    radius: float,
    color: Color = (120, 200, 255),
) -> Image.Image:
    """Cyan engine glow blob composited onto `img`."""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=(color[0], color[1], color[2], 220),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.4))
    return Image.alpha_composite(img, glow)


def _ship_courier(
    size_w: int, size_h: int, hull: Color, accent: Color
) -> Image.Image:
    """Slender scout-courier hull — pointed nose, two thin wings, one engine."""
    img = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))

    # Drop shadow.
    shadow = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        (size_w * 0.12, size_h * 0.74,
         size_w * 0.88, size_h * 0.92),
        fill=(0, 0, 0, 170),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(size_w * 0.04))
    img = Image.alpha_composite(img, shadow)

    d = ImageDraw.Draw(img)
    # Wings — two elongated triangles spanning the rear half.
    wing_color = _darken(hull, 0.70)
    d.polygon(
        [
            (size_w * 0.55, size_h * 0.30),
            (size_w * 0.20, size_h * 0.50),
            (size_w * 0.55, size_h * 0.50),
        ],
        fill=(wing_color[0], wing_color[1], wing_color[2], 255),
    )
    d.polygon(
        [
            (size_w * 0.55, size_h * 0.50),
            (size_w * 0.20, size_h * 0.50),
            (size_w * 0.55, size_h * 0.70),
        ],
        fill=(wing_color[0], wing_color[1], wing_color[2], 255),
    )
    # Main hull — pointed nose forward (right), tapered back to engine.
    d.polygon(
        [
            (size_w * 0.92, size_h * 0.50),   # nose
            (size_w * 0.70, size_h * 0.32),
            (size_w * 0.30, size_h * 0.36),
            (size_w * 0.18, size_h * 0.42),   # back-top
            (size_w * 0.18, size_h * 0.58),   # back-bottom
            (size_w * 0.30, size_h * 0.64),
            (size_w * 0.70, size_h * 0.68),
        ],
        fill=(hull[0], hull[1], hull[2], 255),
        outline=(220, 230, 240, 220), width=2,
    )
    # Hull highlight along the top spine.
    hl = _lighten_color(hull, 0.45)
    d.polygon(
        [
            (size_w * 0.88, size_h * 0.50),
            (size_w * 0.70, size_h * 0.38),
            (size_w * 0.30, size_h * 0.42),
            (size_w * 0.22, size_h * 0.46),
        ],
        fill=(hl[0], hl[1], hl[2], 160),
    )
    # Bridge canopy near nose.
    can = _lighten_color(accent, 0.35)
    d.ellipse(
        (size_w * 0.62, size_h * 0.44,
         size_w * 0.78, size_h * 0.56),
        fill=(can[0], can[1], can[2], 240),
        outline=(255, 255, 255, 200), width=1,
    )
    # Engine nozzle at the tail.
    d.rectangle(
        (size_w * 0.10, size_h * 0.46,
         size_w * 0.20, size_h * 0.54),
        fill=(_darken(hull, 0.40)[0], _darken(hull, 0.40)[1], _darken(hull, 0.40)[2], 255),
    )
    # Engine plume glow.
    img = _draw_engine_plume(
        img, size_w * 0.08, size_h * 0.50, size_h * 0.13,
        (120, 200, 255),
    )
    return img


def _ship_gunship(
    size_w: int, size_h: int, hull: Color, accent: Color
) -> Image.Image:
    """Stocky gunship — twin engines, prominent gun pods."""
    img = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        (size_w * 0.10, size_h * 0.74,
         size_w * 0.90, size_h * 0.94),
        fill=(0, 0, 0, 170),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(size_w * 0.045))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)
    # Gun pods (top & bottom) — small rounded rects.
    pod_col = _darken(hull, 0.6)
    d.rounded_rectangle(
        (size_w * 0.40, size_h * 0.20,
         size_w * 0.70, size_h * 0.32),
        radius=4,
        fill=(pod_col[0], pod_col[1], pod_col[2], 255),
        outline=(220, 220, 230, 200), width=1,
    )
    d.rounded_rectangle(
        (size_w * 0.40, size_h * 0.68,
         size_w * 0.70, size_h * 0.80),
        radius=4,
        fill=(pod_col[0], pod_col[1], pod_col[2], 255),
        outline=(220, 220, 230, 200), width=1,
    )
    # Main hull — broad rounded hexagon.
    d.polygon(
        [
            (size_w * 0.90, size_h * 0.50),    # nose
            (size_w * 0.74, size_h * 0.30),
            (size_w * 0.28, size_h * 0.32),
            (size_w * 0.14, size_h * 0.46),
            (size_w * 0.14, size_h * 0.54),
            (size_w * 0.28, size_h * 0.68),
            (size_w * 0.74, size_h * 0.70),
        ],
        fill=(hull[0], hull[1], hull[2], 255),
        outline=(220, 230, 240, 220), width=2,
    )
    hl = _lighten_color(hull, 0.40)
    d.polygon(
        [
            (size_w * 0.86, size_h * 0.50),
            (size_w * 0.74, size_h * 0.36),
            (size_w * 0.28, size_h * 0.38),
            (size_w * 0.20, size_h * 0.46),
        ],
        fill=(hl[0], hl[1], hl[2], 160),
    )
    # Bridge canopy.
    can = _lighten_color(accent, 0.35)
    d.ellipse(
        (size_w * 0.62, size_h * 0.44,
         size_w * 0.78, size_h * 0.56),
        fill=(can[0], can[1], can[2], 240),
        outline=(255, 255, 255, 200), width=1,
    )
    # Twin engines.
    eng_col = _darken(hull, 0.40)
    d.rectangle(
        (size_w * 0.08, size_h * 0.36,
         size_w * 0.18, size_h * 0.46),
        fill=(eng_col[0], eng_col[1], eng_col[2], 255),
    )
    d.rectangle(
        (size_w * 0.08, size_h * 0.54,
         size_w * 0.18, size_h * 0.64),
        fill=(eng_col[0], eng_col[1], eng_col[2], 255),
    )
    img = _draw_engine_plume(img, size_w * 0.06, size_h * 0.41, size_h * 0.10, (180, 130, 90))
    img = _draw_engine_plume(img, size_w * 0.06, size_h * 0.59, size_h * 0.10, (180, 130, 90))
    return img


def _ship_lancer(
    size_w: int, size_h: int, hull: Color, accent: Color
) -> Image.Image:
    """Sleek patrol — long pointed nose, three engines, angled fins."""
    img = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        (size_w * 0.10, size_h * 0.74,
         size_w * 0.92, size_h * 0.92),
        fill=(0, 0, 0, 170),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(size_w * 0.04))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)
    # Angled fins.
    fin_col = _darken(hull, 0.65)
    d.polygon(
        [
            (size_w * 0.50, size_h * 0.35),
            (size_w * 0.18, size_h * 0.22),
            (size_w * 0.30, size_h * 0.42),
        ],
        fill=(fin_col[0], fin_col[1], fin_col[2], 255),
    )
    d.polygon(
        [
            (size_w * 0.50, size_h * 0.65),
            (size_w * 0.18, size_h * 0.78),
            (size_w * 0.30, size_h * 0.58),
        ],
        fill=(fin_col[0], fin_col[1], fin_col[2], 255),
    )
    # Long pointed hull.
    d.polygon(
        [
            (size_w * 0.96, size_h * 0.50),
            (size_w * 0.65, size_h * 0.40),
            (size_w * 0.18, size_h * 0.44),
            (size_w * 0.10, size_h * 0.50),
            (size_w * 0.18, size_h * 0.56),
            (size_w * 0.65, size_h * 0.60),
        ],
        fill=(hull[0], hull[1], hull[2], 255),
        outline=(220, 230, 240, 220), width=2,
    )
    hl = _lighten_color(hull, 0.45)
    d.polygon(
        [
            (size_w * 0.92, size_h * 0.50),
            (size_w * 0.65, size_h * 0.43),
            (size_w * 0.18, size_h * 0.46),
        ],
        fill=(hl[0], hl[1], hl[2], 150),
    )
    # Bridge canopy near nose.
    can = _lighten_color(accent, 0.40)
    d.ellipse(
        (size_w * 0.68, size_h * 0.46,
         size_w * 0.84, size_h * 0.54),
        fill=(can[0], can[1], can[2], 240),
        outline=(255, 255, 255, 200), width=1,
    )
    # Three engine cones.
    eng_col = _darken(hull, 0.45)
    for y_off in (0.46, 0.50, 0.54):
        d.rectangle(
            (size_w * 0.06, size_h * (y_off - 0.014),
             size_w * 0.12, size_h * (y_off + 0.014)),
            fill=(eng_col[0], eng_col[1], eng_col[2], 255),
        )
        img = _draw_engine_plume(img, size_w * 0.04, size_h * y_off,
                                 size_h * 0.05, (180, 220, 255))
    return img


def _ship_corvette(
    size_w: int, size_h: int, hull: Color, accent: Color
) -> Image.Image:
    """Heavy corvette — wide hull, big wings, twin large engines."""
    img = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        (size_w * 0.08, size_h * 0.72,
         size_w * 0.92, size_h * 0.94),
        fill=(0, 0, 0, 175),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(size_w * 0.05))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)
    # Wide swept wings.
    wing_col = _darken(hull, 0.60)
    d.polygon(
        [
            (size_w * 0.65, size_h * 0.32),
            (size_w * 0.30, size_h * 0.10),
            (size_w * 0.20, size_h * 0.30),
            (size_w * 0.55, size_h * 0.45),
        ],
        fill=(wing_col[0], wing_col[1], wing_col[2], 255),
    )
    d.polygon(
        [
            (size_w * 0.65, size_h * 0.68),
            (size_w * 0.30, size_h * 0.90),
            (size_w * 0.20, size_h * 0.70),
            (size_w * 0.55, size_h * 0.55),
        ],
        fill=(wing_col[0], wing_col[1], wing_col[2], 255),
    )
    # Main hull — large rounded form.
    d.polygon(
        [
            (size_w * 0.94, size_h * 0.50),
            (size_w * 0.78, size_h * 0.28),
            (size_w * 0.30, size_h * 0.32),
            (size_w * 0.14, size_h * 0.40),
            (size_w * 0.14, size_h * 0.60),
            (size_w * 0.30, size_h * 0.68),
            (size_w * 0.78, size_h * 0.72),
        ],
        fill=(hull[0], hull[1], hull[2], 255),
        outline=(230, 240, 245, 220), width=2,
    )
    hl = _lighten_color(hull, 0.45)
    d.polygon(
        [
            (size_w * 0.92, size_h * 0.50),
            (size_w * 0.78, size_h * 0.34),
            (size_w * 0.30, size_h * 0.38),
            (size_w * 0.20, size_h * 0.42),
        ],
        fill=(hl[0], hl[1], hl[2], 160),
    )
    # Bridge canopy.
    can = _lighten_color(accent, 0.35)
    d.ellipse(
        (size_w * 0.64, size_h * 0.42,
         size_w * 0.82, size_h * 0.58),
        fill=(can[0], can[1], can[2], 240),
        outline=(255, 255, 255, 200), width=1,
    )
    # Twin big engines.
    eng_col = _darken(hull, 0.45)
    d.rectangle(
        (size_w * 0.06, size_h * 0.36,
         size_w * 0.18, size_h * 0.48),
        fill=(eng_col[0], eng_col[1], eng_col[2], 255),
    )
    d.rectangle(
        (size_w * 0.06, size_h * 0.52,
         size_w * 0.18, size_h * 0.64),
        fill=(eng_col[0], eng_col[1], eng_col[2], 255),
    )
    img = _draw_engine_plume(img, size_w * 0.05, size_h * 0.42,
                             size_h * 0.12, (220, 130, 90))
    img = _draw_engine_plume(img, size_w * 0.05, size_h * 0.58,
                             size_h * 0.12, (220, 130, 90))
    return img


def _ship_dreadnought(
    size_w: int, size_h: int, hull: Color, accent: Color
) -> Image.Image:
    """Dreadnought — massive multi-decked hull, four engines, four gun pods."""
    img = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        (size_w * 0.06, size_h * 0.70,
         size_w * 0.94, size_h * 0.94),
        fill=(0, 0, 0, 180),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(size_w * 0.05))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)
    # Outer hull plates (top & bottom wings).
    wing_col = _darken(hull, 0.55)
    d.polygon(
        [
            (size_w * 0.78, size_h * 0.25),
            (size_w * 0.30, size_h * 0.12),
            (size_w * 0.12, size_h * 0.25),
            (size_w * 0.35, size_h * 0.40),
            (size_w * 0.65, size_h * 0.42),
        ],
        fill=(wing_col[0], wing_col[1], wing_col[2], 255),
    )
    d.polygon(
        [
            (size_w * 0.78, size_h * 0.75),
            (size_w * 0.30, size_h * 0.88),
            (size_w * 0.12, size_h * 0.75),
            (size_w * 0.35, size_h * 0.60),
            (size_w * 0.65, size_h * 0.58),
        ],
        fill=(wing_col[0], wing_col[1], wing_col[2], 255),
    )
    # Four big gun pods.
    pod_col = _darken(hull, 0.50)
    for y_frac in (0.18, 0.32, 0.68, 0.82):
        d.rounded_rectangle(
            (size_w * 0.55, size_h * (y_frac - 0.04),
             size_w * 0.78, size_h * (y_frac + 0.04)),
            radius=3,
            fill=(pod_col[0], pod_col[1], pod_col[2], 255),
            outline=(220, 220, 230, 200), width=1,
        )
        # Gun barrel.
        d.rectangle(
            (size_w * 0.78, size_h * (y_frac - 0.012),
             size_w * 0.88, size_h * (y_frac + 0.012)),
            fill=(80, 80, 90, 255),
        )
    # Main central hull.
    d.polygon(
        [
            (size_w * 0.96, size_h * 0.50),
            (size_w * 0.80, size_h * 0.34),
            (size_w * 0.30, size_h * 0.36),
            (size_w * 0.10, size_h * 0.46),
            (size_w * 0.10, size_h * 0.54),
            (size_w * 0.30, size_h * 0.64),
            (size_w * 0.80, size_h * 0.66),
        ],
        fill=(hull[0], hull[1], hull[2], 255),
        outline=(240, 240, 245, 220), width=2,
    )
    hl = _lighten_color(hull, 0.40)
    d.polygon(
        [
            (size_w * 0.94, size_h * 0.50),
            (size_w * 0.80, size_h * 0.38),
            (size_w * 0.30, size_h * 0.42),
            (size_w * 0.14, size_h * 0.46),
        ],
        fill=(hl[0], hl[1], hl[2], 160),
    )
    # Bridge canopy (red — ominous).
    d.ellipse(
        (size_w * 0.72, size_h * 0.44,
         size_w * 0.86, size_h * 0.56),
        fill=(accent[0], accent[1], accent[2], 240),
        outline=(255, 255, 255, 200), width=1,
    )
    # Four engine plumes.
    eng_col = _darken(hull, 0.50)
    for y_frac in (0.40, 0.47, 0.53, 0.60):
        d.rectangle(
            (size_w * 0.04, size_h * (y_frac - 0.025),
             size_w * 0.12, size_h * (y_frac + 0.025)),
            fill=(eng_col[0], eng_col[1], eng_col[2], 255),
        )
        img = _draw_engine_plume(img, size_w * 0.03, size_h * y_frac,
                                 size_h * 0.05, (255, 80, 80))
    return img


_SHIP_CLASS_BUILDERS: dict[str, callable] = {
    "courier":     _ship_courier,
    "gunship":     _ship_gunship,
    "lancer":      _ship_lancer,
    "corvette":    _ship_corvette,
    "dreadnought": _ship_dreadnought,
}


def ship_silhouette(
    class_name: str,
    width: int,
    height: int,
    hull: Color,
    accent: Color = (90, 200, 240),
) -> arcade.Texture:
    """Build a stylized ship hull silhouette of the given class.

    Classes: courier, gunship, lancer, corvette, dreadnought."""
    key = ("ship_sil", class_name, width, height, hull, accent)
    cached = _TEX_CACHE.get(key)
    if cached is not None:
        return cached
    builder = _SHIP_CLASS_BUILDERS.get(class_name, _ship_courier)
    img = builder(width, height, hull, accent)
    return _wrap(img, key)


# ---------- Crew silhouettes (species-flavored) ---------------------------

def _darken(c: Color, amount: float = 0.5) -> Color:
    return int(c[0] * amount), int(c[1] * amount), int(c[2] * amount)


def _lighten_color(c: Color, amount: float = 0.5) -> Color:
    return (
        min(255, int(c[0] + (255 - c[0]) * amount)),
        min(255, int(c[1] + (255 - c[1]) * amount)),
        min(255, int(c[2] + (255 - c[2]) * amount)),
    )


def _draw_body_ellipse(
    d: ImageDraw.ImageDraw,
    bbox: tuple[float, float, float, float],
    color: Color,
) -> None:
    """Ellipse with a top highlight + bottom shadow, for soft volume."""
    rgba = (color[0], color[1], color[2], 255)
    d.ellipse(bbox, fill=rgba)
    # Highlight on the upper-left half.
    left, top, right, bottom = bbox
    w = right - left
    h = bottom - top
    hl = _lighten_color(color, 0.55)
    d.ellipse(
        (left + w * 0.18, top + h * 0.12, left + w * 0.62, top + h * 0.48),
        fill=(hl[0], hl[1], hl[2], 110),
    )


def _eye(d: ImageDraw.ImageDraw, x: float, y: float, r: float, glow: Color | None = None) -> None:
    if glow is not None:
        d.ellipse(
            (x - r * 2, y - r * 2, x + r * 2, y + r * 2),
            fill=(glow[0], glow[1], glow[2], 80),
        )
    d.ellipse((x - r, y - r, x + r, y + r), fill=(15, 18, 24, 255))


def _draw_shadow_under(
    img: Image.Image, cx: float, base_y: float, w: float
) -> Image.Image:
    """Soft elliptical drop shadow at the crew's feet."""
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(
        (cx - w * 0.55, base_y - 3, cx + w * 0.55, base_y + 6),
        fill=(0, 0, 0, 140),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(2.0))
    return Image.alpha_composite(img, sh)


def _crew_human(size: int, color: Color, *, helmet: bool = False) -> Image.Image:
    """Sapien / Ferran / Yssari template — round head, oval body."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = size / 2
    base_y = size * 0.92
    body_w = size * 0.55
    body_h = size * 0.45
    head_r = size * 0.22

    # Body (torso).
    body_top = base_y - body_h
    _draw_body_ellipse(
        d,
        (cx - body_w / 2, body_top, cx + body_w / 2, base_y),
        color,
    )
    # Head.
    head_cy = body_top - head_r * 0.4
    head_color = _lighten_color(color, 0.15) if not helmet else _darken(color, 0.6)
    _draw_body_ellipse(
        d,
        (cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r),
        head_color,
    )
    if helmet:
        # Visor strip across the head.
        d.rectangle(
            (cx - head_r * 0.7, head_cy - head_r * 0.15,
             cx + head_r * 0.7, head_cy + head_r * 0.15),
            fill=(40, 200, 255, 240),
        )
    else:
        # Two small eyes.
        _eye(d, cx - head_r * 0.35, head_cy - head_r * 0.08, max(1.0, size * 0.025))
        _eye(d, cx + head_r * 0.35, head_cy - head_r * 0.08, max(1.0, size * 0.025))
    # Arms — thin ellipses on either side of body.
    arm_w = body_w * 0.18
    arm_h = body_h * 0.7
    _draw_body_ellipse(
        d,
        (cx - body_w / 2 - arm_w * 0.7, body_top + body_h * 0.18,
         cx - body_w / 2 + arm_w * 0.5, body_top + body_h * 0.18 + arm_h),
        _darken(color, 0.8),
    )
    _draw_body_ellipse(
        d,
        (cx + body_w / 2 - arm_w * 0.5, body_top + body_h * 0.18,
         cx + body_w / 2 + arm_w * 0.7, body_top + body_h * 0.18 + arm_h),
        _darken(color, 0.8),
    )
    return _draw_shadow_under(img, cx, base_y, body_w)


def _crew_robot(size: int, color: Color) -> Image.Image:
    """Halene — synthetic, rectangular head + chest panel + antenna."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = size / 2
    base_y = size * 0.92
    body_w = size * 0.50
    body_h = size * 0.42
    head_w = size * 0.40
    head_h = size * 0.34

    # Body — rounded rect.
    body_top = base_y - body_h
    d.rounded_rectangle(
        (cx - body_w / 2, body_top, cx + body_w / 2, base_y),
        radius=int(size * 0.06),
        fill=(color[0], color[1], color[2], 255),
    )
    # Chest plate highlight.
    hl = _lighten_color(color, 0.35)
    d.rounded_rectangle(
        (cx - body_w / 3, body_top + body_h * 0.18,
         cx + body_w / 3, body_top + body_h * 0.55),
        radius=int(size * 0.04),
        fill=(hl[0], hl[1], hl[2], 220),
    )
    # Head — rounded rect, slightly darker than body.
    dk = _darken(color, 0.78)
    head_top = body_top - head_h * 0.85
    d.rounded_rectangle(
        (cx - head_w / 2, head_top, cx + head_w / 2, head_top + head_h),
        radius=int(size * 0.06),
        fill=(dk[0], dk[1], dk[2], 255),
    )
    # Antenna.
    d.line(
        (cx, head_top, cx, head_top - size * 0.10),
        fill=(220, 220, 220, 230), width=max(1, int(size * 0.02)),
    )
    d.ellipse(
        (cx - size * 0.03, head_top - size * 0.13,
         cx + size * 0.03, head_top - size * 0.07),
        fill=(255, 220, 90, 255),
    )
    # Single glowing optic.
    eye_y = head_top + head_h * 0.45
    _eye(d, cx, eye_y, max(1.5, size * 0.05), glow=(120, 220, 255))
    # Arms — chunky.
    d.rounded_rectangle(
        (cx - body_w / 2 - size * 0.10, body_top + body_h * 0.18,
         cx - body_w / 2 + size * 0.02, body_top + body_h * 0.85),
        radius=int(size * 0.04),
        fill=(dk[0], dk[1], dk[2], 255),
    )
    d.rounded_rectangle(
        (cx + body_w / 2 - size * 0.02, body_top + body_h * 0.18,
         cx + body_w / 2 + size * 0.10, body_top + body_h * 0.85),
        radius=int(size * 0.04),
        fill=(dk[0], dk[1], dk[2], 255),
    )
    return _draw_shadow_under(img, cx, base_y, body_w)


def _crew_insectoid(size: int, color: Color) -> Image.Image:
    """Mhirsa — chitinous body, mandibles, antennae, multi-legged."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = size / 2
    base_y = size * 0.88
    body_w = size * 0.58
    body_h = size * 0.40
    head_r = size * 0.18
    body_top = base_y - body_h

    # Legs (lines) under the body.
    leg_color = (_darken(color, 0.55)[0], _darken(color, 0.55)[1], _darken(color, 0.55)[2], 240)
    for i, off in enumerate((-0.35, -0.1, 0.1, 0.35)):
        leg_x_top = cx + body_w * off / 2
        leg_x_bot = leg_x_top + (body_w * 0.18 * (1 if i % 2 == 0 else -1))
        d.line(
            (leg_x_top, base_y - body_h * 0.2,
             leg_x_bot, base_y + body_h * 0.05),
            fill=leg_color, width=max(2, int(size * 0.035)),
        )
    # Abdomen (segmented oval).
    _draw_body_ellipse(
        d,
        (cx - body_w / 2, body_top, cx + body_w / 2, base_y),
        color,
    )
    # Segmentation lines.
    seg_col = (_darken(color, 0.5)[0], _darken(color, 0.5)[1], _darken(color, 0.5)[2], 220)
    for f in (0.35, 0.6):
        d.line(
            (cx - body_w / 2 * 0.85, body_top + body_h * f,
             cx + body_w / 2 * 0.85, body_top + body_h * f),
            fill=seg_col, width=max(1, int(size * 0.02)),
        )
    # Head (smaller circle in front of body).
    head_cy = body_top - head_r * 0.4
    _draw_body_ellipse(
        d,
        (cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r),
        _darken(color, 0.85),
    )
    # Mandibles — two short curves either side of mouth.
    mand_color = (_darken(color, 0.4)[0], _darken(color, 0.4)[1], _darken(color, 0.4)[2], 255)
    d.line(
        (cx - head_r * 0.6, head_cy + head_r * 0.5,
         cx - head_r * 0.95, head_cy + head_r * 0.95),
        fill=mand_color, width=max(2, int(size * 0.03)),
    )
    d.line(
        (cx + head_r * 0.6, head_cy + head_r * 0.5,
         cx + head_r * 0.95, head_cy + head_r * 0.95),
        fill=mand_color, width=max(2, int(size * 0.03)),
    )
    # Compound eyes — bright orbs.
    _eye(d, cx - head_r * 0.45, head_cy - head_r * 0.05,
         max(1.5, size * 0.04), glow=_lighten_color(color, 0.7))
    _eye(d, cx + head_r * 0.45, head_cy - head_r * 0.05,
         max(1.5, size * 0.04), glow=_lighten_color(color, 0.7))
    # Antennae — thin lines arching upward.
    ant_col = (_darken(color, 0.7)[0], _darken(color, 0.7)[1], _darken(color, 0.7)[2], 230)
    d.line(
        (cx - head_r * 0.3, head_cy - head_r * 0.9,
         cx - head_r * 0.8, head_cy - head_r * 1.8),
        fill=ant_col, width=max(1, int(size * 0.02)),
    )
    d.line(
        (cx + head_r * 0.3, head_cy - head_r * 0.9,
         cx + head_r * 0.8, head_cy - head_r * 1.8),
        fill=ant_col, width=max(1, int(size * 0.02)),
    )
    return _draw_shadow_under(img, cx, base_y, body_w)


def _crew_psychic(size: int, color: Color) -> Image.Image:
    """Choir — tall draped form, glow halo, single large eye."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = size / 2
    base_y = size * 0.92
    body_w = size * 0.40
    body_h = size * 0.62
    head_r = size * 0.18

    # Robe — tall narrow ellipse.
    body_top = base_y - body_h
    _draw_body_ellipse(
        d,
        (cx - body_w / 2, body_top, cx + body_w / 2, base_y),
        color,
    )
    # Head.
    head_cy = body_top - head_r * 0.15
    _draw_body_ellipse(
        d,
        (cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r),
        _lighten_color(color, 0.15),
    )
    # Halo glow around head.
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gl_col = _lighten_color(color, 0.8)
    ImageDraw.Draw(glow).ellipse(
        (cx - head_r * 2.0, head_cy - head_r * 2.0,
         cx + head_r * 2.0, head_cy + head_r * 2.0),
        fill=(gl_col[0], gl_col[1], gl_col[2], 90),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.05))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)
    # Single glowing inner eye (vertical slit).
    eye_color = _lighten_color(color, 0.9)
    d.ellipse(
        (cx - head_r * 0.18, head_cy - head_r * 0.35,
         cx + head_r * 0.18, head_cy + head_r * 0.30),
        fill=(eye_color[0], eye_color[1], eye_color[2], 255),
    )
    return _draw_shadow_under(img, cx, base_y, body_w)


def _crew_plantlike(size: int, color: Color) -> Image.Image:
    """Loam — short rounded body, leafy crown."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = size / 2
    base_y = size * 0.93
    body_w = size * 0.60
    body_h = size * 0.50
    body_top = base_y - body_h
    _draw_body_ellipse(
        d,
        (cx - body_w / 2, body_top, cx + body_w / 2, base_y),
        color,
    )
    # Sleepy eyes.
    _eye(d, cx - body_w * 0.18, body_top + body_h * 0.30, max(1.0, size * 0.025))
    _eye(d, cx + body_w * 0.18, body_top + body_h * 0.30, max(1.0, size * 0.025))
    # Soft smile (small dark arc — approximate by a thick line).
    d.arc(
        (cx - body_w * 0.18, body_top + body_h * 0.32,
         cx + body_w * 0.18, body_top + body_h * 0.60),
        start=20, end=160,
        fill=(20, 25, 30, 200), width=max(1, int(size * 0.02)),
    )
    # Leaf crown — three pointed ellipses fanning upward.
    leaf_color = _darken(color, 0.7)
    for angle_deg, scale in ((-30, 1.0), (0, 1.15), (30, 1.0)):
        # rotate would require new image; approximate by offset ellipse.
        import math as _math

        ang = _math.radians(angle_deg)
        lx = cx + _math.sin(ang) * body_w * 0.3
        ly = body_top - _math.cos(ang) * body_h * 0.35 * scale
        leaf_w = size * 0.10
        leaf_h = size * 0.20 * scale
        d.ellipse(
            (lx - leaf_w, ly - leaf_h, lx + leaf_w, ly + leaf_h * 0.3),
            fill=(leaf_color[0], leaf_color[1], leaf_color[2], 250),
        )
    return _draw_shadow_under(img, cx, base_y, body_w)


def _crew_hooded(size: int, color: Color) -> Image.Image:
    """Yssari — cloaked silhouette with no visible face (mind-shielded)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = size / 2
    base_y = size * 0.93
    body_w = size * 0.55
    body_h = size * 0.55
    body_top = base_y - body_h
    # Cloak body — wider at the base.
    cloak_color = _darken(color, 0.65)
    d.polygon(
        [
            (cx - body_w / 2, base_y),
            (cx - body_w * 0.3, body_top + body_h * 0.2),
            (cx + body_w * 0.3, body_top + body_h * 0.2),
            (cx + body_w / 2, base_y),
        ],
        fill=(cloak_color[0], cloak_color[1], cloak_color[2], 255),
    )
    # Hood — rounded shape on top.
    hood_w = body_w * 0.55
    hood_h = size * 0.40
    hood_top = body_top - hood_h * 0.55
    _draw_body_ellipse(
        d,
        (cx - hood_w / 2, hood_top, cx + hood_w / 2, hood_top + hood_h),
        color,
    )
    # Face shadow — deep dark void inside the hood.
    void_color = (10, 10, 14, 255)
    d.ellipse(
        (cx - hood_w * 0.35, hood_top + hood_h * 0.30,
         cx + hood_w * 0.35, hood_top + hood_h * 0.85),
        fill=void_color,
    )
    # Two faint glowing eyes within the void.
    eye_glow = _lighten_color(color, 0.8)
    for off in (-0.18, 0.18):
        ex = cx + hood_w * off
        ey = hood_top + hood_h * 0.55
        d.ellipse(
            (ex - size * 0.015, ey - size * 0.015,
             ex + size * 0.015, ey + size * 0.015),
            fill=(eye_glow[0], eye_glow[1], eye_glow[2], 240),
        )
    return _draw_shadow_under(img, cx, base_y, body_w)


def _crew_engineer(size: int, color: Color) -> Image.Image:
    """Drevant — hunched, goggled engineer."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = size / 2
    base_y = size * 0.93
    body_w = size * 0.58
    body_h = size * 0.42
    head_r = size * 0.20
    body_top = base_y - body_h
    # Body (slightly squatter than human).
    _draw_body_ellipse(
        d,
        (cx - body_w / 2, body_top, cx + body_w / 2, base_y),
        color,
    )
    # Tool-belt accent strip.
    belt_col = _darken(color, 0.55)
    d.rectangle(
        (cx - body_w / 2 + 2, body_top + body_h * 0.6,
         cx + body_w / 2 - 2, body_top + body_h * 0.74),
        fill=(belt_col[0], belt_col[1], belt_col[2], 240),
    )
    # Head, leaning slightly forward (offset right).
    head_cy = body_top - head_r * 0.25
    head_cx = cx + size * 0.02
    _draw_body_ellipse(
        d,
        (head_cx - head_r, head_cy - head_r,
         head_cx + head_r, head_cy + head_r),
        _lighten_color(color, 0.15),
    )
    # Goggles — two black circles linked by a strip.
    g_y = head_cy - head_r * 0.10
    g_r = head_r * 0.32
    for off in (-0.4, 0.4):
        gx = head_cx + head_r * off
        d.ellipse(
            (gx - g_r, g_y - g_r, gx + g_r, g_y + g_r),
            fill=(20, 24, 30, 255),
            outline=(180, 180, 190, 255), width=1,
        )
        # Inner glow.
        d.ellipse(
            (gx - g_r * 0.5, g_y - g_r * 0.5,
             gx + g_r * 0.5, g_y + g_r * 0.5),
            fill=(255, 220, 120, 230),
        )
    d.line(
        (head_cx - head_r * 0.08, g_y, head_cx + head_r * 0.08, g_y),
        fill=(20, 24, 30, 255), width=max(2, int(size * 0.025)),
    )
    return _draw_shadow_under(img, cx, base_y, body_w)


_CREW_BUILDERS: dict[str, callable] = {
    "sapien":  lambda s, c: _crew_human(s, c),
    "halene":  lambda s, c: _crew_robot(s, c),
    "mhirsa":  lambda s, c: _crew_insectoid(s, c),
    "choir":   lambda s, c: _crew_psychic(s, c),
    "yssari":  lambda s, c: _crew_hooded(s, c),
    "ferran":  lambda s, c: _crew_human(s, c, helmet=True),
    "loam":    lambda s, c: _crew_plantlike(s, c),
    "drevant": lambda s, c: _crew_engineer(s, c),
}


def crew_sprite(species_id: str, size: int, color: Color) -> arcade.Texture:
    """Build a small species-flavored crew silhouette and wrap as Texture."""
    key = ("crew_sprite", species_id, size, color)
    cached = _TEX_CACHE.get(key)
    if cached is not None:
        return cached
    builder = _CREW_BUILDERS.get(species_id)
    if builder is None:
        # Unknown species — fall back to the orb.
        return radial_orb(size, _lighten_color(color, 0.55), color,
                          rim=(20, 22, 30), halo=1.25, highlight=True)
    img = builder(size, color)
    return _wrap(img, key)


# ---------- Soft circle (generic glow) ------------------------------------

def soft_circle(diameter: int, color: Color, *, alpha: int = 200) -> arcade.Texture:
    key = ("soft", diameter, color, alpha)
    cached = _TEX_CACHE.get(key)
    if cached is not None:
        return cached
    s = diameter
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = img.load()
    cx = cy = (s - 1) / 2.0
    r = s / 2.0
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - cx, y - cy)
            if d > r:
                continue
            t = d / r
            a = int(alpha * (1.0 - t) ** 2)
            px[x, y] = (color[0], color[1], color[2], a)
    return _wrap(img, key)


# ---------- Convenience: draw a texture at a rect-by-center ---------------

def draw_centered(
    tex: arcade.Texture,
    cx: float,
    cy: float,
    size: float | None = None,
    *,
    fit: bool = False,
) -> None:
    """Draw `tex` centered at (cx, cy).

    - `size=None` uses the texture's natural width/height.
    - `size=N, fit=False` (default) forces a square N×N rectangle.
    - `size=N, fit=True` preserves the texture's aspect ratio, scaled so
      the longer edge is N pixels."""
    if size is None:
        w = tex.width
        h = tex.height
    elif fit:
        if tex.width >= tex.height:
            w = size
            h = size * (tex.height / max(1, tex.width))
        else:
            h = size
            w = size * (tex.width / max(1, tex.height))
    else:
        w = h = size
    rect = arcade.LBWH(cx - w / 2, cy - h / 2, w, h)
    arcade.draw_texture_rect(tex, rect)
