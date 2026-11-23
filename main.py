#!/usr/bin/env python3
"""THE MERIDIAN - a one-page newspaper for Monday, 23 November 2026.

Single-file entry for make.fun news-image-20261123. Python 3.13, standard
library only, no network. Draws a dense 1024x1024 broadsheet page with its
own 5x7 pixel font and its own PNG encoder, then writes /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png). Fully deterministic: two runs produce
byte-identical output.
"""

import os
import struct
import sys
import zlib

# The grader runs `python3 -P -s /bot/main.py`, which drops this script's
# directory from sys.path. Put it back before anything sibling is imported
# (this file imports nothing sibling, but the path fix is kept regardless).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W = 1024
H = 1024

# ---------------------------------------------------------------- canvas ---
BUF = bytearray(W * H * 3)

PAPER = (246, 240, 222)
PAPER_DARK = (236, 228, 200)
INK = (26, 24, 20)
FADE = (74, 68, 58)
RULE = (188, 178, 152)
RED = (176, 32, 24)
BLUE = (30, 70, 120)
TEAL = (18, 88, 88)
GOLD = (186, 138, 38)
GREEN = (38, 110, 60)
SKY = (168, 186, 200)
NIGHT = (24, 34, 54)
WHITE = (250, 248, 240)


def fill_bg(color):
    row = bytes(color) * W
    for y in range(H):
        i = y * W * 3
        BUF[i:i + W * 3] = row


# ------------------------------------------------------------------ font ---
# A hand-drawn 5x7 pixel font. Each glyph is 7 rows of 5 pixels, '#' = ink.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
}
FONT.update({
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".####"),
    "f": ("..##.", ".#...", "#####", ".#...", ".#...", ".#...", ".#..."),
    "g": (".....", ".....", ".####", "#...#", "#...#", ".###.", "####."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "#####", ".#...", ".#...", ".#..#", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "<": ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    ">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    "•": (".....", ".....", ".....", ".###.", ".###.", ".....", "....."),
})

_REPLACE = {
    "á": "a", "à": "a", "é": "e", "è": "e", "í": "i", "ó": "o",
    "ú": "u", "ü": "u", "ñ": "n", "ç": "c", "ş": "s", "ğ": "g",
    "ı": "i", "Á": "A", "É": "E", "Ü": "U", "‘": "'", "’": "'",
    "“": '"', "”": '"', "–": "-", "—": "-", "…": ".",
}


def norm(s):
    out = []
    for ch in s:
        ch = _REPLACE.get(ch, ch)
        out.append(ch if ch in FONT else " ")
    return "".join(out)


# ------------------------------------------------------------ primitives ---
def rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    n = (x1 - x0) * 3
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        BUF[i:i + n] = row


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = color[0]
        BUF[i + 1] = color[1]
        BUF[i + 2] = color[2]


def line(x0, y0, x1, y1, color, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        rect(x0, y0, thick, thick, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                put(xx, yy, color)


# ----------------------------------------------------------------- text ----
def text_w(s, scale):
    return len(norm(s)) * 6 * scale


def draw_text(x, y, s, scale, color, bold=False):
    cx = x
    for ch in norm(s):
        glyph = FONT[ch]
        for r in range(7):
            row = glyph[r]
            base_y = y + r * scale
            for c in range(5):
                if row[c] == "#":
                    rect(cx + c * scale, base_y, scale, scale, color)
                    if bold:
                        rect(cx + c * scale + 1, base_y, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(y, s, scale, color, bold=False):
    w = text_w(s, scale)
    draw_text((W - w) // 2, y, s, scale, color, bold)


def wrap(s, scale, maxw):
    words = norm(s).split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, color, maxw, lh, bold=False):
    for ln in wrap(s, scale, maxw):
        draw_text(x, y, ln, scale, color, bold)
        y += lh
    return y


# ------------------------------------------------------------ PNG output ---
def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += BUF[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------- illustrations --
def art_cop31(x, y, w, h):
    """A summit hall: screen, flag poles and rows of delegate desks."""
    rect(x, y, w, h, TEAL)
    rect(x, y, w, 10, (10, 56, 56))
    # screen
    rect(x + w // 2 - 52, y + 8, 104, 30, WHITE)
    draw_text(x + w // 2 - 30, y + 14, "COP31", 3, TEAL, bold=True)
    draw_text(x + w // 2 - 36, y + 30, "ANTALYA", 1, TEAL)
    # flags on poles
    flag_cols = [RED, GOLD, BLUE, GREEN, (200, 90, 30), (120, 60, 140),
                 (30, 140, 90), (210, 60, 90)]
    for i, col in enumerate(flag_cols):
        fx = x + 14 + i * 38
        rect(fx, y + 6, 2, 26, (220, 214, 190))
        rect(fx + 2, y + 6, 15, 9, col)
    # delegate desks and heads
    for r in range(2):
        dy = y + h - 26 + r * 14
        for d in range(6):
            dx = x + 16 + d * 50
            rect(dx, dy + 5, 40, 6, (96, 66, 38))
            circle(dx + 20, dy + 1, 4, (226, 188, 150))
            rect(dx + 15, dy + 4, 10, 4, BLUE if (d + r) % 2 else RED)


def art_dymer(x, y, w, h):
    """An apartment block, a rescue crane and an ambulance."""
    rect(x, y, w, h, SKY)
    rect(x, y + h - 8, w, 8, (110, 104, 92))
    # apartment block
    bx, by, bw, bh = x + 18, y + 8, 120, h - 16
    rect(bx, by, bw, bh, (196, 188, 168))
    rect(bx, by, bw, 6, (140, 60, 40))
    for r in range(4):
        for c in range(5):
            wx = bx + 10 + c * 23
            wy = by + 12 + r * 13
            if (r * 5 + c) in (3, 7, 12):
                rect(wx, wy, 13, 9, (52, 50, 48))
                line(wx, wy, wx + 13, wy + 9, INK, 1)
            elif (r * 5 + c) % 3 == 0:
                rect(wx, wy, 13, 9, (250, 214, 120))
            else:
                rect(wx, wy, 13, 9, (88, 104, 122))
    # damage scar down one corner
    for i in range(6):
        rect(bx + bw - 12 - i * 2, by + 8 + i * 8, 10, 6, (70, 62, 54))
    # rescue crane
    cx0 = x + w - 90
    rect(cx0, y + 14, 6, h - 22, GOLD)
    line(cx0 + 3, y + 14, bx + bw - 6, y + 10, GOLD, 3)
    line(cx0 + 3, y + 14, cx0 + 60, y + 30, GOLD, 3)
    line(bx + bw - 8, y + 10, bx + bw - 8, y + 30, INK, 1)
    rect(bx + bw - 16, y + 30, 16, 10, RED)
    circle(bx + bw - 8, y + 35, 3, (226, 188, 150))
    rect(cx0 - 8, y + h - 14, 70, 8, (70, 70, 74))
    circle(cx0 + 4, y + h - 5, 4, INK)
    circle(cx0 + 48, y + h - 5, 4, INK)
    # ambulance
    ax = x + w - 150
    rect(ax, y + h - 24, 52, 16, WHITE)
    rect(ax + 38, y + h - 20, 12, 12, (170, 200, 225))
    rect(ax + 20, y + h - 21, 5, 12, RED)
    rect(ax + 16, y + h - 17, 13, 4, RED)
    circle(ax + 10, y + h - 7, 4, INK)
    circle(ax + 42, y + h - 7, 4, INK)


def art_markets(x, y, w, h):
    """A plunging chart on a dark trading screen."""
    rect(x, y, w, h, NIGHT)
    for gx in range(x + 20, x + w - 8, 36):
        line(gx, y + 6, gx, y + h - 16, (52, 66, 96), 1)
    for gy in range(y + 10, y + h - 12, 14):
        line(x + 8, gy, x + w - 10, gy, (52, 66, 96), 1)
    pts = [(x + 14, y + 12), (x + 70, y + 18), (x + 118, y + 15),
           (x + 160, y + 30), (x + 205, y + 28), (x + 240, y + 44),
           (x + 272, y + h - 22), (x + w - 14, y + h - 14)]
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 3)
    for px, py in pts:
        circle(px, py, 3, (255, 120, 100))
    # falling bars
    for i, bh in enumerate((10, 16, 13, 22, 30)):
        rect(x + 30 + i * 26, y + h - 14 - bh, 14, bh, RED if i % 2 else GREEN)
    rect(x + w - 124, y + 4, 116, 36, NIGHT)
    draw_text(x + w - 118, y + 8, "NIKKEI", 2, WHITE, bold=True)
    draw_text(x + w - 118, y + 24, "-5.06%", 2, RED, bold=True)


# ---------------------------------------------------------------- content --
TICKER = ("NIKKEI -5.06% • S&P 500 -3.7% • OIL NEAR $90 • GOLD RP2.505.000/G"
          " • JAKARTA INDEX -1% • BMKG: HEAVY RAIN OVER GREATER JAKARTA")

LEADS = [
    ("COP31 COLLAPSES IN ANTALYA",
     "The summit ended without a deal after overtime; the EU and about 130 "
     "parties rejected a draft omitting fossil fuels.",
     "cop31"),
    ("DYMER STRIKE KILLS TEN",
     "A Russian strike hit a Dymer apartment block, north of Kyiv, killing "
     "at least 10. A boy of 7 was pulled alive from rubble.",
     "dymer"),
    ("AI SELL-OFF ROCKS MARKETS",
     "Nikkei fell 5.06% as a US AI-share rout spread across Asia. Hong "
     "Kong hit a 19-month low; the S&P 500 fell 3.7%.",
     "markets"),
]

# Each column: a list of (section header, [(headline, one factual line)]).
COLUMNS = [
    [
        ("WORLD & EUROPE", [
            ("CORVETTE SUNK AT BENGHAZI",
             "The corvette Merkury sank at Benghazi naval base in Libya "
             "after a suspected Ukrainian sea-drone attack."),
            ("TRIPP CORRIDOR OPENS",
             "Armenia launched the US-backed TRIPP corridor across its "
             "south; Tehran warned it would 'break legs' over it."),
            ("UK TO HOST 2035 WORLD CUP",
             "FIFA is set to confirm the UK as host of the 2035 Women's "
             "World Cup, the first on UK soil since 1966."),
            ("ALLIES DOUSE SHIP FIRE",
             "NATO allies helped put out a fire aboard the Russian "
             "vessel Sparta II in the Gulf of Finland."),
            ("NATO DRILLS ON THE NEMAN",
             "NATO troops rehearsed a contested crossing of the Neman "
             "River in Lithuania."),
            ("FRANCE HOPEFULS DOUBT AID",
             "France's leading presidential candidates both question "
             "Ukraine aid ahead of next spring's election."),
            ("SANCHEZ: VOTERS DECIDE",
             "Spain's PM Sanchez said voters, not the press, will "
             "decide his future."),
        ]),
        ("AMERICAS", [
            ("DEMOCRATS TAKE THE HOUSE",
             "US Democrats clinched at least 258 House seats, their "
             "largest since 1992, after a North Carolina recount flip."),
            ("TRUMP REPOSTS TRUMPCARE",
             "Trump reposted a 'TrumpCare' universal health-care pitch, "
             "drawing reactions across Washington."),
            ("EL CHAPO ISIDRO CAPTURED",
             "Mexico captured FBI most-wanted cartel boss 'El Chapo "
             "Isidro'; 11 died in firefights in Sinaloa."),
            ("IOWA EXPLOSIVES ROW",
             "The US Army plans to detonate tonnes of unstable "
             "explosives in Iowa despite a court order."),
            ("FBI PROBES SYSTEM BREACH",
             "The FBI is probing an apparent breach of a central "
             "law-enforcement system, an AP source said."),
            ("METS SIGN SKUBAL FOR $450M",
             "The New York Mets agreed a record nine-year, $450 "
             "million deal for pitcher Tarik Skubal."),
        ]),
    ],
    [
        ("MIDDLE EAST", [
            ("TANKERS AFIRE NEAR HORMUZ",
             "Two Iranian supertankers hit mines and caught fire near "
             "Hormuz; an Iranian strike wounded two in Bahrain."),
            ("TRUMP WARNS TEHRAN",
             "Trump threatened to sink Iranian vessels that run the "
             "blockade, and said he wants a permanent nuclear deal."),
            ("EISENKOT CONDEMNS ARSON",
             "Israeli leader Eisenkot condemned settler arson in West "
             "Bank villages as 'Jewish terrorism'."),
            ("TALKS END WITHOUT A DEAL",
             "Likud and Eisenkot's Yashar ended coalition talks "
             "without a deal."),
            ("GAZA FOOD VEHICLE STRUCK",
             "An Israeli strike killed three in a food-delivery "
             "vehicle in Gaza City, the Health Ministry said."),
            ("HOUTHIS CLAIM REFINERY HIT",
             "Houthis claimed a hit on the Rabigh refinery; the "
             "coalition said it downed a missile and a drone."),
            ("SYRIA BURNS 400M CAPTAGON",
             "Syria destroyed 400 million Captagon pills in a major "
             "drug haul."),
        ]),
        ("ASIA-PACIFIC", [
            ("M6.5 QUAKE HITS VANUATU",
             "A magnitude 6.5 earthquake struck the Vanuatu region at "
             "02:40 UTC, 598 km deep."),
            ("KOREA MINISTER QUITS",
             "South Korea's education minister resigned over an "
             "exam-cheating scandal."),
            ("INDIA, CHINA TALK BORDER",
             "India and China held 10-day talks to ease border "
             "tensions in Arunachal Pradesh."),
            ("TAIWAN STOCKS SWING WILDLY",
             "Taiwan stocks swung 1,578 points intraday before TSMC "
             "led a recovery of over 2%."),
            ("KOREA EXPORTS PASS $1TN",
             "South Korea's annual exports topped $1 trillion for the "
             "first time."),
            ("AI HACK FRAMEWORK NAMED",
             "Suspected Chinese hackers used the AI framework Cairn "
             "against East Asian universities, researchers said."),
        ]),
    ],
    [
        ("INDONESIA", [
            ("24 DEAD IN BANTEN FIRE",
             "A weekend fire at a Cikande candy factory killed 24 "
             "people; about 30 workers are still missing."),
            ("PRABOWO TO NAME VP PAIR",
             "President Prabowo will hand two VP candidate names to "
             "the MPR on Monday, to replace Gibran."),
            ("ELITES MEET AT HAMBALANG",
             "Gerindra elites met Prabowo at Hambalang as the VP "
             "search heated up."),
            ("KARANGETANG ERUPTS TWICE",
             "Mount Karangetang on Siau erupted twice; lava flowed "
             "500 metres and ash rose 1,000 metres."),
            ("LANDSLIDES BURY HOMES",
             "Landslides in Tasikmalaya buried homes and left two "
             "people missing."),
            ("JAKARTA INDEX FALLS 1%",
             "Jakarta's stock index fell about 1% amid rupiah "
             "pressure."),
            ("PAYMENTS SWING TO SURPLUS",
             "Indonesia's Q3 balance of payments swung to a US$100 "
             "million surplus."),
            ("ANTAM GOLD AT RP2.505.000",
             "Antam gold rose Rp10,000 to Rp2,505,000 per gram."),
        ]),
        ("SPORT & LIFE", [
            ("ALCARAZ WINS ATP FINALS",
             "Carlos Alcaraz won his first ATP Finals title, beating "
             "Alexander Zverev."),
            ("LIVERPOOL ROUT UNITED 4-0",
             "Liverpool beat ten-man Manchester United 4-0 at "
             "Anfield."),
            ("THITIKUL MAKES IT THREE",
             "Jeeno Thitikul won a third straight LPGA title with a "
             "final-round 65."),
            ("PRICE TAKES GRAND SLAM",
             "Gerwyn Price won the Grand Slam of Darts, ending a "
             "four-year wait for a major."),
            ("PAOLO BULGARI DIES AT 89",
             "Italian jeweller Paolo Bulgari has died aged 89."),
        ]),
    ],
]

TIMELINE = [
    "02:40 UTC - M6.5 QUAKE, VANUATU",
    "KARANGETANG ERUPTS TWICE, SIAU",
    "BANTEN FIRE TOLL REACHES 24",
    "TANKERS AFIRE AT HORMUZ",
    "DYMER STRIKE KILLS TEN",
    "TRIPP CORRIDOR OPENS, ARMENIA",
    "NIKKEI CLOSES DOWN 5.06%",
    "ALCARAZ LIFTS ATP FINALS TITLE",
]


# ------------------------------------------------------------ page layout --
MARGIN = 20
COL_W = 318
COL_X = [MARGIN, MARGIN + COL_W + 15, MARGIN + 2 * (COL_W + 15)]


def draw_masthead():
    rect(0, 6, W, 3, INK)
    draw_centered(14, "THE MERIDIAN", 10, INK, bold=True)
    draw_centered(90, "MONDAY, 23 NOVEMBER 2026", 3, INK, bold=True)
    draw_centered(114, "THE DAY'S WORLD IN ONE PAGE - EST. 2026 - NO. 23",
                  1, FADE)
    rect(0, 126, W, 2, INK)
    rect(0, 131, W, 1, INK)
    draw_centered(136, TICKER, 1, RED)


def draw_leads(y):
    arts = {"cop31": art_cop31, "dymer": art_dymer, "markets": art_markets}
    for i, (head, body, art) in enumerate(LEADS):
        x = COL_X[i]
        arts[art](x, y, COL_W, 56)
        line(x, y + 59, x + COL_W, y + 59, RULE, 1)
        yy = draw_para(x, y + 64, head, 3, INK, COL_W, 24, bold=True)
        draw_para(x, yy + 2, body, 2, FADE, COL_W, 18)
        if i < 2:
            line(x + COL_W + 7, y, x + COL_W + 7, y + 196, RULE, 1)
    return y + 200


def draw_section(x, y, header, briefs):
    rect(x, y, COL_W, 22, INK)
    draw_text(x + 8, y + 4, header, 2, PAPER, bold=True)
    y += 26
    for head, body in briefs:
        y = draw_para(x, y, head, 2, INK, COL_W, 15, bold=True)
        y = draw_para(x, y + 1, body, 1, FADE, COL_W, 9)
        y += 2
        line(x, y, x + COL_W, y, RULE, 1)
        y += 3
    return y


def draw_sections(y):
    for ci, sections in enumerate(COLUMNS):
        yy = y
        for header, briefs in sections:
            yy = draw_section(COL_X[ci], yy, header, briefs)
        if ci < 2:
            line(COL_X[ci] + COL_W + 7, y, COL_X[ci] + COL_W + 7, 946,
                 RULE, 1)


def draw_timeline():
    rect(0, 950, W, 2, INK)
    draw_text(MARGIN, 956, "THE DAY IN ORDER", 2, RED, bold=True)
    for i, item in enumerate(TIMELINE):
        col = i % 4
        row = i // 4
        x = MARGIN + col * 246
        y = 978 + row * 13
        draw_text(x, y, str(i + 1), 1, RED, bold=True)
        draw_text(x + 12, y, item, 1, INK)
    rect(0, 1006, W, 1, INK)
    draw_centered(1010, "THE MERIDIAN - MONDAY, 23 NOVEMBER 2026 - PAGE ONE",
                  1, FADE)


def build_page():
    fill_bg(PAPER)
    draw_masthead()
    y = draw_leads(148)
    line(0, y + 4, W, y + 4, INK, 2)
    draw_sections(y + 12)
    draw_timeline()


def main():
    build_page()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(encode_png())


if __name__ == "__main__":
    main()
