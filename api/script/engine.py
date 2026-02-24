# ============================================================
#  script/code.py  –  Core QR generation engine (Vercel-safe)
#  cairosvg replaced with svglib + reportlab (pure Python)
# ============================================================

import os
import re
import base64
import mimetypes
import math
import tempfile
from io import BytesIO

import segno
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from script.assets import (
    BODY_PRESETS,
    resolve_color, resolve_inner, resolve_outer,
    resolve_icon, resolve_gradient, resolve_body_shape,
)

GRADIENT_TYPES_MAP = {
    "left_to_right":  ("0%",   "0%",   "100%", "0%"),
    "right_to_left":  ("100%", "0%",   "0%",   "0%"),
    "top_to_bottom":  ("0%",   "0%",   "0%",   "100%"),
    "bottom_to_top":  ("0%",   "100%", "0%",   "0%"),
    "diagonal_tl_br": ("0%",   "0%",   "100%", "100%"),
    "diagonal_tr_bl": ("100%", "0%",   "0%",   "100%"),
    "radial":          None,
}


# ────────────────────────────────────────────────────────────
#  Colour helpers
# ────────────────────────────────────────────────────────────

def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def _lerp(c1, c2, t):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex(
        r1 + (r2 - r1) * t,
        g1 + (g2 - g1) * t,
        b1 + (b2 - b1) * t,
    )

def _module_colour(col, row, matrix_size, border, size,
                   body_color, body_gradient_color, body_gradient_type):
    if not body_gradient_color:
        return body_color
    total = (matrix_size + border * 2) * size
    cx = (col + border + 0.5) * size
    cy = (row + border + 0.5) * size
    gt = body_gradient_type
    if   gt == "left_to_right":   t = cx / total
    elif gt == "right_to_left":   t = 1 - cx / total
    elif gt == "top_to_bottom":   t = cy / total
    elif gt == "bottom_to_top":   t = 1 - cy / total
    elif gt == "diagonal_tl_br":  t = (cx + cy) / (total * 2)
    elif gt == "diagonal_tr_bl":  t = (total - cx + cy) / (total * 2)
    elif gt == "radial":
        dx = cx - total / 2
        dy = cy - total / 2
        t  = min(math.hypot(dx, dy) / (total / 2), 1.0)
    else:
        t = 0
    return _lerp(body_color, body_gradient_color, t)


# ────────────────────────────────────────────────────────────
#  SVG helpers  (no cairosvg)
# ────────────────────────────────────────────────────────────

def _svg_to_png_bytes(svg_string: str) -> bytes:
    """Convert an SVG string to PNG bytes using svglib + reportlab."""
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False,
                                     mode="w", encoding="utf-8") as f:
        f.write(svg_string)
        tmp_path = f.name
    try:
        drawing = svg2rlg(tmp_path)
        buf = BytesIO()
        renderPM.drawToFile(drawing, buf, fmt="PNG")
        buf.seek(0)
        return buf.read()
    finally:
        os.unlink(tmp_path)


def _load_svg(path, strip_fill=True):
    if not path or not os.path.exists(path) or not path.lower().endswith(".svg"):
        return None
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'width="[^"]+"', "", content)
    content = re.sub(r'height="[^"]+"', "", content)
    content = re.sub(r'fill="[^"]+"', "" if strip_fill else 'fill="currentColor"', content)
    start = content.find(">") + 1
    end   = content.rfind("</svg>")
    return content[start:end].strip()

def _svg_size(path):
    if not path or not os.path.exists(path) or not path.lower().endswith(".svg"):
        return 100, 100
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'viewBox="([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)"', content)
    if m:
        _, _, w, h = map(float, m.groups())
        return w, h
    wm = re.search(r'width="(\d+)"', content)
    hm = re.search(r'height="(\d+)"', content)
    if wm and hm:
        return float(wm.group(1)), float(hm.group(1))
    return 100, 100

def _icon_base64(path, target_width):
    """Return a base64 data-URI for the icon. SVG icons are rasterised via svglib."""
    if not path or not os.path.exists(path):
        return None

    if path.lower().endswith(".svg"):
        # Build a tiny wrapper SVG sized to target_width so svglib scales it correctly
        inner = _load_svg(path, strip_fill=False)
        iw, ih = _svg_size(path)
        wrapper = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{target_width * 2}" height="{target_width * 2}" '
            f'viewBox="0 0 {iw} {ih}">{inner}</svg>'
        )
        png_bytes = _svg_to_png_bytes(wrapper)
        return "data:image/png;base64," + base64.b64encode(png_bytes).decode()

    mime, _ = mimetypes.guess_type(path)
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


# ────────────────────────────────────────────────────────────
#  Public API
# ────────────────────────────────────────────────────────────

def generate_custom_qr(
    data,
    output_path             = "output/qr.png",
    body_shape              = None,
    body_color              = "black",
    body_gradient_color     = None,
    body_gradient_type      = "radial",
    innereye_color          = None,
    innereye_shape          = None,
    outereye_color          = None,
    outereye_shape          = None,
    icon_path               = None,
    icon_scale              = 0.20,
    size                    = 10,
    border                  = 4,
):
    """
    Generate a custom QR code and save to output_path (.svg or .png).
    Works on Vercel / any serverless environment (no cairosvg).
    """

    # ── Resolve friendly values ──────────────────────────────
    body_color           = resolve_color(body_color)           or "#000000"
    body_gradient_color  = resolve_color(body_gradient_color)
    innereye_color       = resolve_color(innereye_color)       or body_color
    outereye_color       = resolve_color(outereye_color)       or body_color
    body_gradient_type   = resolve_gradient(body_gradient_type)
    innereye_shape_path  = resolve_inner(innereye_shape)
    outereye_shape_path  = resolve_outer(outereye_shape)
    icon_file            = resolve_icon(icon_path)
    body_shape_key       = resolve_body_shape(body_shape)

    # ── Matrix ───────────────────────────────────────────────
    qr          = segno.make(data, error="h")
    matrix      = qr.matrix
    matrix_size = len(matrix)
    total_px    = int((matrix_size + border * 2) * size)

    # ── Icon region ──────────────────────────────────────────
    if icon_file and os.path.exists(icon_file):
        icon_modules = math.ceil(matrix_size * icon_scale)
        if (matrix_size - icon_modules) % 2 != 0:
            icon_modules += 1
        m_start = (matrix_size - icon_modules) // 2
        m_end   = m_start + icon_modules
    else:
        m_start = m_end = -1

    # ── Helpers ──────────────────────────────────────────────
    def is_finder(col, row):
        for fx, fy in [(0, 0), (matrix_size - 7, 0), (0, matrix_size - 7)]:
            if fx <= col < fx + 7 and fy <= row < fy + 7:
                return True
        return False

    # ── Body shape ───────────────────────────────────────────
    if body_shape_key in BODY_PRESETS:
        body_svg = BODY_PRESETS[body_shape_key]
        body_w = body_h = 10
    elif body_shape_key and os.path.exists(body_shape_key):
        body_svg = _load_svg(body_shape_key, strip_fill=True)
        body_w, body_h = _svg_size(body_shape_key)
    else:
        body_svg = None
        body_w = body_h = 10

    outer_svg        = _load_svg(outereye_shape_path, strip_fill=False)
    outer_w, outer_h = _svg_size(outereye_shape_path)
    inner_svg        = _load_svg(innereye_shape_path, strip_fill=False)
    inner_w, inner_h = _svg_size(innereye_shape_path)

    # ── Build SVG ────────────────────────────────────────────
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{total_px}" height="{total_px}" viewBox="0 0 {total_px} {total_px}">',
        f'<rect width="{total_px}" height="{total_px}" fill="white"/>',
    ]

    # Body modules
    for row in range(matrix_size):
        for col in range(matrix_size):
            if not matrix[row][col]:
                continue
            if is_finder(col, row):
                continue
            if m_start <= col < m_end and m_start <= row < m_end:
                continue

            px    = (col + border) * size
            py    = (row + border) * size
            color = _module_colour(
                col, row, matrix_size, border, size,
                body_color, body_gradient_color, body_gradient_type,
            )

            if body_svg:
                sx, sy = size / body_w, size / body_h
                lines.append(
                    f'<g transform="translate({px},{py}) scale({sx},{sy})" fill="{color}">'
                    f"{body_svg}</g>"
                )
            else:
                lines.append(
                    f'<rect x="{px}" y="{py}" width="{size}" height="{size}" fill="{color}"/>'
                )

    # Finder eyes
    EYE_PX = 7 * size
    for fx, fy, angle in [(0, 0, 0), (matrix_size - 7, 0, 90), (0, matrix_size - 7, -90)]:
        px = (fx + border) * size
        py = (fy + border) * size
        cx = px + EYE_PX / 2
        cy = py + EYE_PX / 2

        if outer_svg:
            tf = (
                f"translate({cx},{cy}) rotate({angle}) "
                f"translate({-EYE_PX/2},{-EYE_PX/2}) "
                f"scale({EYE_PX/outer_w},{EYE_PX/outer_h})"
            )
            lines.append(
                f'<g transform="{tf}" style="color:{outereye_color};" fill="currentColor">'
                f"{outer_svg}</g>"
            )
        else:
            lines.append(
                f'<path d="M{px},{py} h{EYE_PX} v{EYE_PX} h-{EYE_PX} z '
                f'M{px+size},{py+size} v{5*size} h{5*size} v-{5*size} z" '
                f'fill="{outereye_color}"/>'
            )

        ix, iy   = px + 2 * size, py + 2 * size
        inner_px = 3 * size
        if inner_svg:
            tf_i = f"translate({ix},{iy}) scale({inner_px/inner_w},{inner_px/inner_h})"
            lines.append(
                f'<g transform="{tf_i}" style="color:{innereye_color};" fill="currentColor">'
                f"{inner_svg}</g>"
            )
        else:
            lines.append(
                f'<rect x="{ix}" y="{iy}" width="{inner_px}" height="{inner_px}" '
                f'fill="{innereye_color}"/>'
            )

    # Icon
    if icon_file and os.path.exists(icon_file) and m_start >= 0:
        dim = (m_end - m_start) * size
        pos = (m_start + border) * size
        img = _icon_base64(icon_file, dim)
        if img:
            lines.append(
                f'<rect x="{pos}" y="{pos}" width="{dim}" height="{dim}" fill="white"/>'
            )
            lines.append(
                f'<image xlink:href="{img}" x="{pos}" y="{pos}" width="{dim}" height="{dim}"/>'
            )

    lines.append("</svg>")
    full_svg = "\n".join(lines)

    # ── Save ─────────────────────────────────────────────────
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".svg":
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_svg)
        print(f"✅  SVG → {output_path}")
    else:
        png_bytes = _svg_to_png_bytes(full_svg)
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        print(f"✅  PNG → {output_path}")

    return full_svg