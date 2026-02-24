# ============================================================
#  main.py  –  Run examples to test every feature
#
#  Just run:  python main.py
#
#  Outputs land in:  output/
# ============================================================

from code import generate_custom_qr


# ─────────────────────────────────────────────────────────────────────────────
#  1. Simplest possible  –  plain black QR
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data        = "https://example.com",
    output_path = "output/01_plain.png",
)


# ─────────────────────────────────────────────────────────────────────────────
#  2. Colour only  –  solid green, no gradient
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data        = "https://example.com",
    output_path = "output/02_solid_green.png",
    body_color  = "green",              # friendly name
    innereye_color = "green",
    outereye_color = "green",
)


# ─────────────────────────────────────────────────────────────────────────────
#  3. Radial gradient  (center colour → outer colour)
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data                 = "https://example.com",
    output_path          = "output/03_radial_gradient.png",
    body_color           = "teal",
    body_gradient_color  = "deep_blue",   # friendly name for gradient end
    body_gradient_type   = "radial",
    innereye_color       = "teal",
    outereye_color       = "deep_blue",
)


# ─────────────────────────────────────────────────────────────────────────────
#  4. Horizontal gradient
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data                 = "https://example.com",
    output_path          = "output/04_horizontal_gradient.png",
    body_color           = "purple",
    body_gradient_color  = "pink",
    body_gradient_type   = "horizontal",  # alias for left_right
    innereye_color       = "purple",
    outereye_color       = "pink",
)


# ─────────────────────────────────────────────────────────────────────────────
#  5. Diagonal gradient  –  hex colours
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data                 = "https://example.com",
    output_path          = "output/05_diagonal_hex.png",
    body_color           = "#ff6b6b",
    body_gradient_color  = "#feca57",
    body_gradient_type   = "diagonal",
    innereye_color       = "#ff6b6b",
    outereye_color       = "#feca57",
)


# ─────────────────────────────────────────────────────────────────────────────
#  6. Custom eye shapes  –  cloud inner + zig outer
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data           = "https://example.com",
    output_path    = "output/06_cloud_zig.png",
    body_color     = "navy",
    innereye_color = "teal",
    outereye_color = "navy",
    innereye_shape = "cloud",             # short name  →  inner/cloud.svg
    outereye_shape = "zig",               # short name  →  outer/zig.svg
)


# ─────────────────────────────────────────────────────────────────────────────
#  7. Heart inner + eye outer
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data           = "https://example.com",
    output_path    = "output/07_heart_eye.png",
    body_color     = "coral",
    innereye_color = "red",
    outereye_color = "coral",
    innereye_shape = "heart",
    outereye_shape = "eye",
)


# ─────────────────────────────────────────────────────────────────────────────
#  8. Flower inner + rounded outer  +  gradient
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data                 = "https://example.com",
    output_path          = "output/08_flower_rounded_gradient.png",
    body_color           = "gold",
    body_gradient_color  = "brown",
    body_gradient_type   = "vertical",
    innereye_color       = "gold",
    outereye_color       = "brown",
    innereye_shape       = "flower",
    outereye_shape       = "rounded",
)


# ─────────────────────────────────────────────────────────────────────────────
#  9. Custom body shape  –  dots
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data           = "https://example.com",
    output_path    = "output/09_dot_body.png",
    body_shape     = "dot",               # preset name
    body_color     = "indigo",
    innereye_color = "indigo",
    outereye_color = "indigo",
)


# ─────────────────────────────────────────────────────────────────────────────
#  10. Diamond body  +  octagon outer
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data           = "https://example.com",
    output_path    = "output/10_diamond_octagon.png",
    body_shape     = "diamond",
    body_color     = "cyan",
    innereye_color = "cyan",
    outereye_color = "cyan",
    outereye_shape = "octagon",
)


# ─────────────────────────────────────────────────────────────────────────────
#  11. YouTube icon  –  short name
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data           = "https://youtube.com",
    output_path    = "output/11_youtube_icon.png",
    body_color     = "red",
    innereye_color = "red",
    outereye_color = "red",
    icon_path      = "youtube",           # short name  →  icon/yt.svg
)


# ─────────────────────────────────────────────────────────────────────────────
#  12. Gold icon  –  short name
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data           = "https://example.com",
    output_path    = "output/12_gold_icon.png",
    body_color     = "gold",
    body_gradient_color = "brown",
    body_gradient_type  = "radial",
    innereye_color = "gold",
    outereye_color = "brown",
    icon_path      = "gold",              # short name  →  icon/gold.png
)


# ─────────────────────────────────────────────────────────────────────────────
#  13. Everything at once  –  gradient + custom eyes + icon + SVG output
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data                 = "https://example.com",
    output_path          = "output/13_full_combo.png",   # SVG output
    body_shape           = "rounded",
    body_color           = "teal",
    body_gradient_color  = "indigo",
    body_gradient_type   = "diagonal",
    innereye_color       = "teal",
    outereye_color       = "indigo",
    innereye_shape       = "sphere",
    outereye_shape       = "circle",
    icon_path            = "youtube",
    size                 = 14,
    border               = 4,
)


# ─────────────────────────────────────────────────────────────────────────────
#  14. Custom icon from file path  –  works with any image
# ─────────────────────────────────────────────────────────────────────────────
generate_custom_qr(
    data        = "https://example.com",
    output_path = "output/14_custom_icon_path.png",
    body_color  = "black",
    icon_path   = "icon/gold.png",        # direct path still works fine
)