# ============================================================
#  script/code.py  –  Core QR generation engine (Vercel-safe)
#  PNG rendered directly with Pillow — zero system dependencies
# ============================================================

import os
import re
import base64
import mimetypes
import math
from io import BytesIO

import segno
from PIL import Image, ImageDraw

from script.assets import (
    BODY_PRESETS,
    resolve_color, resolve_inner, resolve_outer,
    resolve_icon, resolve_gradient, resolve_body_shape,
)


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
#  SVG helpers  (SVG output only)
# ────────────────────────────────────────────────────────────

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

def _icon_base64_for_svg(path, target_width):
    """For SVG output only — embeds icon as base64."""
    if not path or not os.path.exists(path):
        return None
    if path.lower().endswith(".svg"):
        # For SVG output, just embed the SVG as-is via base64
        with open(path, "rb") as f:
            return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()
    mime, _ = mimetypes.guess_type(path)
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


# ────────────────────────────────────────────────────────────
#  Direct Pillow PNG renderer  (no cairo, no svglib)
# ────────────────────────────────────────────────────────────

def _draw_png(
    matrix, matrix_size, total_px, size, border,
    body_color, body_gradient_color, body_gradient_type,
    innereye_color, outereye_color,
    icon_file, m_start, m_end,
):
    img  = Image.new("RGB", (total_px, total_px), "white")
    draw = ImageDraw.Draw(img)

    def is_finder(col, row):
        for fx, fy in [(0, 0), (matrix_size - 7, 0), (0, matrix_size - 7)]:
            if fx <= col < fx + 7 and fy <= row < fy + 7:
                return True
        return False

    # Body modules
    for row in range(matrix_size):
        for col in range(matrix_size):
            if not matrix[row][col]:
                continue
            if is_finder(col, row):
                continue
            if m_start <= col < m_end and m_start <= row < m_end:
                continue
            color = _module_colour(
                col, row, matrix_size, border, size,
                body_color, body_gradient_color, body_gradient_type,
            )
            px = (col + border) * size
            py = (row + border) * size
            draw.rectangle([px, py, px + size - 1, py + size - 1], fill=color)

    # Finder eyes
    EYE = 7 * size
    for fx, fy in [(0, 0), (matrix_size - 7, 0), (0, matrix_size - 7)]:
        px = (fx + border) * size
        py = (fy + border) * size
        # Outer ring
        draw.rectangle([px, py, px + EYE - 1, py + EYE - 1], fill=outereye_color)
        draw.rectangle([px + size, py + size,
                         px + EYE - size - 1, py + EYE - size - 1], fill="white")
        # Inner square
        ix = px + 2 * size
        iy = py + 2 * size
        inner = 3 * size
        draw.rectangle([ix, iy, ix + inner - 1, iy + inner - 1], fill=innereye_color)

    # Icon
    if icon_file and os.path.exists(icon_file) and m_start >= 0:
        dim = (m_end - m_start) * size
        pos = (m_start + border) * size
        try:
            icon_img = Image.open(icon_file).convert("RGBA")
            icon_img = icon_img.resize((dim, dim), Image.LANCZOS)
            # White background behind icon
            bg = Image.new("RGB", (dim, dim), "white")
            bg.paste(icon_img, mask=icon_img.split()[3] if icon_img.mode == "RGBA" else None)
            img.paste(bg, (pos, pos))
        except Exception as e:
            print(f"Icon paste failed: {e}")

    return img


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

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    ext = os.path.splitext(output_path)[1].lower()

    # ── PNG: draw directly with Pillow ───────────────────────
    if ext != ".svg":
        img = _draw_png(
            matrix, matrix_size, total_px, size, border,
            body_color, body_gradient_color, body_gradient_type,
            innereye_color, outereye_color,
            icon_file, m_start, m_end,
        )
        img.save(output_path, "PNG")
        print(f"✅  PNG → {output_path}")
        return img  # return PIL Image for in-memory use

    # ── SVG: build markup ────────────────────────────────────
    def is_finder(col, row):
        for fx, fy in [(0, 0), (matrix_size - 7, 0), (0, matrix_size - 7)]:
            if fx <= col < fx + 7 and fy <= row < fy + 7:
                return True
        return False

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

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{total_px}" height="{total_px}" viewBox="0 0 {total_px} {total_px}">',
        f'<rect width="{total_px}" height="{total_px}" fill="white"/>',
    ]

    for row in range(matrix_size):
        for col in range(matrix_size):
            if not matrix[row][col]: continue
            if is_finder(col, row):  continue
            if m_start <= col < m_end and m_start <= row < m_end: continue
            px    = (col + border) * size
            py    = (row + border) * size
            color = _module_colour(col, row, matrix_size, border, size,
                                   body_color, body_gradient_color, body_gradient_type)
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

    EYE_PX = 7 * size
    for fx, fy, angle in [(0, 0, 0), (matrix_size-7, 0, 90), (0, matrix_size-7, -90)]:
        px = (fx + border) * size
        py = (fy + border) * size
        cx = px + EYE_PX / 2
        cy = py + EYE_PX / 2
        if outer_svg:
            tf = (f"translate({cx},{cy}) rotate({angle}) "
                  f"translate({-EYE_PX/2},{-EYE_PX/2}) "
                  f"scale({EYE_PX/outer_w},{EYE_PX/outer_h})")
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
        ix, iy   = px + 2*size, py + 2*size
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

    if icon_file and os.path.exists(icon_file) and m_start >= 0:
        dim = (m_end - m_start) * size
        pos = (m_start + border) * size
        img_data = _icon_base64_for_svg(icon_file, dim)
        if img_data:
            lines.append(f'<rect x="{pos}" y="{pos}" width="{dim}" height="{dim}" fill="white"/>')
            lines.append(f'<image xlink:href="{img_data}" x="{pos}" y="{pos}" width="{dim}" height="{dim}"/>')

    lines.append("</svg>")
    full_svg = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_svg)
    print(f"✅  SVG → {output_path}")
    return full_svg