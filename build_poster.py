#!/usr/bin/env python3
"""Render the VELMARA travel poster (1024x1024 PNG).

Pure Pillow, no network, deterministic. Draws at 2x and downsamples
with LANCZOS for clean edges. The one bundled font (Gloock, SIL OFL)
lives in fonts/ next to this file.

    python3 build_poster.py [output_path]

Default output is entry.png beside this file.
"""

import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SS = 2                      # supersample factor
W, H = 1024, 1024           # final size
SW, SH = W * SS, H * SS     # working size

# --- palette (restrained: 6 hues) ---
NAVY = (20, 38, 62)         # bottom band, deep shadow
SKY_TOP = (38, 38, 79)      # dusk indigo
SKY_MID = (124, 74, 114)    # mauve
SKY_LOW = (217, 106, 90)    # coral
SKY_HOR = (242, 166, 90)    # amber at the horizon
SUN = (251, 217, 139)       # sun disc
SEA_TOP = (27, 122, 138)    # teal
SEA_BOT = (12, 74, 94)      # deep teal
CLIFF = (30, 47, 71)        # basalt
CLIFF_LIT = (52, 71, 99)    # basalt rim light
CREAM = (247, 237, 216)     # houses, type
ROOF = (201, 111, 74)       # terracotta roofs
WINDOW = (255, 201, 120)    # lit windows
ROCK = (67, 53, 74)         # sea stack
ROCK_LIT = (96, 74, 92)     # sea stack rim
CORAL = (228, 87, 61)       # lighthouse band
GOLD = (232, 178, 92)       # rules, sun glints
WHITE = (251, 246, 234)

HORIZON = 592               # y of the sea line
BAND_TOP = 832              # y where the navy name band starts


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(draw, x0, y0, x1, y1, stops):
    """Vertical multi-stop gradient, drawn as 1px rows (supersampled)."""
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                lt = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                draw.line([(x0, y), (x1, y)], fill=lerp(c0, c1, lt))
                break


def glow(draw, cx, cy, r, color, steps=24):
    """Soft radial glow: concentric discs fading out."""
    layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    g = ImageDraw.Draw(layer)
    for i in range(steps, 0, -1):
        a = int(26 * (1 - i / steps) ** 2) + 4
        rr = r * i / steps
        g.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (a,))
    return layer


def house(draw, x, y, w, h, roof_h, lit=True):
    """One white cubic house with a terracotta roof and lit windows."""
    draw.rectangle([x, y, x + w, y + h], fill=CREAM)
    draw.polygon([(x - 3 * SS, y), (x + w // 2, y - roof_h),
                  (x + w + 3 * SS, y)], fill=ROOF)
    if lit:
        ww = max(6 * SS, w // 5)
        wh = max(8 * SS, h // 3)
        draw.rectangle([x + w // 4 - ww // 2, y + h // 4,
                        x + w // 4 + ww // 2, y + h // 4 + wh], fill=WINDOW)
        draw.rectangle([x + 3 * w // 4 - ww // 2, y + h // 4,
                        x + 3 * w // 4 + ww // 2, y + h // 4 + wh], fill=WINDOW)


def bird(draw, x, y, s):
    """A distant gull: two short arcs."""
    draw.arc([x - s, y - s // 2, x, y + s // 2], 200, 340,
             fill=(30, 30, 60), width=2 * SS)
    draw.arc([x, y - s // 2, x + s, y + s // 2], 200, 340,
             fill=(30, 30, 60), width=2 * SS)


def draw_tracked(draw, cx, y, text, font, fill, tracking):
    """Draw text centred on cx with letter spacing (tracking, in px)."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += wch + tracking
    return total


def render(path):
    img = Image.new("RGB", (SW, SH), NAVY)
    d = ImageDraw.Draw(img, "RGBA")
    s = SS  # shorthand

    # --- sky ---
    vgrad(d, 0, 0, SW, HORIZON * s,
          [(0.0, SKY_TOP), (0.45, SKY_MID), (0.78, SKY_LOW), (1.0, SKY_HOR)])

    # --- sun + glow (low, right of centre) ---
    sun_cx, sun_cy, sun_r = 668 * s, 548 * s, 66 * s
    img.paste(Image.alpha_composite(
        img.convert("RGBA"),
        glow(d, sun_cx, sun_cy, sun_r * 3, (245, 166, 91))), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r,
               sun_cx + sun_r, sun_cy + sun_r], fill=SUN)

    # --- thin cloud streaks, warm lit (two soft lobes each) ---
    cloud_layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud_layer)
    for (cx, cy, cw, col) in [
            (280, 214, 260, (233, 150, 128)),
            (770, 168, 170, (214, 128, 128)),
            (170, 336, 160, (226, 138, 122)),
            (830, 300, 190, (238, 164, 130))]:
        ch = 9 * s
        cd.ellipse([cx * s, cy * s, (cx + cw) * s, cy * s + ch],
                   fill=col + (150,))
        cd.ellipse([(cx + cw // 4) * s, (cy - 5) * s,
                    (cx + 3 * cw // 4) * s, (cy + 5) * s], fill=col + (150,))
    img = Image.alpha_composite(img.convert("RGBA"), cloud_layer)
    d = ImageDraw.Draw(img, "RGBA")

    # --- gulls ---
    for (bx, by, bs) in [(250, 250, 22), (360, 190, 16), (880, 260, 20),
                         (920, 300, 14), (540, 200, 15)]:
        bird(d, bx * s, by * s, bs * s)

    # --- sea ---
    vgrad(d, 0, HORIZON * s, SW, BAND_TOP * s,
          [(0.0, SEA_TOP), (1.0, SEA_BOT)])
    d.line([(0, HORIZON * s), (SW, HORIZON * s)], fill=(255, 220, 160),
           width=2 * s)

    # sun path: shimmering dashes under the sun, jittered, tapering
    rng = random.Random(42)
    for row in range(10):
        y = (HORIZON + 14 + row * 20 + rng.uniform(-4, 4)) * s
        half = (20 + row * 11) * s
        n = 4 + row // 2
        for i in range(n):
            cx = sun_cx + rng.uniform(-half, half)
            w = rng.uniform(12, 34) * s
            d.line([(cx - w / 2, y), (cx + w / 2, y)],
                   fill=(255, 214, 140, 140), width=3 * s)

    # gentle wave arcs
    for (wx, wy, ww) in [(180, 660, 90), (380, 720, 110), (820, 700, 100),
                         (120, 770, 80), (600, 780, 120), (900, 770, 70)]:
        d.arc([wx * s, wy * s, (wx + ww) * s, (wy + 18) * s], 180, 360,
              fill=(255, 255, 255, 60), width=2 * s)

    # --- cliff town, left ---
    cliff = [(0, BAND_TOP), (0, 470), (58, 452), (118, 468), (150, 496),
             (206, 516), (252, 556), (298, 592), (330, 648), (344, BAND_TOP)]
    d.polygon([(x * s, y * s) for x, y in cliff], fill=CLIFF)
    # rim light along the cliff's top edge
    d.line([(x * s, y * s) for x, y in cliff[1:-1]], fill=CLIFF_LIT,
           width=5 * s, joint="curve")
    # houses stacked on the cliff edge
    for (hx, hy, hw, hh, rh) in [
            (30, 402, 56, 52, 22), (96, 414, 48, 48, 18),
            (150, 452, 52, 50, 20), (206, 478, 46, 46, 16),
            (60, 452, 44, 40, 16), (120, 470, 40, 38, 14)]:
        house(d, hx * s, hy * s, hw * s, hh * s, rh * s)
    # small dome tower above the town
    d.rectangle([86 * s, 372 * s, 106 * s, 404 * s], fill=CREAM)
    d.pieslice([82 * s, 352 * s, 110 * s, 380 * s], 180, 360, fill=ROOF)
    d.rectangle([94 * s, 380 * s, 98 * s, 400 * s], fill=WINDOW)

    # --- sea stack + lighthouse, right ---
    stack = [(798, BAND_TOP), (804, 620), (814, 520), (828, 470),
             (872, 470), (884, 540), (892, 640), (898, BAND_TOP)]
    d.polygon([(x * s, y * s) for x, y in stack], fill=ROCK)
    # warm rim light on the sun-facing (left) flank
    d.polygon([(798 * s, BAND_TOP * s), (804 * s, 620 * s),
               (814 * s, 520 * s), (828 * s, 470 * s),
               (838 * s, 470 * s), (826 * s, 540 * s),
               (818 * s, 640 * s), (814 * s, BAND_TOP * s)], fill=ROCK_LIT)
    # lighthouse tower
    lx0, lx1 = 822 * s, 864 * s
    d.polygon([(lx0, 470 * s), (lx0 + 4 * s, 372 * s),
               (lx1 - 4 * s, 372 * s), (lx1, 470 * s)], fill=WHITE)
    d.rectangle([lx0 + 2 * s, 420 * s, lx1 - 2 * s, 438 * s], fill=CORAL)
    # lamp room + cap
    d.rectangle([(lx0 - 2 * s), 352 * s, (lx1 + 2 * s), 372 * s],
                fill=NAVY)
    d.rectangle([(lx0 + 6 * s), 356 * s, (lx1 - 6 * s), 368 * s],
                fill=WINDOW)
    d.polygon([((lx0 - 4 * s), 352 * s), ((lx0 + lx1) // 2, 336 * s),
               ((lx1 + 4 * s), 352 * s)], fill=CORAL)
    # beam sweeping up-left across the dusk: layered wedges so it
    # fades toward its far end instead of ending in a hard edge
    beam = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    lamp = ((lx0 + lx1) // 2, 360 * s)
    far_top, far_bot = (380 * s, 268 * s), (360 * s, 322 * s)
    for frac, alpha in ((1.0, 26), (0.66, 22), (0.33, 18)):
        ft = (lamp[0] + (far_top[0] - lamp[0]) * frac,
              lamp[1] + (far_top[1] - lamp[1]) * frac)
        fb = (lamp[0] + (far_bot[0] - lamp[0]) * frac,
              lamp[1] + (far_bot[1] - lamp[1]) * frac)
        bd.polygon([lamp, ft, fb], fill=(255, 222, 148, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), beam)
    d = ImageDraw.Draw(img, "RGBA")

    # --- sailboat ---
    bx, by = 470 * s, 706 * s
    d.polygon([(bx, by - 74 * s), (bx, by - 6 * s), (bx + 44 * s, by - 6 * s)],
              fill=WHITE)
    d.polygon([(bx - 6 * s, by - 6 * s), (bx - 6 * s, by - 56 * s),
               (bx - 40 * s, by - 6 * s)], fill=(235, 228, 210))
    d.line([(bx, by - 78 * s), (bx, by - 2 * s)], fill=NAVY, width=3 * s)
    d.polygon([(bx - 48 * s, by), (bx + 52 * s, by),
               (bx + 40 * s, by + 12 * s), (bx - 36 * s, by + 12 * s)],
              fill=NAVY)

    # --- name band ---
    d.rectangle([0, BAND_TOP * s, SW, SH], fill=NAVY)
    d.line([(0, BAND_TOP * s), (SW, BAND_TOP * s)], fill=GOLD, width=3 * s)

    font = ImageFont.truetype(os.path.join(HERE, "fonts",
                                           "Gloock-Regular.ttf"), 116 * s)
    # gold rules framing the name
    rule_y1, rule_y2 = 872 * s, 992 * s
    d.line([(96 * s, rule_y1), (928 * s, rule_y1)], fill=GOLD, width=2 * s)
    d.line([(96 * s, rule_y2), (928 * s, rule_y2)], fill=GOLD, width=2 * s)
    # small diamond ornaments centred on each rule
    for ry in (rule_y1, rule_y2):
        cx = 512 * s
        d.polygon([(cx, ry - 8 * s), (cx + 8 * s, ry),
                   (cx, ry + 8 * s), (cx - 8 * s, ry)], fill=GOLD)
    # the place name, tracked and centred on the rules' midpoint using
    # the glyphs' real bbox, so no letter touches a rule
    name = "VELMARA"
    bbox = font.getbbox(name)
    glyph_h = bbox[3] - bbox[1]
    mid = (rule_y1 + rule_y2) / 2
    name_y = int(mid - glyph_h / 2 - bbox[1])
    total_w = draw_tracked(d, 512 * s, name_y, name, font, CREAM, 14 * s)
    assert total_w <= 832 * s, "name overflows the band"

    # --- vignette ---
    vig = Image.new("L", (SW, SH), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-SW * 0.25, -SH * 0.25, SW * 1.25, SH * 1.25], fill=255)
    vig = vig.point(lambda p: int(255 - (255 - p) * 0.16))
    dark = Image.new("RGB", (SW, SH), (10, 14, 30))
    img = Image.composite(img.convert("RGB"), dark, vig)

    # --- downsample + seeded grain (kills gradient banding) ---
    out = img.resize((W, H), Image.LANCZOS)
    tile = Image.new("L", (256, 256))
    tpix = tile.load()
    grng = random.Random(7)
    for ty in range(256):
        for tx in range(256):
            tpix[tx, ty] = 128 + grng.randint(-5, 5)
    noise = Image.new("L", (W, H))
    for oy in range(0, H, 256):
        for ox in range(0, W, 256):
            noise.paste(tile, (ox, oy))
    out = Image.composite(
        Image.eval(out, lambda v: min(255, v + 4)),
        Image.eval(out, lambda v: max(0, v - 4)),
        noise.point(lambda v: v if v > 128 else 0))
    out.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HERE, "entry.png")
    render(out_path)
    print("wrote", out_path, os.path.getsize(out_path), "bytes")
