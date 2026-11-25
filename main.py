#!/usr/bin/env python3
"""THE WORLD TODAY -- Wednesday 25 November 2026.

Draws a one-page newspaper front page summing up the world's news of
25 November 2026 as a single 1024x1024 PNG. Pure PIL, no network, no
randomness, no clock: two runs produce byte-identical output.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes: $MAKEFUN_OUTPUT_DIR/entry.png (or ./entry.png when unset).
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (251, 247, 238)      # warm newsprint cream
INK = (22, 22, 22)           # near-black
RED = (185, 28, 28)          # accent red
DARKRED = (140, 20, 20)
GREY = (105, 102, 96)
LIGHTGREY = (200, 196, 188)
BLUE = (38, 78, 130)
ORANGE = (214, 110, 30)
GOLD = (196, 150, 40)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, text, fnt, max_width, fill=INK,
                    line_spacing=1.28, max_lines=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap(draw, text, fnt, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    step = int(fnt.size * line_spacing)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


# ---------------------------------------------------------------- icons
# Every icon is drawn from PIL primitives inside a square box (x, y, s).

def icon_tower(draw, x, y, s):
    """A tall skyscraper tower with a spire, hit near the top."""
    cx = x + s // 2
    base = y + s - 6
    top = y + 8
    # tower body, slightly tapered
    draw.polygon([(cx - s * 0.30, base), (cx - s * 0.20, top + s * 0.22),
                  (cx + s * 0.20, top + s * 0.22), (cx + s * 0.30, base)],
                 fill=BLUE, outline=INK, width=2)
    # spire
    draw.polygon([(cx - 4, top + s * 0.22), (cx, top), (cx + 4, top + s * 0.22)],
                 fill=INK)
    # window rows
    for r in range(5):
        wy = top + s * 0.30 + r * s * 0.12
        for c in range(3):
            wx = cx - s * 0.17 + c * s * 0.12
            draw.rectangle([wx, wy, wx + s * 0.07, wy + s * 0.05],
                           fill=(220, 225, 235))
    # impact burst near the top of the tower
    bx, by = cx + s * 0.22, top + s * 0.30
    for dx, dy, ln in [(-14, 0, 16), (14, 0, 16), (0, -14, 16),
                       (0, 14, 16), (-10, -10, 12), (10, 10, 12),
                       (10, -10, 12), (-10, 10, 12)]:
        draw.line([(bx, by), (bx + dx, by + dy)], fill=RED, width=4)
    draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=ORANGE)
    # small drone approaching
    dx0, dy0 = x + s - 14, y + 6
    draw.ellipse([dx0 - 5, dy0 - 3, dx0 + 5, dy0 + 3], fill=INK)
    draw.line([(dx0 - 12, dy0 - 4), (dx0 + 12, dy0 - 4)], fill=INK, width=2)
    draw.line([(dx0 - 12, dy0 + 4), (dx0 + 12, dy0 + 4)], fill=INK, width=2)


def icon_tanker(draw, x, y, s):
    """An oil tanker on waves, with smoke rising from the deck."""
    hull_y = y + s * 0.52
    # hull
    draw.polygon([(x + 2, hull_y), (x + s - 2, hull_y),
                  (x + s - 14, hull_y + s * 0.26), (x + 14, hull_y + s * 0.26)],
                 fill=(150, 40, 32), outline=INK, width=2)
    # deck containers
    for i, col in enumerate([BLUE, GOLD, (90, 130, 90)]):
        cx0 = x + 8 + i * s * 0.24
        draw.rectangle([cx0, hull_y - s * 0.22, cx0 + s * 0.20,
                        hull_y - 2], fill=col, outline=INK, width=2)
    # bridge tower
    draw.rectangle([x + s * 0.74, hull_y - s * 0.36, x + s * 0.88,
                    hull_y - 2], fill=(240, 240, 235), outline=INK, width=2)
    # smoke puffs above the deck
    for px, py, r in [(x + s * 0.26, y + 8, 7), (x + s * 0.34, y + 16, 9),
                      (x + s * 0.24, y + 24, 6)]:
        draw.ellipse([px - r, py - r, px + r, py + r], fill=GREY)
    # waves
    for wy in (y + s - 12, y + s - 2):
        for k in range(4):
            wx = x + 2 + k * s * 0.24
            draw.arc([wx, wy - 6, wx + s * 0.22, wy + 8], 200, 340,
                     fill=BLUE, width=3)


def icon_ship(draw, x, y, s):
    """A cargo ship with a drone above it and a splash alongside."""
    hull_y = y + s * 0.55
    draw.polygon([(x + 4, hull_y), (x + s - 4, hull_y),
                  (x + s - 16, hull_y + s * 0.24), (x + 16, hull_y + s * 0.24)],
                 fill=(60, 70, 80), outline=INK, width=2)
    # containers
    for i, col in enumerate([RED, BLUE]):
        cx0 = x + 14 + i * s * 0.22
        draw.rectangle([cx0, hull_y - s * 0.20, cx0 + s * 0.18,
                        hull_y - 2], fill=col, outline=INK, width=2)
    # mast
    draw.line([(x + s * 0.78, hull_y), (x + s * 0.78, hull_y - s * 0.34)],
              fill=INK, width=3)
    # drone above, larger and clearer
    dx0, dy0 = x + s * 0.60, y + 10
    draw.ellipse([dx0 - 7, dy0 - 4, dx0 + 7, dy0 + 4], fill=INK)
    draw.line([(dx0 - 16, dy0 - 3), (dx0 + 16, dy0 - 3)], fill=INK, width=2)
    draw.line([(dx0 - 16, dy0 + 5), (dx0 + 16, dy0 + 5)], fill=INK, width=2)
    draw.line([(dx0 - 5, dy0 + 14), (dx0 + 5, dy0 + 14)], fill=RED, width=3)
    # splash
    for k in range(3):
        sx = x + 6 + k * 7
        draw.line([(sx, hull_y + s * 0.28), (sx, hull_y + s * 0.28 + 12)],
                  fill=BLUE, width=3)


def icon_court(draw, x, y, s):
    """A courthouse: pediment, columns, steps."""
    # pediment
    draw.polygon([(x + 4, y + s * 0.34), (x + s // 2, y + 6),
                  (x + s - 4, y + s * 0.34)], fill=(235, 230, 215),
                 outline=INK, width=2)
    draw.ellipse([x + s // 2 - 6, y + s * 0.16, x + s // 2 + 6,
                  y + s * 0.16 + 12], fill=GOLD, outline=INK, width=2)
    # entablature
    draw.rectangle([x + 4, y + s * 0.34, x + s - 4, y + s * 0.42],
                   fill=(225, 220, 205), outline=INK, width=2)
    # columns
    for i in range(4):
        cx0 = x + 10 + i * s * 0.23
        draw.rectangle([cx0, y + s * 0.42, cx0 + s * 0.10,
                        y + s * 0.78], fill=(245, 242, 235),
                       outline=INK, width=2)
    # steps
    for i in range(3):
        draw.rectangle([x + 4 + i * 6, y + s * 0.78 + i * s * 0.06,
                        x + s - 4 - i * 6, y + s * 0.84 + i * s * 0.06],
                       fill=(210, 205, 195), outline=INK, width=1)


def icon_rocket(draw, x, y, s):
    """A rocket lifting off, with stars."""
    cx = x + s // 2
    # stars
    for sx, sy in [(x + 8, y + 14), (x + s - 12, y + 26), (x + 12, y + s * 0.55),
                   (x + s - 8, y + s * 0.62)]:
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)
    # flame
    draw.polygon([(cx - 12, y + s * 0.72), (cx + 12, y + s * 0.72),
                  (cx, y + s - 4)], fill=ORANGE, outline=RED, width=2)
    draw.polygon([(cx - 6, y + s * 0.72), (cx + 6, y + s * 0.72),
                  (cx, y + s * 0.88)], fill=(250, 200, 60))
    # fins
    draw.polygon([(cx - 16, y + s * 0.55), (cx - 26, y + s * 0.78),
                  (cx - 16, y + s * 0.74)], fill=RED, outline=INK, width=2)
    draw.polygon([(cx + 16, y + s * 0.55), (cx + 26, y + s * 0.78),
                  (cx + 16, y + s * 0.74)], fill=RED, outline=INK, width=2)
    # body
    draw.rectangle([cx - 16, y + s * 0.22, cx + 16, y + s * 0.74],
                   fill=(245, 245, 240), outline=INK, width=2)
    # nose cone
    draw.polygon([(cx - 16, y + s * 0.22), (cx, y + 4),
                  (cx + 16, y + s * 0.22)], fill=RED, outline=INK, width=2)
    # window
    draw.ellipse([cx - 8, y + s * 0.34, cx + 8, y + s * 0.34 + 16],
                 fill=(150, 200, 235), outline=INK, width=2)
    # flag stripe
    draw.rectangle([cx - 16, y + s * 0.56, cx + 16, y + s * 0.62],
                   fill=(30, 120, 60))


def icon_chart(draw, x, y, s):
    """A falling stock chart: axes, descending red line, arrow."""
    ox, oy = x + 10, y + s - 12
    # faint bars
    bars = [0.55, 0.72, 0.62, 0.45, 0.38, 0.22]
    bw = (s - 24) / len(bars)
    for i, h in enumerate(bars):
        bx0 = x + 12 + i * bw
        draw.rectangle([bx0, oy - h * s * 0.62, bx0 + bw - 4, oy],
                       fill=(215, 210, 200), outline=GREY, width=1)
    # axes
    draw.line([(ox, y + 8), (ox, oy)], fill=INK, width=2)
    draw.line([(ox, oy), (x + s - 6, oy)], fill=INK, width=2)
    # descending line
    pts = [(x + 14, y + 14), (x + s * 0.30, y + s * 0.30),
           (x + s * 0.48, y + s * 0.26), (x + s * 0.66, y + s * 0.52),
           (x + s - 12, y + s * 0.72)]
    draw.line(pts, fill=RED, width=4, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED)
    # arrow head at the end
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 12, ey - 2), (ex - 2, ey - 12)], fill=RED)
    # percent tag
    draw.text((x + s * 0.52, y + 2), "-1.5%", font=font(SANS_BOLD, 18),
              fill=RED)


# ---------------------------------------------------------------- layout

LEAD = {
    "kicker": "MIDDLE EAST",
    "headline": "Houthi drone hits Riyadh's tallest tower, 11 wounded",
    "body": ("A Houthi drone hit the PIF Tower in Riyadh's financial district "
             "-- the second attack in a week. Eleven people were wounded; "
             "the Saudi-led coalition vowed a firm response."),
}

STORIES = [
    {
        "kicker": "STRAIT OF HORMUZ",
        "headline": "Tankers hit mines in the Strait of Hormuz",
        "body": ("Iran says 3-4 tankers hit sea mines and burned -- unverified. "
                 "Tehran is closing the strait step by step."),
        "icon": icon_tanker,
    },
    {
        "kicker": "UKRAINE",
        "headline": "Zelenskiy confirms ship strike in Gulf of Finland",
        "body": ("Zelenskiy confirmed Ukraine hit a Russian cargo ship in the "
                 "Gulf of Finland; Norway urged Kyiv to take care."),
        "icon": icon_ship,
    },
    {
        "kicker": "TECH",
        "headline": "Huawei convicted in US criminal trial",
        "body": ("Huawei was convicted in a US criminal trial over trade-secret "
                 "theft tied to Iran; cleared of racketeering."),
        "icon": icon_court,
    },
    {
        "kicker": "SPACE",
        "headline": "First Pakistani in orbit aboard Shenzhou-24",
        "body": ("Shenzhou-24 lifted off today; Pakistan's Zeeshan Ali became "
                 "the first Pakistani in orbit, and the first foreigner on "
                 "Tiangong."),
        "icon": icon_rocket,
    },
    {
        "kicker": "MARKETS",
        "headline": "AI sell-off hits Wall Street",
        "body": ("The Nasdaq fell 1.5%, Nvidia -6%, Micron -11% a day after a "
                 "rally; the Trump administration is preparing higher tariffs "
                 "on China, the EU and 15 other countries."),
        "icon": icon_chart,
    },
]

ALSO = [
    "GAZA -- Israeli strike kills Hamas security official Naeem Abu Nahel; seven Palestinians dead.",
    "FRANCE -- Sarkozy and Carla Bruni ordered to face a corruption trial, starting in April 2027.",
    "NEPAL -- Magnitude 5.6 earthquake shakes eastern Nepal, Koshi province.",
    "MALAYSIA -- Malaysia to repatriate 6,500+ Rohingya refugees to Myanmar in December.",
]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    f_mast = font(SANS_BOLD, 72)
    f_date = font(SANS_BOLD, 22)
    f_kicker = font(SANS_BOLD, 18)
    f_kicker_lead = font(SANS_BOLD, 20)
    f_head_lead = font(SANS_BOLD, 38)
    f_body_lead = font(SANS, 20)
    f_head = font(SANS_BOLD, 26)
    f_body = font(SANS, 18)
    f_strip = font(SANS_BOLD, 22)
    f_also = font(SANS, 18)
    f_also_b = font(SANS_BOLD, 18)

    # ---- masthead
    title = "THE WORLD TODAY"
    tw = draw.textlength(title, font=f_mast)
    draw.text(((W - tw) / 2, 24), title, font=f_mast, fill=INK)
    date = "WEDNESDAY, 25 NOVEMBER 2026"
    dw = draw.textlength(date, font=f_date)
    draw.text(((W - dw) / 2, 104), date, font=f_date, fill=RED)
    draw.rectangle([36, 134, 988, 139], fill=RED)
    draw.rectangle([36, 143, 988, 144], fill=INK)

    # ---- lead story (y 156-380)
    lx, ly, lw, lh = 36, 156, 952, 224
    draw.rectangle([lx, ly, lx + lw, ly + lh], outline=INK, width=2)
    tx = lx + 22
    ty = ly + 14
    draw.text((tx, ty), LEAD["kicker"], font=f_kicker_lead, fill=RED)
    ty += 30
    ty = draw_text_block(draw, tx, ty, LEAD["headline"], f_head_lead, 640,
                         line_spacing=1.12, max_lines=2)
    ty += 8
    draw_text_block(draw, tx, ty, LEAD["body"], f_body_lead, 640,
                    line_spacing=1.32, max_lines=3)
    icon_tower(draw, lx + lw - 212, ly + 16, 192)
    draw.line([(lx + lw - 226, ly + 16), (lx + lw - 226, ly + lh - 16)],
              fill=LIGHTGREY, width=1)

    # ---- grid: first four stories in 2 columns x 2 rows (y 392-738)
    gx, gy = 36, 392
    cw, ch, gap = 466, 168, 20
    for i, st in enumerate(STORIES[:4]):
        col, row = i % 2, i // 2
        cx0 = gx + col * (cw + gap)
        cy0 = gy + row * (ch + 10)
        draw.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], outline=INK, width=2)
        ix = cx0 + cw - 92
        iy = cy0 + 8
        st["icon"](draw, ix, iy, 80)
        draw.text((cx0 + 14, cy0 + 10), st["kicker"], font=f_kicker, fill=RED)
        hy = draw_text_block(draw, cx0 + 14, cy0 + 34, st["headline"], f_head,
                             cw - 110, line_spacing=1.12, max_lines=2)
        draw_text_block(draw, cx0 + 14, hy + 6, st["body"], f_body, cw - 28,
                        line_spacing=1.28, max_lines=3)

    # ---- fifth story (MARKETS) as one full-width row (y 748-868)
    st = STORIES[4]
    mx, my, mw, mh = 36, 748, 952, 120
    draw.rectangle([mx, my, mx + mw, my + mh], outline=INK, width=2)
    st["icon"](draw, mx + mw - 118, my + 10, 100)
    draw.text((mx + 16, my + 10), st["kicker"], font=f_kicker, fill=RED)
    hy = draw_text_block(draw, mx + 16, my + 32, st["headline"], f_head,
                         mw - 160, line_spacing=1.12, max_lines=1)
    draw_text_block(draw, mx + 16, hy + 6, st["body"], f_body, mw - 160,
                    line_spacing=1.28, max_lines=2)

    # ---- footer: ALSO TODAY (strip y 880-910, items y 918-1006)
    fy = 880
    draw.rectangle([36, fy, 988, fy + 30], fill=RED)
    draw.text((48, fy + 4), "ALSO TODAY", font=f_strip, fill=(255, 255, 255))
    draw.text((988 - draw.textlength("THE WORLD IN BRIEF", font=f_also),
               fy + 6), "THE WORLD IN BRIEF", font=f_also,
              fill=(255, 220, 220))
    ay = fy + 38
    for item in ALSO:
        tag, _, rest = item.partition(" -- ")
        draw.text((48, ay), tag + " --", font=f_also_b, fill=RED)
        tw2 = draw.textlength(tag + " -- ", font=f_also_b)
        draw.text((48 + tw2, ay), rest, font=f_also, fill=INK)
        ay += 22

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(os.path.join(out_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
