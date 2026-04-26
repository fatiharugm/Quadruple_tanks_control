"""
Generate a more realistic schematic diagram for the quadruple-tank process.

This version is intentionally simple and fast: it uses Pillow only (no matplotlib),
so it runs reliably in minimal Python environments.

Run:
  python examples/generate_system_diagram_realistic.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from typing import cast


@dataclass(frozen=True)
class Theme:
    t1: str = "#FF6B6B"  # red
    t2: str = "#4ECDC4"  # teal
    t3: str = "#45B7D1"  # blue
    t4: str = "#FFA07A"  # orange
    water: str = "#4A90E2"
    pipe: str = "#2F2F2F"
    pipe_light: str = "#7A7A7A"
    bg: str = "#FFFFFF"
    panel: str = "#F6F6F6"


def _font(size: int) -> ImageFont.ImageFont:
    # Prefer a common system font if available; otherwise fall back.
    for name in ("DejaVuSans.ttf", "Arial.ttf"):
        try:
            return cast(ImageFont.ImageFont, ImageFont.truetype(name, size=size))
        except Exception:
            pass
    return cast(ImageFont.ImageFont, ImageFont.load_default())


def _rounded_rect(draw: ImageDraw.ImageDraw, box, r, outline, width=3, fill=None):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=outline, width=width, fill=fill)


def _line(draw: ImageDraw.ImageDraw, pts, color, width=6):
    draw.line(pts, fill=color, width=width, joint="curve")


def _arrow(draw: ImageDraw.ImageDraw, p0, p1, color, width=6, head=14):
    _line(draw, [p0, p1], color, width=width)
    # Arrow head
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    n = (dx * dx + dy * dy) ** 0.5 or 1.0
    ux, uy = dx / n, dy / n
    # Perp
    px, py = -uy, ux
    tip = (x1, y1)
    left = (x1 - int(ux * head) + int(px * head * 0.6), y1 - int(uy * head) + int(py * head * 0.6))
    right = (x1 - int(ux * head) - int(px * head * 0.6), y1 - int(uy * head) - int(py * head * 0.6))
    draw.polygon([tip, left, right], fill=color)


def _circle(draw: ImageDraw.ImageDraw, c, r, outline, width=3, fill=None):
    x, y = c
    draw.ellipse([x - r, y - r, x + r, y + r], outline=outline, width=width, fill=fill)


def _valve(draw: ImageDraw.ImageDraw, c, size, color):
    x, y = c
    s = size
    draw.polygon([(x - s, y - int(0.8 * s)), (x, y), (x - s, y + int(0.8 * s))], outline=color, fill="white")
    draw.polygon([(x + s, y - int(0.8 * s)), (x, y), (x + s, y + int(0.8 * s))], outline=color, fill="white")
    draw.line([(x - s, y - int(0.8 * s)), (x - s, y + int(0.8 * s))], fill=color, width=2)
    draw.line([(x + s, y - int(0.8 * s)), (x + s, y + int(0.8 * s))], fill=color, width=2)


def _valve_labeled(draw: ImageDraw.ImageDraw, c, size, color, label, font):
    _valve(draw, c, size=size, color=color)
    tw = draw.textlength(label, font=font)
    x = c[0] - tw / 2
    y = c[1] - size - 30
    # white backing box for readability on top of pipes
    pad_x, pad_y = 8, 5
    draw.rounded_rectangle(
        [x - pad_x, y - pad_y, x + tw + pad_x, y + font.size + pad_y],
        radius=6,
        fill="white",
        outline=None,
    )
    draw.text((x, y), label, font=font, fill=color)


def _orifice(draw: ImageDraw.ImageDraw, c, r, color):
    _circle(draw, c, r, outline=color, width=3, fill="white")
    _circle(draw, c, max(2, r // 3), outline=color, width=1, fill=color)


def _tank(draw: ImageDraw.ImageDraw, box, label, accent, water_frac, theme: Theme, font_big, font_small):
    x0, y0, x1, y1 = box
    _rounded_rect(draw, box, r=18, outline=accent, width=6, fill="white")

    # Water fill
    h = y1 - y0
    fill_h = int(max(0.0, min(1.0, water_frac)) * h)
    if fill_h > 0:
        water_box = [x0 + 8, y1 - fill_h + 6, x1 - 8, y1 - 8]
        draw.rectangle(water_box, fill=theme.water)

    # Level sensor icon on left
    sy = y0 + int(h * 0.35)
    _circle(draw, (x0 - 22, sy), 10, outline=theme.pipe, width=3, fill="white")
    _line(draw, [(x0 - 12, sy), (x0, sy)], theme.pipe, width=4)

    # Label above (with white backing for clarity)
    tw = draw.textlength(label, font=font_big)
    lx = x0 + (x1 - x0 - tw) / 2
    ly = y0 - 58
    draw.rounded_rectangle(
        [lx - 10, ly - 6, lx + tw + 10, ly + font_big.size + 6],
        radius=10,
        fill="white",
        outline=None,
    )
    draw.text((lx, ly), label, font=font_big, fill=accent)


def _pump(draw: ImageDraw.ImageDraw, c, label, accent, theme: Theme, font_small):
    x, y = c
    _circle(draw, (x, y), 30, outline=theme.pipe, width=5, fill="white")
    _circle(draw, (x, y), 7, outline=theme.pipe, width=1, fill=theme.pipe)
    _line(draw, [(x - 14, y), (x + 14, y)], theme.pipe, width=4)
    _line(draw, [(x, y - 14), (x, y + 14)], theme.pipe, width=4)
    tw = draw.textlength(label, font=font_small)
    draw.text((x - tw / 2, y + 42), label, font=font_small, fill=accent)


def main():
    theme = Theme()
    out_path = Path(__file__).resolve().parents[1] / "system_diagram_realistic.png"

    W, H = 1200, 1600
    img = Image.new("RGB", (W, H), theme.bg)
    draw = ImageDraw.Draw(img)

    font_title = _font(44)
    font_big = _font(42)
    font_med = _font(28)
    font_small = _font(24)

    title = "Quadruple-Tank (Coupled Tanks) Process"
    tw = draw.textlength(title, font=font_title)
    draw.text(((W - tw) / 2, 40), title, font=font_title, fill="#111111")

    # Layout (pixel coordinates)
    tank_w, tank_h = 220, 340
    t1 = (240, 220, 240 + tank_w, 220 + tank_h)
    t2 = (740, 220, 740 + tank_w, 220 + tank_h)
    t3 = (240, 820, 240 + tank_w, 820 + tank_h)
    t4 = (740, 820, 740 + tank_w, 820 + tank_h)

    _tank(draw, t1, "T1", theme.t1, 0.45, theme, font_big, font_small)
    _tank(draw, t2, "T2", theme.t2, 0.45, theme, font_big, font_small)
    _tank(draw, t3, "T3", theme.t3, 0.35, theme, font_big, font_small)
    _tank(draw, t4, "T4", theme.t4, 0.35, theme, font_big, font_small)

    # h-labels
    def _hlabel(tbox, txt, color):
        x0, y0, x1, y1 = tbox
        # Put a small white backing box so pipes never obscure the label
        x = x1 + 18
        y = y0 + 120
        tw = draw.textlength(txt, font=font_med)
        draw.rounded_rectangle(
            [x - 8, y - 6, x + tw + 8, y + font_med.size + 6],
            radius=10,
            fill="white",
            outline=None,
        )
        draw.text((x, y), txt, font=font_med, fill=color)

    _hlabel(t1, "h1", theme.t1)
    _hlabel(t2, "h2", theme.t2)
    _hlabel(t3, "h3", theme.t3)
    _hlabel(t4, "h4", theme.t4)

    # Pumps
    p1 = (t1[0] + tank_w // 2, 140)
    p2 = (t2[0] + tank_w // 2, 140)
    _pump(draw, p1, "Pump 1", theme.t1, theme, font_small)
    _pump(draw, p2, "Pump 2", theme.t2, theme, font_small)

    # Pump lines + valves + u1/u2
    def _pump_to_tank(p, tbox, ulabel, ucolor):
        tx = (tbox[0] + tbox[2]) // 2
        top_y = tbox[1]
        mid = (tx, 190)
        _line(draw, [p, mid], theme.pipe, width=10)
        vpos = (tx, 215)
        _valve(draw, vpos, size=18, color=theme.pipe)
        _arrow(draw, (tx, 235), (tx, top_y + 18), theme.pipe, width=10, head=18)
        tw2 = draw.textlength(ulabel, font=font_med)
        draw.text((tx - tw2 / 2, 178), ulabel, font=font_med, fill=ucolor)

    _pump_to_tank(p1, t1, "u1", theme.t1)
    _pump_to_tank(p2, t2, "u2", theme.t2)

    # Orifices at upper tank bottoms
    def _bottom_center(tbox):
        return ((tbox[0] + tbox[2]) // 2, tbox[3])

    t1_out = _bottom_center(t1)
    t2_out = _bottom_center(t2)
    _orifice(draw, t1_out, r=12, color=theme.pipe)
    _orifice(draw, t2_out, r=12, color=theme.pipe)

    # Junctions and coupling pipes
    j1 = (t1_out[0], t1_out[1] + 90)
    j2 = (t2_out[0], t2_out[1] + 90)
    _arrow(draw, (t1_out[0], t1_out[1] + 18), j1, theme.pipe, width=10, head=18)
    _arrow(draw, (t2_out[0], t2_out[1] + 18), j2, theme.pipe, width=10, head=18)

    # Inlets at lower tank tops
    def _top_center(tbox):
        return ((tbox[0] + tbox[2]) // 2, tbox[1])

    t3_in = _top_center(t3)
    t4_in = _top_center(t4)

    # Main paths (thick)
    _arrow(draw, j1, (t3_in[0], j1[1] + 170), theme.pipe, width=10, head=18)
    _arrow(draw, (t3_in[0], j1[1] + 170), (t3_in[0], t3_in[1] + 18), theme.pipe, width=10, head=18)
    _arrow(draw, j2, (t4_in[0], j2[1] + 170), theme.pipe, width=10, head=18)
    _arrow(draw, (t4_in[0], j2[1] + 170), (t4_in[0], t4_in[1] + 18), theme.pipe, width=10, head=18)

    # Cross-coupling (thin/lighter)
    _arrow(draw, j1, (t4_in[0], j1[1] + 220), theme.pipe_light, width=7, head=16)
    _arrow(draw, (t4_in[0], j1[1] + 220), (t4_in[0], t4_in[1] + 18), theme.pipe_light, width=7, head=16)
    _arrow(draw, j2, (t3_in[0], j2[1] + 220), theme.pipe_light, width=7, head=16)
    _arrow(draw, (t3_in[0], j2[1] + 220), (t3_in[0], t3_in[1] + 18), theme.pipe_light, width=7, head=16)

    draw.text((j1[0] + 16, j1[1] + 16), "γ", font=font_med, fill=theme.pipe)
    draw.text((j2[0] + 16, j2[1] + 16), "γ", font=font_med, fill=theme.pipe)

    # Add explicit control valves on the four interconnection pipes for clarity.
    # Place them slightly away from crossings and tank labels.
    # u13: T1 -> T3 (main, thick)
    _valve_labeled(draw, (t3_in[0] - 34, j1[1] + 150), size=16, color=theme.pipe, label="u13", font=font_small)
    # u14: T1 -> T4 (cross, light)
    _valve_labeled(draw, (t4_in[0] + 34, j1[1] + 212), size=14, color=theme.pipe_light, label="u14", font=font_small)
    # u24: T2 -> T4 (main, thick)
    _valve_labeled(draw, (t4_in[0] + 34, j2[1] + 150), size=16, color=theme.pipe, label="u24", font=font_small)
    # u23: T2 -> T3 (cross, light)
    _valve_labeled(draw, (t3_in[0] - 34, j2[1] + 212), size=14, color=theme.pipe_light, label="u23", font=font_small)

    # Lower tank drains to reservoir
    t3_out = _bottom_center(t3)
    t4_out = _bottom_center(t4)
    _orifice(draw, t3_out, r=12, color=theme.pipe)
    _orifice(draw, t4_out, r=12, color=theme.pipe)

    res_box = (360, 1420, 840, 1525)
    _rounded_rect(draw, res_box, r=18, outline=theme.pipe, width=4, fill=theme.panel)
    res_label = "Drain / Reservoir"
    tw3 = draw.textlength(res_label, font=font_med)
    draw.text(((res_box[0] + res_box[2] - tw3) / 2, res_box[1] + 32), res_label, font=font_med, fill="#222222")

    # Drain pipes into reservoir
    _arrow(draw, (t3_out[0], t3_out[1] + 18), (t3_out[0], 1320), theme.pipe, width=10, head=18)
    _arrow(draw, (t4_out[0], t4_out[1] + 18), (t4_out[0], 1320), theme.pipe, width=10, head=18)
    _arrow(draw, (t3_out[0], 1320), (res_box[0] + 120, 1420), theme.pipe, width=10, head=18)
    _arrow(draw, (t4_out[0], 1320), (res_box[2] - 120, 1420), theme.pipe, width=10, head=18)

    # Footnote legend
    legend = "Valves u13/u14/u23/u24 actuate pipes   •   Thick: main coupling   •   Light: cross-coupling"
    tw4 = draw.textlength(legend, font=font_small)
    draw.text(((W - tw4) / 2, 1560), legend, font=font_small, fill="#444444")

    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()

