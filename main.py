#!/usr/bin/env python3
"""THE WORLD TODAY - Wednesday 25 November 2026.

Pure Python 3 standard library. Draws a 1024x1024 newspaper front page
summing up the day's world news and writes it to entry.png.

No network, no randomness, no timestamps: two runs write identical bytes.
The output directory comes from MAKEFUN_OUTPUT_DIR, default /output.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 231)
PANEL = (238, 231, 216)
INK = (20, 20, 20)
GREY = (112, 106, 94)
RED = (176, 32, 32)
ORANGE = (198, 98, 16)
BLUE = (28, 68, 120)
TEAL = (14, 110, 104)
GREEN = (40, 130, 60)
YELLOW = (255, 200, 60)
WHITE = (255, 255, 255)
BLACK = (12, 12, 12)


# ---------------------------------------------------------------- canvas

def set_px(buf, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def fill_rect(buf, x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        s = (yy * W + x0) * 3
        buf[s:s + len(row)] = row


def hline(buf, x, y, w, c, t=1):
    fill_rect(buf, x, y, w, t, c)


def vline(buf, x, y, h, c, t=1):
    fill_rect(buf, x, y, t, h, c)


def rect_outline(buf, x, y, w, h, c, t=2):
    hline(buf, x, y, w, c, t)
    hline(buf, x, y + h - t, w, c, t)
    vline(buf, x, y, h, c, t)
    vline(buf, x + w - t, y, h, c, t)


def line(buf, x0, y0, x1, y1, c):
    """Bresenham line."""
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_px(buf, x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle_outline(buf, cx, cy, r, c):
    """Midpoint circle outline."""
    x = 0
    y = r
    d = 3 - 2 * r
    while y >= x:
        for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                       (cx + x, cy - y), (cx - x, cy - y),
                       (cx + y, cy + x), (cx - y, cy + x),
                       (cx + y, cy - x), (cx - y, cy - x)):
            set_px(buf, px, py, c)
        x += 1
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6


def disc(buf, cx, cy, r, c):
    """Filled circle."""
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(r * r - dy * dy))
        hline(buf, cx - dx, cy + dy, 2 * dx + 1, c)


def ellipse(buf, cx, cy, rx, ry, c):
    """Thin ellipse outline, sampled parametrically."""
    for deg in range(0, 360, 2):
        a = math.radians(deg)
        set_px(buf, cx + int(rx * math.cos(a)), cy + int(ry * math.sin(a)), c)


def polyline(buf, pts, c):
    for a, b in zip(pts, pts[1:]):
        line(buf, a[0], a[1], b[0], b[1], c)


# ---------------------------------------------------------------- font
# A 5x7 bitmap font, drawn by hand: '#' is ink, '.' is blank.
# Seven rows per glyph, five columns each.

FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".###."),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
}


def text_w(s, sc):
    return len(s) * 6 * sc


def draw_text(buf, x, y, s, sc, color):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == '#':
                    fill_rect(buf, cx + c * sc, y + r * sc, sc, sc, color)
        cx += 6 * sc
    return cx - x


def draw_centered(buf, y, s, sc, color):
    draw_text(buf, (W - text_w(s, sc)) // 2, y, s, sc, color)


def wrap_text(s, sc, max_w):
    lines = []
    cur = ''
    for word in s.split(' '):
        trial = (cur + ' ' + word).strip()
        if text_w(trial, sc) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(buf, x, y, s, sc, max_w, color, leading=None):
    if leading is None:
        leading = 9 * sc
    for ln in wrap_text(s, sc, max_w):
        draw_text(buf, x, y, ln, sc, color)
        y += leading
    return y


# ---------------------------------------------------------------- icons

def burst(buf, cx, cy, r, spike_c, core_c, core_r):
    """Starburst: spikes in spike_c, filled core in core_c."""
    for k in range(12):
        a = math.pi * k / 6
        x1 = cx + int(r * math.cos(a))
        y1 = cy + int(r * math.sin(a))
        line(buf, cx, cy, x1, y1, spike_c)
    disc(buf, cx, cy, core_r, core_c)


def tower(buf):
    """Riyadh's PIF Tower: tall blue tower, windows, explosion, drone."""
    cx = 870
    base_y = 365
    top_y = 196
    # spire
    vline(buf, cx - 1, 172, 24, INK, 2)
    disc(buf, cx, 170, 3, INK)
    # tapered body, filled blue
    for yy in range(top_y, base_y + 1):
        half = 32 + (48 - 32) * (yy - top_y) // (base_y - top_y)
        hline(buf, cx - half, yy, 2 * half + 1, BLUE)
    # edges
    line(buf, cx - 32, top_y, cx - 48, base_y, INK)
    line(buf, cx + 32, top_y, cx + 48, base_y, INK)
    hline(buf, cx - 32, top_y, 65, INK, 2)
    hline(buf, cx - 48, base_y, 97, INK, 2)
    # windows: 7 rows x 3 columns of white squares
    for ry in range(7):
        wy = 212 + ry * 22
        for wx in (-24, 0, 24):
            fill_rect(buf, cx + wx - 6, wy, 12, 12, WHITE)
    # explosion at the top-right corner
    burst(buf, 924, 208, 17, ORANGE, RED, 7)
    disc(buf, 924, 208, 3, YELLOW)
    # small drone above the tower: body, two rotor discs, legs
    fill_rect(buf, 936, 176, 16, 4, INK)
    disc(buf, 934, 172, 3, INK)
    disc(buf, 954, 172, 3, INK)
    hline(buf, 930, 172, 28, INK, 1)
    vline(buf, 940, 180, 5, INK, 1)
    vline(buf, 948, 180, 5, INK, 1)


def ship(buf, x, y, c1, c2, c3):
    """Small cargo ship with three containers and waves."""
    fill_rect(buf, x + 8, y + 2, 10, 8, c1)
    fill_rect(buf, x + 20, y + 2, 10, 8, c2)
    fill_rect(buf, x + 32, y + 2, 10, 8, c3)
    vline(buf, x + 44, y - 4, 14, INK, 2)
    fill_rect(buf, x + 46, y - 4, 8, 5, RED)
    fill_rect(buf, x + 2, y + 12, 44, 10, BLUE)
    line(buf, x + 2, y + 12, x + 8, y + 22, BLUE)
    line(buf, x + 46, y + 12, x + 40, y + 22, BLUE)
    hline(buf, x, y + 26, 48, TEAL, 2)
    hline(buf, x + 8, y + 30, 32, TEAL, 2)


def courthouse(buf, x, y):
    """Courthouse: pediment, four columns, steps."""
    line(buf, x + 2, y + 14, x + 26, y + 2, INK)
    line(buf, x + 26, y + 2, x + 50, y + 14, INK)
    hline(buf, x + 2, y + 14, 48, INK, 2)
    disc(buf, x + 26, y + 9, 3, ORANGE)
    for cx in (x + 7, x + 19, x + 31, x + 43):
        fill_rect(buf, cx, y + 18, 3, 18, INK)
    hline(buf, x, y + 38, 52, INK, 2)
    hline(buf, x + 2, y + 42, 48, INK, 2)


def rocket(buf, x, y):
    """Rocket lifting off, with fins, flame and stars."""
    disc(buf, x + 4, y + 6, 2, YELLOW)
    disc(buf, x + 44, y + 10, 2, ORANGE)
    disc(buf, x + 2, y + 30, 2, YELLOW)
    disc(buf, x + 46, y + 34, 2, ORANGE)
    # body
    fill_rect(buf, x + 18, y + 12, 12, 28, WHITE)
    vline(buf, x + 18, y + 12, 28, INK, 2)
    vline(buf, x + 28, y + 12, 28, INK, 2)
    hline(buf, x + 18, y + 40, 12, INK, 2)
    # nose cone
    line(buf, x + 18, y + 12, x + 24, y + 2, RED)
    line(buf, x + 30, y + 12, x + 24, y + 2, RED)
    hline(buf, x + 18, y + 12, 12, RED, 2)
    # window
    disc(buf, x + 24, y + 22, 4, BLUE)
    circle_outline(buf, x + 24, y + 22, 4, INK)
    # fins
    line(buf, x + 18, y + 30, x + 10, y + 44, RED)
    line(buf, x + 30, y + 30, x + 38, y + 44, RED)
    line(buf, x + 18, y + 32, x + 12, y + 44, RED)
    line(buf, x + 30, y + 32, x + 36, y + 44, RED)
    # flame
    disc(buf, x + 24, y + 47, 5, ORANGE)
    disc(buf, x + 24, y + 49, 3, YELLOW)


def chart(buf, x, y):
    """Market chart: grey bars rising, red line falling."""
    heights = (18, 26, 22, 34, 28, 40)
    for i, hh in enumerate(heights):
        fill_rect(buf, x + 8 + i * 18, y + 70 - hh, 11, hh, (170, 164, 150))
    pts = [(x + 12, y + 12), (x + 32, y + 26), (x + 50, y + 20),
           (x + 70, y + 38), (x + 88, y + 34), (x + 106, y + 52)]
    polyline(buf, pts, RED)
    polyline(buf, [(px + 1, py) for px, py in pts], RED)
    for px, py in pts:
        disc(buf, px, py, 3, RED)
    hline(buf, x, y + 70, 118, INK, 2)


# ---------------------------------------------------------------- layout

MARGIN = 30
CW = W - 2 * MARGIN  # 964


def cell(buf, x, y, w, h, kicker, head_lines, body, icon):
    rect_outline(buf, x, y, w, h, INK, 2)
    draw_text(buf, x + 16, y + 10, kicker, 2, RED)
    hy = y + 32
    for ln in head_lines:
        draw_text(buf, x + 16, hy, ln, 3, INK)
        hy += 21
    draw_block(buf, x + 16, y + 100, body, 2, w - 32, INK, 18)
    icon(buf, x + w - 64, y + 10)


def draw_page(buf):
    # --- masthead
    hline(buf, MARGIN, 24, CW, INK, 5)
    draw_centered(buf, 38, "THE WORLD TODAY", 8, INK)
    draw_centered(buf, 112, "WEDNESDAY, 25 NOVEMBER 2026", 3, RED)
    hline(buf, MARGIN, 136, CW, RED, 4)
    hline(buf, MARGIN, 144, CW, INK, 2)

    # --- lead story: Houthi drone, Riyadh
    rect_outline(buf, MARGIN, 156, CW, 222, INK, 2)
    draw_text(buf, 46, 170, "MIDDLE EAST", 2, RED)
    draw_text(buf, 46, 196, "Houthi drone hits Riyadh's", 4, INK)
    draw_text(buf, 46, 232, "tallest tower, 11 wounded", 4, INK)
    draw_block(buf, 46, 288,
               "A Houthi drone hit the PIF Tower in Riyadh's financial "
               "district -- the second attack in a week. Eleven people "
               "were wounded; the Saudi-led coalition vowed a firm response.",
               2, 660, INK, 19)
    vline(buf, 742, 170, 194, GREY, 2)
    tower(buf)

    # --- row 2: Hormuz + Ukraine
    cell(buf, MARGIN, 392, 472, 174, "STRAIT OF HORMUZ",
         ["Tankers hit mines in", "the Strait of Hormuz"],
         "Iran says 3-4 tankers hit sea mines and burned. Tehran is "
         "closing the strait step by step.",
         lambda b, x, y: ship(b, x, y, RED, YELLOW, TEAL))
    cell(buf, 522, 392, 472, 174, "UKRAINE",
         ["Zelenskiy confirms", "ship strike in Gulf", "of Finland"],
         "Zelenskiy confirmed Ukraine hit a Russian cargo ship in the "
         "Gulf of Finland.",
         lambda b, x, y: ship(b, x, y, BLUE, RED, WHITE))

    # --- row 3: Huawei + Shenzhou-24
    cell(buf, MARGIN, 580, 472, 174, "TECH",
         ["Huawei convicted in", "US criminal trial"],
         "Huawei was convicted in a US criminal trial over trade-secret "
         "theft tied to Iran; cleared of racketeering.",
         courthouse)
    cell(buf, 522, 580, 472, 174, "SPACE",
         ["First Pakistani in", "orbit aboard", "Shenzhou-24"],
         "Shenzhou-24 lifted off today; Pakistan's Zeeshan Ali became "
         "the first Pakistani in orbit, and the first foreigner on "
         "Tiangong.",
         rocket)

    # --- markets, full width
    rect_outline(buf, MARGIN, 768, CW, 112, INK, 2)
    draw_text(buf, 46, 778, "MARKETS", 2, RED)
    draw_text(buf, 46, 800, "AI sell-off hits Wall Street", 3, INK)
    draw_block(buf, 46, 836,
               "The Nasdaq fell 1.5%, Nvidia -6%, Micron -11% a day after "
               "a rally; the Trump administration is preparing higher "
               "tariffs.",
               2, 780, INK, 19)
    draw_text(buf, 872, 778, "-1.5%", 2, RED)
    chart(buf, 856, 796)

    # --- footer: also today
    fill_rect(buf, MARGIN, 892, CW, 30, RED)
    draw_text(buf, 44, 902, "ALSO TODAY", 2, WHITE)
    draw_text(buf, 762, 902, "THE WORLD IN BRIEF", 2, WHITE)
    foot = [
        ("GAZA -- ", "Israeli strike kills Hamas security official "
         "Naeem Abu Nahel; 7 dead."),
        ("FRANCE -- ", "Sarkozy and Carla Bruni ordered to face "
         "corruption trial, April 2027."),
        ("NEPAL -- ", "Magnitude 5.6 earthquake shakes eastern Nepal, "
         "Koshi province."),
        ("MALAYSIA -- ", "Malaysia to repatriate 6,500+ Rohingya to "
         "Myanmar in December."),
    ]
    fy = 934
    for lead, rest in foot:
        draw_text(buf, MARGIN, fy, lead, 2, RED)
        draw_text(buf, MARGIN + text_w(lead, 2), fy, rest, 2, INK)
        fy += 20


# ---------------------------------------------------------------- PNG

def _chunk(kind, data):
    out = struct.pack('>I', len(data)) + kind + data
    out += struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    return out


def write_png(path, buf, w, h):
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)
        raw += buf[yy * stride:(yy + 1) * stride]
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    png += _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += _chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def main():
    buf = bytearray(bytes(PAPER) * (W * H))
    draw_page(buf)
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, 'entry.png'), buf, W, H)


if __name__ == '__main__':
    main()
