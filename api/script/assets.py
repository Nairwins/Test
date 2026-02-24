# ============================================================
#  presets.py  –  All lookups, palettes & shape registries
# ============================================================

import os

# ----------------------------
# Base directories
# ----------------------------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INNER_DIR  = os.path.join(BASE_DIR, "inner")
OUTER_DIR  = os.path.join(BASE_DIR, "outer")
ICON_DIR   = os.path.join(BASE_DIR, "icon")

# ----------------------------
# Friendly colour names
# ----------------------------
COLORS = {
    # basics
    "black":       "#000000",
    "white":       "#ffffff",
    "red":         "#e63946",
    "green":       "#226422",
    "blue":        "#1d3557",
    "navy":        "#0a1628",
    "orange":      "#f4a261",
    "yellow":      "#e9c46a",
    "pink":        "#e63b8a",
    "purple":      "#7b2d8b",
    "teal":        "#2a9d8f",
    "cyan":        "#48cae4",
    "coral":       "#e76f51",
    "gold":        "#d4af37",
    "silver":      "#a8a9ad",
    "lime":        "#70e000",
    "indigo":      "#3a0ca3",
    "brown":       "#6d4c41",
    "gray":        "#6c757d",
    "darkgray":    "#343a40",
    # gradients end colours (commonly paired)
    "deep_red":    "#7b0000",
    "deep_green":  "#0d3b0d",
    "deep_blue":   "#03045e",
    "light_blue":  "#90e0ef",
    "light_pink":  "#ffb3c6",
}

# ----------------------------
# Gradient direction names
# ----------------------------
GRADIENTS = {
    "left_right":    "left_to_right",
    "right_left":    "right_to_left",
    "top_bottom":    "top_to_bottom",
    "bottom_top":    "bottom_to_top",
    "diagonal":      "diagonal_tl_br",
    "diagonal_rev":  "diagonal_tr_bl",
    "radial":        "radial",
    # aliases
    "horizontal":    "left_to_right",
    "vertical":      "top_to_bottom",
    "center":        "radial",
}

# ----------------------------
# Inner eye shapes  (filename without .svg)
# ----------------------------
INNER_SHAPES = {
    "cloud":    os.path.join(INNER_DIR, "cloud.svg"),
    "flower":   os.path.join(INNER_DIR, "flower.svg"),
    "heart":    os.path.join(INNER_DIR, "heart.svg"),
    "rounded":  os.path.join(INNER_DIR, "rounded.svg"),
    "sphere":   os.path.join(INNER_DIR, "sphere.svg"),
    "target":   os.path.join(INNER_DIR, "target.svg"),
    "x":        os.path.join(INNER_DIR, "x.svg"),
    # default square  →  None keeps original behaviour
    "square":   None,
    "default":  None,
}

# ----------------------------
# Outer eye shapes
# ----------------------------
OUTER_SHAPES = {
    "circle":   os.path.join(OUTER_DIR, "circle.svg"),
    "eye":      os.path.join(OUTER_DIR, "eye.svg"),
    "octagon":  os.path.join(OUTER_DIR, "octagon.svg"),
    "rounded":  os.path.join(OUTER_DIR, "rounded.svg"),
    "rounder":  os.path.join(OUTER_DIR, "rounder.svg"),
    "target":   os.path.join(OUTER_DIR, "target.svg"),
    "zig":      os.path.join(OUTER_DIR, "zig.svg"),
    "square":   None,
    "default":  None,
}

# ----------------------------
# Built-in icons
# ----------------------------
ICONS = {
    "youtube":   os.path.join(ICON_DIR, "yt.svg"),
    "yt":        os.path.join(ICON_DIR, "yt.svg"),
    "gold":      os.path.join(ICON_DIR, "gold.png"),
    # add more as you drop files into /icon
    None:        None,
    "none":      None,
}

# ----------------------------
# Body shape presets  (SVG snippet, viewBox 0 0 10 10)
# ----------------------------
BODY_PRESETS = {
    "square":        '<rect x="0" y="0" width="10" height="10"/>',
    "circle":        '<circle cx="5" cy="5" r="4.5"/>',
    "rounded":       '<rect x="0.5" y="0.5" rx="1.5" ry="1.5" width="9" height="9"/>',
    "block":         '<rect x="0.5" y="0.5" width="9" height="9"/>',
    "diamond":       '<path d="M5 0 L10 5 L5 10 L0 5 Z"/>',
    "dot":           '<circle cx="5" cy="5" r="3"/>',
    "constellation": (
        '<path d="'
        'M5.000,0.500 '
        'C5.342,4.060 5.940,4.658 9.500,5.000 '
        'C5.940,5.342 5.342,5.940 5.000,9.500 '
        'C4.658,5.940 4.060,5.342 0.500,5.000 '
        'C4.060,4.658 4.658,4.060 5.000,0.500 '
        'Z"/>'
    ),
    "":     None,   # empty string → default square rect
    None:   None,
}

# ----------------------------
# Resolve helpers  (used by qr_generator)
# ----------------------------

def resolve_color(value):
    """'red' → '#e63946'  |  '#ff0000' → '#ff0000'  |  None → None"""
    if value is None:
        return None
    if str(value).startswith("#"):
        return value
    return COLORS.get(str(value).lower(), value)


def resolve_inner(value):
    """'cloud' → 'inner/cloud.svg'  |  full path kept as-is  |  None → None"""
    if value is None or str(value).lower() in ("none", "default", "square", ""):
        return None
    if str(value) in INNER_SHAPES:
        return INNER_SHAPES[str(value)]
    if os.path.exists(str(value)):          # already a valid path
        return value
    return None


def resolve_outer(value):
    """'zig' → 'outer/zig.svg'  |  full path kept as-is  |  None → None"""
    if value is None or str(value).lower() in ("none", "default", "square", ""):
        return None
    if str(value) in OUTER_SHAPES:
        return OUTER_SHAPES[str(value)]
    if os.path.exists(str(value)):
        return value
    return None


def resolve_icon(value):
    """'youtube' → 'icon/yt.svg'  |  custom path kept as-is  |  None → None"""
    if value is None or str(value).lower() == "none":
        return None
    if str(value) in ICONS:
        return ICONS[str(value)]
    if os.path.exists(str(value)):
        return value
    return None


def resolve_gradient(value):
    """'radial' → 'radial'  |  'horizontal' → 'left_to_right'"""
    if value is None:
        return "left_to_right"
    return GRADIENTS.get(str(value).lower(), str(value))


def resolve_body_shape(value):
    """'circle' → svg snippet  |  path to .svg → kept  |  '' → None"""
    if value is None or value == "":
        return None             # caller will use plain rect
    if value in BODY_PRESETS:
        return value            # generator handles preset lookup
    if os.path.exists(str(value)):
        return value            # custom SVG file path
    return None