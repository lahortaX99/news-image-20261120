#!/usr/bin/env python3
"""Render the front page for news-image-20261120.

Draws a one-page newspaper (1024x1024) from app/stories.json:
masthead + dateline, a dotted world map with story markers, the day
in numbers, three lead stories with small illustrations, and a numbered
grid of every story. Writes a PNG. Deterministic: same input gives the
same bytes. Run from the repository root: python3 app/render.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "app" / "stories.json"
OUT = REPO / "entry.png"

W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (17, 17, 17)
RED = (185, 28, 28)
GREY = (68, 68, 68)
MAP_BG = (219, 234, 254)
DOT = (21, 128, 61)
WHITE = (255, 255, 255)

REGION_COLORS = {
    "AMERICAS": (29, 78, 216),
    "EUROPE": (126, 34, 206),
    "MIDEAST": (146, 64, 14),
    "AFRICA": (22, 101, 52),
    "ASIA": (15, 118, 110),
    "OCEANIA": (157, 23, 77),
    "SCIENCE": (87, 83, 78),
}
REGION_ORDER = ["AMERICAS", "EUROPE", "MIDEAST", "AFRICA", "ASIA", "OCEANIA", "SCIENCE"]

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_B = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SANS_B = str(FONT_DIR / "DejaVuSans-Bold.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# Dotted world map: land as (start, end) column ranges per row.
# Grid is 52 columns (longitude -180..180) by 25 rows (latitude ~84..-55).
MAP_RANGES = [
    [(16, 17)],
    [(6, 9), (15, 18)],
    [(1, 13), (15, 19), (27, 29), (36, 50)],
    [(1, 14), (16, 18), (27, 30), (35, 50)],
    [(4, 14), (25, 25), (27, 30), (35, 50)],
    [(5, 14), (25, 25), (26, 32), (35, 49)],
    [(6, 15), (26, 34), (35, 49)],
    [(6, 15), (25, 33), (35, 45), (48, 49)],
    [(7, 15), (25, 27), (30, 30), (32, 33), (34, 38), (40, 46), (48, 49)],
    [(7, 13), (26, 34), (36, 38), (40, 46)],
    [(8, 11), (26, 34), (36, 38), (39, 40), (42, 45)],
    [(9, 12), (26, 34), (36, 37), (38, 40), (42, 45)],
    [(10, 12), (26, 34), (39, 40), (42, 45)],
    [(13, 18), (27, 32), (43, 47)],
    [(13, 19), (28, 33), (43, 47)],
    [(14, 19), (29, 33)],
    [(14, 19), (29, 33)],
    [(14, 18), (29, 33), (43, 49)],
    [(15, 18), (29, 32), (34, 35), (43, 49)],
    [(15, 17), (29, 32), (43, 49), (50, 51)],
    [(15, 17), (30, 31), (44, 48), (50, 51)],
    [(16, 17), (46, 47), (50, 50)],
    [(16, 17), (50, 50)],
    [(16, 17)],
    [(16, 16)],
]
# Red markers for key stories, as (col, row) in the same grid.
MARKERS = [(30, 6), (43, 11), (33, 10), (37, 10), (31, 15), (48, 20), (50, 18)]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=MAP_BG, outline=INK, width=2)
    cols, rows = 52, 25
    sx, sy = (w - 4) / cols, (h - 4) / rows
    for r, ranges in enumerate(MAP_RANGES):
        cy = y + 2 + (r + 0.5) * sy
        for a, b in ranges:
            for c in range(a, b + 1):
                cx = x + 2 + (c + 0.5) * sx
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=DOT)
    for c, r in MARKERS:
        cx = x + 2 + (c + 0.5) * sx
        cy = y + 2 + (r + 0.5) * sy
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED, outline=WHITE, width=1)


def draw_burst(d, cx, cy, r, color):
    """A small explosion starburst: filled circle plus spikes."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        x2, y2 = cx + (r + 7) * math.cos(a), cy + (r + 7) * math.sin(a)
        d.line([cx, cy, x2, y2], fill=color, width=3)


def draw_lead_art(d, box, kind):
    """Small geometric illustration strip at the top of a lead box."""
    x, y, w, h = box
    if kind == "missiles":
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=(30, 41, 59))
        # building silhouettes
        import random
        rnd = random.Random(7)
        bx = x
        while bx < x + w:
            bw = rnd.randint(18, 34)
            bh = rnd.randint(18, h - 14)
            d.rectangle([bx, y + h - bh, bx + bw, y + h - 1], fill=(15, 23, 42))
            bx += bw + 3
        draw_burst(d, x + int(w * 0.30), y + 22, 9, (249, 115, 22))
        draw_burst(d, x + int(w * 0.68), y + 30, 12, (239, 68, 68))
        draw_burst(d, x + int(w * 0.88), y + 16, 7, (250, 204, 21))
    elif kind == "flags":
        # US, China, Russia flags side by side
        fw, fh = w // 3, h - 16
        fx, fy = x, y + 8
        for i in range(7):
            d.rectangle([fx, fy + i * (fh // 7), fx + fw - 6, fy + (i + 1) * (fh // 7)], fill=(185, 28, 28) if i % 2 == 0 else WHITE)
        d.rectangle([fx, fy, fx + fw // 2, fy + fh // 2], fill=(29, 78, 216))
        d.rectangle([fx + fw, fy, fx + 2 * fw - 6, fy + fh], fill=(220, 38, 38))
        for sx, sy in [(fw // 4, fh // 4), (fw // 2, fh // 3), (fw // 3, fh // 2)]:
            d.ellipse([fx + fw + sx - 3, fy + sy - 3, fx + fw + sx + 3, fy + sy + 3], fill=(250, 204, 21))
        d.rectangle([fx + 2 * fw, fy, fx + 3 * fw - 6, fy + fh // 3], fill=WHITE)
        d.rectangle([fx + 2 * fw, fy + fh // 3, fx + 3 * fw - 6, fy + 2 * fh // 3], fill=(29, 78, 216))
        d.rectangle([fx + 2 * fw, fy + 2 * fh // 3, fx + 3 * fw - 6, fy + fh], fill=(185, 28, 28))
        d.rectangle([x, y + h - 4, x + w - 1, y + h - 1], fill=(180, 130, 29))
    else:  # "markets": rising bars with a falling red line
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=(240, 244, 248))
        bars = [0.30, 0.42, 0.38, 0.55, 0.72, 0.95]
        bw = (w - 20) // len(bars)
        for i, f in enumerate(bars):
            bx = x + 10 + i * bw
            bh = int((h - 18) * f)
            col = (220, 38, 38) if i == len(bars) - 1 else (37, 99, 235)
            d.rectangle([bx, y + h - 6 - bh, bx + bw - 6, y + h - 6], fill=col)
        pts = [(x + 12 + i * bw, y + h - 10 - int((h - 18) * f)) for i, f in enumerate(bars)]
        d.line(pts, fill=(220, 38, 38), width=3)
        d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4], fill=(220, 38, 38))


def main():
    data = json.loads(DATA.read_text())
    meta = data["meta"]
    stories = sorted(data["stories"], key=lambda s: s["n"])
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 26  # side margin

    # Masthead
    f_mast = font(SERIF_B, 100)
    title = meta["title"]
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 10), title, font=f_mast, fill=INK)
    d.rectangle([mx, 128, W - mx - 1, 131], fill=RED)

    # Dateline row
    f_date = font(SANS_B, 17)
    f_small = font(SANS, 15)
    d.text((mx, 140), meta["volume"], font=f_small, fill=INK)
    dtw = d.textlength(meta["date"], font=f_date)
    d.text(((W - dtw) / 2, 139), meta["date"], font=f_date, fill=INK)
    ctw = d.textlength(meta["count_line"], font=f_small)
    d.text((W - mx - ctw, 140), meta["count_line"], font=f_small, fill=INK)
    d.rectangle([mx, 166, W - mx - 1, 167], fill=INK)

    # Map (left) and numbers (right)
    map_x, map_y, map_w, map_h = mx, 176, 470, 210
    draw_map(d, map_x, map_y, map_w, map_h)
    num_x, num_y, num_w = 512, 176, W - mx - 512
    f_num_title = font(SANS_B, 20)
    d.text((num_x, num_y), "THE DAY IN NUMBERS", font=f_num_title, fill=INK)
    d.rectangle([num_x, num_y + 30, num_x + num_w - 1, num_y + 31], fill=INK)
    f_big = font(SANS_B, 40)
    f_lab = font(SANS, 17)
    ry = num_y + 42
    for item in data["numbers"]:
        d.text((num_x, ry), item["value"], font=f_big, fill=RED)
        vw = d.textlength(item["value"], font=f_big)
        d.text((num_x + vw + 14, ry + 12), item["label"], font=f_lab, fill=INK)
        ry += 46

    # Region chips legend
    f_leg = font(SANS, 13)
    f_leg_b = font(SANS_B, 13)
    lx, ly = mx, 394
    d.text((lx, ly), "CHIPS:", font=f_leg_b, fill=INK)
    lx += d.textlength("CHIPS:", font=f_leg_b) + 10
    for reg in REGION_ORDER:
        d.rectangle([lx, ly + 2, lx + 12, ly + 14], fill=REGION_COLORS[reg])
        lx += 17
        d.text((lx, ly), reg, font=f_leg, fill=INK)
        lx += d.textlength(reg, font=f_leg) + 14

    # Three lead stories
    leads = stories[:3]
    kinds = ["missiles", "flags", "markets"]
    box_w = (W - 2 * mx - 24) // 3
    box_h = 176
    box_y = 420
    f_head = font(SANS_B, 19)
    f_sub = font(SANS, 13)
    f_badge = font(SANS_B, 15)
    for i, st in enumerate(leads):
        bx = mx + i * (box_w + 12)
        d.rectangle([bx, box_y, bx + box_w - 1, box_y + box_h - 1], fill=PAPER, outline=INK, width=2)
        draw_lead_art(d, (bx + 2, box_y + 2, box_w - 4, 58), kinds[i])
        ty = box_y + 70
        # number badge
        d.rectangle([bx + 10, ty, bx + 34, ty + 24], fill=RED)
        d.text((bx + 10, ty + 2), str(st["n"]), font=f_badge, fill=WHITE, anchor="la")
        # center the digit in the badge
        nw = d.textlength(str(st["n"]), font=f_badge)
        d.rectangle([bx + 10, ty, bx + 34, ty + 24], fill=RED)
        d.text((bx + 10 + (24 - nw) / 2, ty + 3), str(st["n"]), font=f_badge, fill=WHITE)
        lines = wrap(d, st["headline"], f_head, box_w - 48)
        hy = ty
        for ln in lines[:3]:
            d.text((bx + 42, hy), ln, font=f_head, fill=INK)
            hy += 23
        sy = ty + 23 * min(len(lines), 3) + 4
        for ln in wrap(d, st.get("sub", ""), f_sub, box_w - 20)[:2]:
            d.text((bx + 10, sy), ln, font=f_sub, fill=GREY)
            sy += 15

    # Numbered grid: stories 4..39, 4 columns x 9 rows
    grid = stories[3:]
    cols, rows = 4, 9
    col_w = (W - 2 * mx - 30) // cols
    row_h = 44
    grid_y = 602
    f_grid = font(SANS_B, 13)
    f_chip = font(SANS_B, 12)
    for idx, st in enumerate(grid):
        c, r = idx % cols, idx // cols
        gx = mx + c * (col_w + 10)
        gy = grid_y + r * row_h
        col = REGION_COLORS[st["region"]]
        d.rectangle([gx, gy, gx + 20, gy + 20], fill=col)
        nw = d.textlength(str(st["n"]), font=f_chip)
        d.text((gx + (20 - nw) / 2, gy + 3), str(st["n"]), font=f_chip, fill=WHITE)
        lines = wrap(d, st["headline"], f_grid, col_w - 28)
        ly = gy
        for ln in lines[:3]:
            d.text((gx + 26, ly), ln, font=f_grid, fill=INK)
            ly += 14

    # Footer
    f_foot = font(SANS, 12)
    ftw = d.textlength(meta["footer"], font=f_foot)
    d.text(((W - ftw) / 2, 1004), meta["footer"], font=f_foot, fill=GREY)

    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {out.stat().st_size} bytes {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
