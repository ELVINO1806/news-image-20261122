#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Sunday 22 November 2026.

One-page newspaper image: 38 verified stories, 8 regions, one day.
Pure Python 3 stdlib only. Deterministic: no network, no clock, no
unseeded randomness. Renders at 2x supersampling, downsamples to
1024x1024 PNG, writes to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Layout (final 1024 coordinates):
  masthead - numbers strip - region bar - 3 lead panels -
  5 secondary panels - numbered world dot-map + date-check box -
  ALSO ON (30 one-liners, 2 columns) - footer.
"""
import hashlib
import math
import os
import struct
import zlib

S = 2
W = 1024
H = 1024
SW = W * S
SH = H * S

PAPER = (247, 243, 234)
INK = (18, 18, 18)
SOFT = (74, 72, 66)
RED = (178, 32, 28)
WHITE = (255, 255, 255)
PANEL = (255, 255, 255)
RULE = (150, 146, 136)
DOT = (64, 74, 92)
OCEAN = (233, 237, 240)

# ---------------------------------------------------------------- font 5x7
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "%": ("10001", "10010", "00010", "00100", "01000", "01001", "10001"),
    "$": ("00100", "01111", "10101", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10010", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "*": ("00000", "01010", "00100", "11111", "00100", "01010", "00000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "•": ("00000", "00000", "01110", "01110", "01110", "00000", "00000"),
}


def norm(s):
    return s.upper().replace("—", "-").replace("–", "-").replace("’", "'")


# ---------------------------------------------------------------- data
# Numbers strip: (big figure, label line 1, label line 2). All from the log.
NUMBERS = [
    ("186", "DRONES LAUNCHED", "161 SHOT DOWN"),
    ("258", "DEMOCRAT HOUSE SEATS", "LARGEST SINCE 1992"),
    ("720/9", "INDIA'S RECORD TEST", "TOTAL IN NEW ZEALAND"),
    ("37", "WORKERS MISSING", "BANTEN FACTORY FIRE"),
    ("$50BN", "ARGENTINA LNG DEAL", "APPROVED FOR EXPORT"),
    ("130", "DAYS OF US NAVAL", "BLOCKADE OF IRAN"),
]

REGIONS = [
    ("EUROPE", 7, (31, 78, 160)),
    ("ASIA", 7, (198, 90, 20)),
    ("MIDDLE EAST", 5, (120, 60, 140)),
    ("AFRICA", 4, (34, 139, 92)),
    ("NORTH AMERICA", 5, (180, 30, 60)),
    ("LATIN AMERICA", 4, (220, 170, 20)),
    ("OCEANIA", 2, (20, 140, 160)),
    ("GLOBAL", 4, (90, 90, 90)),
]


def region_of(n):
    if n <= 7:
        return "EUROPE"
    if n <= 14:
        return "ASIA"
    if n <= 19:
        return "MIDDLE EAST"
    if n <= 23:
        return "AFRICA"
    if n <= 28:
        return "NORTH AMERICA"
    if n <= 32:
        return "LATIN AMERICA"
    if n <= 34:
        return "OCEANIA"
    return "GLOBAL"


REGION_COLOR = {name: col for name, _c, col in REGIONS}

# World dot-map: 96 cols x 37 rows, land spans per row (col ranges, inclusive).
# Equirectangular: col = (lon + 180) / 3.75, row = (90 - lat) / 4.865.
LAND = {
    1: [(22, 26), (62, 78)],
    2: [(10, 26), (29, 33), (60, 86)],
    3: [(8, 28), (29, 34), (56, 88)],
    4: [(8, 29), (29, 33), (52, 93)],
    5: [(9, 28), (42, 44), (50, 94)],
    6: [(10, 28), (46, 94)],
    7: [(11, 27), (47, 94)],
    8: [(12, 26), (46, 94)],
    9: [(12, 26), (45, 90)],
    10: [(12, 30), (45, 88)],
    11: [(12, 30), (45, 86)],
    12: [(13, 30), (46, 84)],
    13: [(13, 27), (51, 63), (66, 84)],
    14: [(13, 23), (25, 28), (43, 62), (66, 79)],
    15: [(13, 22), (25, 30), (43, 62), (66, 76)],
    16: [(13, 31), (43, 62), (67, 75)],
    17: [(14, 19), (24, 34), (44, 61), (67, 74)],
    18: [(15, 19), (27, 39), (44, 57), (58, 62), (67, 74)],
    19: [(16, 21), (27, 39), (50, 61), (67, 67), (72, 78)],
    20: [(19, 23), (27, 39), (51, 58), (73, 79)],
    21: [(21, 24), (29, 39), (51, 58), (59, 61), (74, 78)],
    22: [(29, 38), (51, 57), (59, 61)],
    23: [(29, 37), (51, 57), (59, 61)],
    24: [(29, 35), (52, 56), (60, 61), (78, 89)],
    25: [(29, 35), (52, 55), (78, 89)],
    26: [(29, 33), (52, 55), (76, 89), (93, 95)],
    27: [(28, 31), (52, 55), (76, 88), (92, 95)],
    28: [(28, 30), (52, 55), (76, 87), (92, 94)],
    29: [(28, 30), (52, 54), (77, 86)],
    30: [(29, 30), (52, 54), (77, 85)],
}

# Map pins: (story, lon, lat, dx, dy). dx/dy nudge the pin (final px) away
# from a crowded true spot; a thin leader line points back to the true spot.
# Stories 35 (Mercury) and 37 (mini-moon) have no Earth spot - in space.
PINS = [
    (1, 30.7, 36.9, 0, 0), (2, 30.3, 50.8, -10, -8),
    (3, 20.1, 32.1, 0, 0), (4, -0.1, 51.5, 0, 0),
    (5, 4.35, 50.85, 12, -9), (6, 28.98, 41.0, 14, -8),
    (7, 30.06, -1.94, -12, -10), (8, 114.16, 22.32, 0, 0),
    (9, 77.2, 28.6, 0, 0), (10, 174.78, -41.29, 0, 0),
    (11, 106.8, -6.2, 0, 0), (12, 126.98, 37.57, 0, 0),
    (13, 106.1, -6.1, -13, 10), (14, 139.7, 35.7, 0, 0),
    (15, 50.6, 26.2, 0, 0), (16, 39.0, 22.8, 0, 0),
    (17, 34.45, 31.5, -12, 10), (18, 51.4, 35.7, 12, -8),
    (19, 35.5, 33.9, 16, -6), (20, 32.56, 15.5, 0, 0),
    (21, 28.19, -25.75, -12, 10), (22, 31.05, -17.83, 12, 10),
    (23, 35.74, -6.16, 0, 0), (24, -77.04, 38.9, 0, 0),
    (25, -77.04, 38.9, 13, -10), (26, -122.33, 47.6, 0, 0),
    (27, -115.14, 36.17, 0, 0), (28, -98.49, 29.42, 0, 0),
    (29, -47.88, -15.79, 0, 0), (30, -72.34, 18.54, 0, 0),
    (31, -58.38, -34.6, 0, 0), (32, -74.78, 10.96, 12, 9),
    (33, -159.77, -21.24, 0, 0), (34, 144.96, -37.81, 0, 0),
    (36, 6.14, 46.2, -12, 9), (38, 6.14, 46.2, 16, 6),
]

# Date-check traps: stories that are NOT 22 November. Left out on purpose.
DATECHECK = [
    "PERU M6.9 QUAKE - 20 NOV",
    "IRAN HIT ON KUWAIT BASE - 18 NOV",
    "BAHRAIN STRIKE ITSELF - 21 NOV",
    "'EL CHAPO ISIDRO' CAPTURED - 21 NOV",
    "FBI CRIME DATABASE HACK - 21 NOV",
    "ESTONIA BORDER SHUT ORDER - 21 NOV",
    "SHENZHEN SUMMIT - 20 NOV",
    "MAMDANI RIKERS PLAN - 20 NOV",
    "NIGERIA FUNERAL BOAT - 20 NOV",
    "ICJ MYANMAR GENOCIDE RULING - 19 NOV",
    "AI SELL-OFF, S AND P -3.7% - 20 NOV",
    "SOUTH AFRICA LOCAL ELECTIONS - 4 NOV",
    "CYCLONE AKVAN LANDFALL - 20 NOV",
    "PILOTLESS AIR TAXI, JAPAN - 20 NOV",
]

# ALSO ON: the 30 remaining numbered stories, one line each.
# (number, headline). Two columns of 15.
ALSO_ON = [
    ("04.", "THERESA MAY \"AGHAST\" AT EU REJOIN TALK; FIRMS WELCOME FOOD DEAL"),
    ("05.", "BELGIUM FACES TOTAL FLIGHT SHUTDOWN IN MONDAY STRIKE"),
    ("06.", "THOUSANDS MARCH IN ISTANBUL AS STATE SEIZES OPPOSITION TV"),
    ("07.", "FIVE EU STATES STRIKE RWANDA DEPORTATION CENTRES DEAL"),
    ("09.", "NEPAL PM SHAH IN DELHI FOR FIRST FOREIGN TRIP IN OFFICE"),
    ("11.", "EU AND INDONESIA SIGN TRADE DEAL AFTER 10 YEARS"),
    ("12.", "SOUTH KOREA EDUCATION MINISTER QUITS OVER AI CHEATING"),
    ("13.", "BANTEN FACTORY FIRE: 37 UNACCOUNTED FOR, OFFICIALS SAID"),
    ("14.", "SAUDIS TO TRIPLE CRUDE STORED IN JAPAN TO 24M BARRELS"),
    ("15.", "GULF CONDEMNS IRAN STRIKE ON BAHRAIN; RADAR CLAIM DISPUTED"),
    ("16.", "HOUTHIS SAY THEY HIT RABIGH REFINERY; DRONE INTERCEPTED"),
    ("17.", "TWO KILLED IN GAZA; SETTLERS TORCH HOMES NEAR RAMALLAH"),
    ("18.", "TRUMP DARES IRAN OVER BLOCKADE, DAY 130; RATIONING STARTS"),
    ("19.", "LEBANON MARKS INDEPENDENCE DAY, WARNS OF TWO OBSTACLES"),
    ("21.", "SOUTH AFRICA'S FIRST WOMAN DEPUTY PRESIDENT DIES AT 71"),
    ("22.", "ZIMBABWE AUTHOR CLEARED OF AI USE IN PRIZE STORY"),
    ("23.", "TANZANIA DRAW 2-2 WITH COSTA RICA ON U17 WORLD CUP DEBUT"),
    ("25.", "TRUMP ORDERS CONTRACTORS TO REPORT CONGRESS REQUESTS"),
    ("26.", "MASKED ICE AGENTS DETAIN TWO AT SEATTLE AIRPORT"),
    ("27.", "VERSTAPPEN WINS LAS VEGAS GP, THIRD WIN IN FOUR YEARS"),
    ("28.", "WEMBANYAMA 50 POINTS, HARDEN 51 IN SPURS WIN"),
    ("30.", "HAITI AND EL SALVADOR AGREE TO BUILD THREE PRISONS"),
    ("31.", "ARGENTINA APPROVES $50BN LNG EXPORT PROJECT"),
    ("32.", "BOCA WIN COPA SUDAMERICANA, FIRST TITLE IN 18 YEARS"),
    ("33.", "CYCLONE XAVIER WEAKENS NEAR COOK ISLANDS; ALL SAFE"),
    ("34.", "MOLLY MELDRUM, COUNTDOWN HOST, DIES AT 83"),
    ("35.", "BEPICOLOMBO ENTERS ORBIT AROUND MERCURY AFTER 8 YEARS"),
    ("36.", "UN AI WEAPONS TALKS END WITH NO BINDING RULES"),
    ("37.", "EARTH GAINS A NEW MINI-MOON, 2026 QQ8"),
    ("38.", "GUKESH DEFENDS WORLD CHESS TITLE IN GENEVA OPENER"),
]


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.buf = bytearray(bytes(PAPER) * (SW * SH))

    def _block(self, x, y, w, h, color):
        # Coordinates in 2048 space; clipped.
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(SW, x + w)
        y1 = min(SH, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * SW + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = row

    def rect(self, x, y, w, h, color):
        self._block(x * S, y * S, w * S, h * S, color)

    def border(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        X0, Y0, X1, Y1 = x0 * S, y0 * S, x1 * S, y1 * S
        T = max(2, t * S)
        dx = abs(X1 - X0)
        dy = -abs(Y1 - Y0)
        sx = 1 if X0 < X1 else -1
        sy = 1 if Y0 < Y1 else -1
        err = dx + dy
        while True:
            self._block(X0 - T // 2, Y0 - T // 2, T, T, color)
            if X0 == X1 and Y0 == Y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                X0 += sx
            if e2 <= dx:
                err += dx
                Y0 += sy

    def polyline(self, pts, color, t=1):
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, t)

    def circle(self, cx, cy, r, color):
        CX, CY, R = cx * S, cy * S, max(1, r * S)
        for dy in range(-R, R + 1):
            dx = int((R * R - dy * dy) ** 0.5)
            self._block(CX - dx, CY + dy, 2 * dx + 1, 1, color)

    def ellipse(self, cx, cy, rx, ry, color):
        CX, CY = cx * S, cy * S
        RX, RY = max(1, rx * S), max(1, ry * S)
        for dy in range(-RY, RY + 1):
            dx = int(RX * (1.0 - (dy * dy) / float(RY * RY)) ** 0.5)
            self._block(CX - dx, CY + dy, 2 * dx + 1, 1, color)

    def poly(self, pts, color):
        P = [(x * S, y * S) for x, y in pts]
        ys = [p[1] for p in P]
        y0, y1 = min(ys), max(ys)
        n = len(P)
        for yy in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x0, ya = P[i]
                x1, yb = P[(i + 1) % n]
                if (ya <= yy < yb) or (yb <= yy < ya):
                    t = (yy - ya) / float(yb - ya)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa = int(xs[i])
                xb = int(xs[i + 1])
                self._block(xa, yy, xb - xa + 1, 1, color)

    # ---- text ----
    def text_w(self, s, scale, spacing=1):
        s = norm(s)
        if not s:
            return 0
        return len(s) * (5 * scale + spacing) - spacing

    def text(self, x, y, s, scale, color, spacing=1, align="left"):
        s = norm(s)
        w = self.text_w(s, scale, spacing)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            if ch != " ":
                for gy in range(7):
                    row = g[gy]
                    for gx in range(5):
                        if row[gx] == "1":
                            self._block((cx + gx * scale) * S, (y + gy * scale) * S,
                                        scale * S, scale * S, color)
            cx += 5 * scale + spacing

    def wrap(self, s, max_w, scale, spacing=1, max_lines=None):
        words = norm(s).split(" ")
        lines = []
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_w(trial, scale, spacing) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines]
            while lines and self.text_w(lines[-1] + "...", scale, spacing) > max_w:
                lines[-1] = lines[-1][:-1]
            lines[-1] = lines[-1] + "..."
        return lines

    def downsample(self):
        rows = []
        buf = self.buf
        for oy in range(H):
            base0 = (oy * 2) * SW * 3
            base1 = base0 + SW * 3
            out = bytearray(W * 3)
            for ox in range(W):
                i0 = base0 + ox * 6
                i1 = base1 + ox * 6
                o = ox * 3
                out[o] = (buf[i0] + buf[i0 + 3] + buf[i1] + buf[i1 + 3] + 2) // 4
                out[o + 1] = (buf[i0 + 1] + buf[i0 + 4] + buf[i1 + 1] + buf[i1 + 4] + 2) // 4
                out[o + 2] = (buf[i0 + 2] + buf[i0 + 5] + buf[i1 + 2] + buf[i1 + 5] + 2) // 4
            rows.append(bytes(out))
        return rows


# ---------------------------------------------------------------- scenes
def scene_cop31(cv, x, y, w, h):
    cv.rect(x, y, w, h, (36, 48, 70))
    cv.rect(x, y + h - 18, w, 18, (22, 30, 46))
    flags = [(178, 32, 28), (31, 78, 160), (220, 170, 20), (34, 139, 92)]
    for i, fc in enumerate(flags):
        cv.rect(x + 12 + i * 16, y + 6, 9, 12, fc)
        cv.rect(x + w - 21 - i * 16, y + 6, 9, 12, fc)
    cv.rect(x + w // 2 - 62, y + 10, 124, 30, (12, 16, 26))
    cv.border(x + w // 2 - 62, y + 10, 124, 30, RED, 2)
    cv.text(x + w // 2, y + 17, "NO DEAL", 2, WHITE, spacing=1, align="center")
    cv.rect(x + w // 2 - 11, y + 44, 22, 50, (150, 30, 26))
    for r in (46, 62, 78):
        for k in range(9):
            if k == 4:
                continue
            cv.rect(x + 14 + k * 32, y + r, 20, 12, (96, 106, 128))
            cv.rect(x + 14 + k * 32, y + r + 9, 20, 3, (70, 78, 100))
    cv.rect(x + w // 2 - 16, y + 82, 32, 12, (96, 72, 36))
    cv.line(x + w // 2 + 6, y + 82, x + w // 2 + 12, y + 70, INK, 1)
    cv.circle(x + w // 2 + 12, y + 70, 2, INK)


def scene_dymer(cv, x, y, w, h):
    cv.rect(x, y, w, h, (10, 16, 38))
    stars = [(0.08, 0.12), (0.20, 0.07), (0.35, 0.15), (0.50, 0.06), (0.66, 0.12),
             (0.80, 0.08), (0.92, 0.16), (0.45, 0.20), (0.60, 0.22), (0.28, 0.24)]
    for fx, fy in stars:
        cv.rect(x + int(w * fx), y + int(h * fy), 2, 2, (220, 220, 230))
    cv.circle(x + int(w * 0.85), y + int(h * 0.20), 9, (232, 228, 200))
    heights = [46, 62, 40, 74, 52, 66, 44]
    bx = x + 6
    for i, bh in enumerate(heights):
        if i == 3:
            bx += 40
            continue
        cv.rect(bx, y + h - bh, 36, bh, (18, 24, 46))
        for wy in range(y + h - bh + 6, y + h - 6, 10):
            for wx in range(bx + 6, bx + 32, 10):
                if (wx * 7 + wy * 13) % 29 < 12:
                    cv.rect(wx, wy, 3, 4, (240, 200, 90))
        bx += 40
    # Damaged block, leaning, burning (4th building slot).
    dbx = x + 6 + 3 * 40
    cv.poly([(dbx, y + h), (dbx + 4, y + h - 74), (dbx + 30, y + h - 66),
             (dbx + 36, y + h)], (24, 20, 34))
    cv.circle(dbx + 16, y + h - 68, 12, (240, 120, 30))
    cv.circle(dbx + 20, y + h - 72, 7, (250, 200, 60))
    cv.circle(dbx + 12, y + h - 84, 9, (90, 90, 96))
    cv.circle(dbx + 20, y + h - 96, 11, (110, 110, 116))
    # Drone arcs converging on the block.
    cv.polyline([(x + 30, y + 12), (x + 90, y + 30), (x + 138, y + 46)],
                (205, 205, 215), 1)
    cv.polyline([(x + 292, y + 10), (x + 222, y + 26), (x + 168, y + 44)],
                (205, 205, 215), 1)
    for dx, dy in ((138, 46), (168, 44)):
        cv.line(x + dx - 4, y + dy - 4, x + dx + 4, y + dy + 4, (230, 230, 235), 1)
        cv.line(x + dx - 4, y + dy + 4, x + dx + 4, y + dy - 4, (230, 230, 235), 1)


def scene_benghazi(cv, x, y, w, h):
    bands = [(52, 38, 66), (120, 62, 70), (198, 110, 62), (232, 150, 80)]
    bh = [13, 13, 12, 12]
    yy = y
    for bc, b in zip(bands, bh):
        cv.rect(x, yy, w, b, bc)
        yy += b
    cv.circle(x + int(w * 0.72), y + 30, 12, (240, 170, 80))
    cv.rect(x, y + 50, w, h - 50, (14, 40, 66))
    for wy in (58, 72, 88, 102):
        for wx in range(x + 8, x + w - 20, 26):
            cv.line(wx, y + wy, wx + 14, y + wy, (120, 160, 200), 1)
    cv.poly([(x + 70, y + 80), (x + 205, y + 72), (x + 222, y + 82),
             (x + 198, y + 94), (x + 92, y + 97)], (16, 18, 24))
    cv.line(x + 150, y + 72, x + 148, y + 44, (16, 18, 24), 2)
    cv.line(x + 138, y + 52, x + 162, y + 50, (16, 18, 24), 1)
    cv.circle(x + 120, y + 68, 10, (240, 120, 30))
    cv.circle(x + 133, y + 71, 7, (250, 200, 60))
    cv.circle(x + 185, y + 66, 8, (230, 100, 30))
    cv.circle(x + 118, y + 52, 9, (90, 90, 96))
    cv.circle(x + 128, y + 40, 11, (110, 110, 116))
    cv.circle(x + 142, y + 28, 12, (130, 130, 136))
    cv.rect(x + 252, y + 64, 34, 8, (20, 24, 34))
    cv.line(x + 266, y + 64, x + 266, y + 52, (20, 24, 34), 2)
    cv.circle(x + 266, y + 48, 4, (120, 120, 126))


def motif_hk(cv, x, y, w, h):
    cv.rect(x, y, w, h, (198, 208, 220))
    heights = [30, 44, 36, 50, 28, 40]
    bx = x + 8
    for bh in heights:
        cv.rect(bx, y + h - bh, 24, bh, (52, 62, 82))
        bx += 28
    cv.rect(x + w - 52, y + h - 26, 34, 22, WHITE)
    cv.border(x + w - 52, y + h - 26, 34, 22, RED, 2)
    cv.rect(x + w - 46, y + h - 22, 22, 3, RED)
    cv.line(x + w - 44, y + h - 10, x + w - 38, y + h - 5, RED, 2)
    cv.line(x + w - 38, y + h - 5, x + w - 30, y + h - 16, RED, 2)


def motif_cricket(cv, x, y, w, h):
    cv.rect(x, y, w, 18, (170, 195, 175))
    cv.rect(x, y + 18, w, h - 18, (52, 128, 66))
    for k in range(3):
        cv.rect(x + 30 + k * 6, y + h - 30, 3, 12, WHITE)
    cv.poly([(x + 58, y + h - 8), (x + 66, y + h - 8), (x + 78, y + h - 34),
             (x + 72, y + h - 38)], (150, 110, 60))
    cv.circle(x + 96, y + h - 20, 5, (178, 32, 28))
    cv.rect(x + w - 58, y + 6, 52, 16, (20, 30, 40))
    cv.text(x + w - 32, y + 9, "720/9", 1, WHITE, spacing=1, align="center")


def motif_house(cv, x, y, w, h):
    cv.rect(x, y, w, h, (208, 212, 218))
    cx = x + w // 2
    pts = []
    for k in range(13):
        a = math.pi * (1 - k / 12.0)
        pts.append((int(cx + 30 * math.cos(a)), int(y + h - 38 - 16 * math.sin(a))))
    cv.poly(pts + [(cx + 30, y + h - 38), (cx - 30, y + h - 38)], (150, 154, 160))
    cv.line(cx, y + h - 54, cx, y + h - 64, INK, 1)
    cv.rect(cx, y + h - 64, 12, 7, RED)
    cv.rect(x + 28, y + h - 38, w - 56, 6, (120, 124, 130))
    for k in range(5):
        cv.rect(x + 34 + k * 28, y + h - 32, 6, 18, WHITE)
    cv.rect(x + 20, y + h - 16, w - 40, 12, (120, 124, 130))


def motif_hospital(cv, x, y, w, h):
    cv.rect(x, y, w, h, (218, 224, 230))
    cv.rect(x + 30, y + 8, w - 60, h - 20, WHITE)
    cv.border(x + 30, y + 8, w - 60, h - 20, (120, 124, 130), 1)
    cx = x + w // 2
    cv.rect(cx - 4, y + 14, 8, 20, RED)
    cv.rect(cx - 10, y + 20, 20, 8, RED)
    cv.rect(cx - 8, y + h - 16, 16, 12, (120, 124, 130))
    cv.rect(x, y + h - 8, w, 8, (0, 140, 70))
    cv.poly([(cx, y + h - 7), (cx + 10, y + h - 4), (cx, y + h - 1),
             (cx - 10, y + h - 4)], (240, 200, 40))


def motif_sudan(cv, x, y, w, h):
    cv.rect(x, y, w, 22, (190, 130, 80))
    cv.rect(x, y + 22, w, h - 22, (232, 190, 130))
    heights = [24, 34, 28, 40]
    bx = x + 10
    for bh in heights:
        cv.rect(bx, y + h - bh, 30, bh, (50, 45, 60))
        bx += 36
    cv.polyline([(x + 130, y + 16), (x + 110, y + 30), (x + 90, y + 40)],
                (90, 80, 90), 1)
    cv.line(x + 126, y + 10, x + 134, y + 18, (40, 35, 45), 1)
    cv.line(x + 126, y + 18, x + 134, y + 10, (40, 35, 45), 1)
    cv.rect(x + 150, y + 30, 20, 12, (60, 110, 200))
    cv.circle(x + 160, y + 36, 3, WHITE)


# ---------------------------------------------------------------- panels
LEADS = [
    {"n": 1, "scene": scene_cop31, "kicker": "01 - EUROPE - CLIMATE",
     "head": "COP31 ENDS WITH NO DEAL",
     "sum": "TWO DAYS OVERTIME, THE LONGEST COP ON RECORD. ABOUT 130 PARTIES "
            "REJECT THE DRAFT PACT. NO CONSENSUS, SAYS KURUM."},
    {"n": 2, "scene": scene_dymer, "kicker": "02 - EUROPE - WAR IN UKRAINE",
     "head": "186 DRONES, A BLOCK FLATTENED IN DYMER",
     "sum": "161 OF 186 DRONES SHOT DOWN. A DRONE PARTLY DESTROYS A BLOCK IN "
            "DYMER, NORTH OF KYIV. AT LEAST 3 KILLED, 14 MISSING."},
    {"n": 3, "scene": scene_benghazi, "kicker": "03 - EUROPE - WAR AT SEA",
     "head": "WARSHIP MERKURY SUNK OFF BENGHAZI",
     "sum": "SEA DRONES HIT THE CORVETTE IN THE EARLY HOURS. SATELLITES SHOW "
            "HER CAPSIZED AND SUNK. A SECOND SHIP, ASCALON, ALSO HIT."},
]

SECONDARY = [
    {"n": 8, "scene": motif_hk, "kicker": "08 - ASIA",
     "head": "RECORD TURNOUT IN HONG KONG",
     "sum": "ABOUT 5,700 VOTERS PICK THE COLLEGE THAT CHOOSES THE CITY'S LEADER."},
    {"n": 10, "scene": motif_cricket, "kicker": "10 - ASIA",
     "head": "INDIA'S 720/9 RECORD IN NZ",
     "sum": "PANT 128, RAHUL 136 AS INDIA DECLARE. NZ 119/2, STILL TRAIL BY 233."},
    {"n": 24, "scene": motif_house, "kicker": "24 - NORTH AMERICA",
     "head": "DEMOCRATS TAKE THE HOUSE, 258",
     "sum": "RECOUNT WIN IN NORTH CAROLINA SEALS THE LARGEST MAJORITY SINCE 1992."},
    {"n": 29, "scene": motif_hospital, "kicker": "29 - LATIN AMERICA",
     "head": "BOLSONARO STABLE IN ICU",
     "sum": "HOSPITAL SAYS THE FORMER PRESIDENT IS STABLE IN ICU SINCE FRIDAY."},
    {"n": 20, "scene": motif_sudan, "kicker": "20 - AFRICA",
     "head": "DRONE STRIKES HIT KHARTOUM",
     "sum": "DRONE STRIKES DAMAGE HOMES AND A UN BUILDING IN KHARTOUM EARLY SUNDAY."},
]


def lead_panel(cv, x, y, w, h, st):
    cv.rect(x, y, w, h, PANEL)
    cv.border(x, y, w, h, INK, 1)
    st["scene"](cv, x, y, w, 112)
    cv.rect(x + 6, y + 6, 24, 18, RED)
    cv.text(x + 18, y + 10, str(st["n"]), 2, WHITE, spacing=1, align="center")
    cv.text(x + 10, y + 122, st["kicker"], 1, RED, spacing=1)
    hy = y + 136
    for ln in cv.wrap(st["head"], 294, 2, 1, 2):
        cv.text(x + 10, hy, ln, 2, INK, spacing=1)
        hy += 16
    sy = y + 172
    for ln in cv.wrap(st["sum"], 294, 1, 1, 3):
        cv.text(x + 10, sy, ln, 1, SOFT, spacing=1)
        sy += 9


def secondary_panel(cv, x, y, w, h, st):
    cv.rect(x, y, w, h, PANEL)
    cv.border(x, y, w, h, INK, 1)
    st["scene"](cv, x, y, w, 56)
    cv.rect(x + 5, y + 5, 18, 14, RED)
    cv.text(x + 14, y + 8, str(st["n"]), 1, WHITE, spacing=1, align="center")
    cv.text(x + 8, y + 62, st["kicker"], 1, RED, spacing=1)
    hy = y + 74
    for ln in cv.wrap(st["head"], 172, 2, 0, 2):
        cv.text(x + 8, hy, ln, 2, INK, spacing=0)
        hy += 16
    sy = y + 108
    for ln in cv.wrap(st["sum"], 172, 1, 1, 3):
        cv.text(x + 8, sy, ln, 1, SOFT, spacing=1)
        sy += 9


# ---------------------------------------------------------------- page
def draw_page(cv):
    # Masthead.
    cv.text(512, 14, "THE WORLD IN ONE DAY", 2, RED, spacing=2, align="center")
    cv.text(512, 34, "SUNDAY 22 NOVEMBER 2026", 7, INK, spacing=1, align="center")
    cv.rect(32, 90, 960, 2, INK)
    cv.text(512, 96, "COP31 ENDS WITH NO DEAL AFTER TWO DAYS OVERTIME - 186 DRONES",
            2, INK, spacing=1, align="center")
    cv.text(512, 112, "RAIN ON UKRAINE - RUSSIAN WARSHIP MERKURY SUNK OFF BENGHAZI",
            2, INK, spacing=1, align="center")
    cv.text(512, 130, "38 STORIES - 8 REGIONS - ONE DAY", 1, SOFT, spacing=1,
            align="center")
    cv.rect(32, 143, 960, 1, RULE)

    # Numbers strip: 6 boxes, red top rule, big figure, two label lines.
    for i, (num, l1, l2) in enumerate(NUMBERS):
        bx = 32 + i * 161
        cv.rect(bx, 150, 153, 64, PANEL)
        cv.border(bx, 150, 153, 64, INK, 1)
        cv.rect(bx, 150, 153, 3, RED)
        cv.text(bx + 76, 160, num, 4, INK, spacing=1, align="center")
        cv.text(bx + 76, 192, l1, 1, SOFT, spacing=1, align="center")
        cv.text(bx + 76, 201, l2, 1, SOFT, spacing=1, align="center")

    # Region bar: 8 segments proportional to story counts, plus legend.
    total_w = 960
    acc = 0
    rx = 32
    for i, (name, cnt, col) in enumerate(REGIONS):
        if i < len(REGIONS) - 1:
            wseg = round(total_w * cnt / 38.0)
        else:
            wseg = total_w - acc
        acc += wseg
        cv.rect(rx, 222, wseg, 22, col)
        cv.text(rx + wseg // 2, 229, str(cnt), 1, WHITE, spacing=1, align="center")
        rx += wseg
    items = []
    tot = 0
    for name, cnt, col in REGIONS:
        label = "%s %d" % (name, cnt)
        wl = cv.text_w(label, 1, 1)
        items.append((label, col, wl))
        tot += 14 + wl
    tot += 12 * (len(REGIONS) - 1)
    lx = (1024 - tot) // 2
    for label, col, wl in items:
        cv.rect(lx, 250, 10, 10, col)
        cv.text(lx + 14, 251, label, 1, INK, spacing=1)
        lx += 14 + wl + 12

    # Lead panels.
    for i, st in enumerate(LEADS):
        lead_panel(cv, 32 + i * 325, 264, 310, 210, st)

    # Secondary row.
    for i, st in enumerate(SECONDARY):
        secondary_panel(cv, 32 + i * 194, 482, 184, 150, st)

    # World dot-map with numbered pins.
    cv.text(32, 640, "THE WORLD, NUMBERED - PINS 1-34, 36, 38. 35 AND 37 ARE IN SPACE.",
            1, INK, spacing=1)
    mx, my, mw, mh = 32, 652, 620, 156
    cv.rect(mx, my, mw, mh, OCEAN)
    cv.border(mx, my, mw, mh, INK, 1)
    cw = mw / 96.0
    rh = mh / 37.0
    for r, spans in LAND.items():
        cy = int(my + (r + 0.5) * rh)
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx = int(mx + (c + 0.5) * cw)
                cv.circle(cx, cy, 2, DOT)

    def pin_xy(lon, lat):
        return (mx + (lon + 180.0) / 360.0 * mw,
                my + (90.0 - lat) / 180.0 * mh)

    for n, lon, lat, dx, dy in PINS:
        px, py = pin_xy(lon, lat)
        qx, qy = int(px + dx), int(py + dy)
        if dx or dy:
            cv.line(int(px), int(py), qx, qy, RED, 1)
            cv.circle(int(px), int(py), 2, RED)
        col = REGION_COLOR[region_of(n)]
        cv.circle(qx, qy, 7, WHITE)
        cv.circle(qx, qy, 6, col)
        cv.text(qx, qy - 3, str(n), 1, WHITE, spacing=1, align="center")

    # Date-check box: traps that are NOT 22 November.
    dx0, dy0, dw, dh = 668, 640, 324, 168
    cv.rect(dx0, dy0, dw, dh, PANEL)
    cv.border(dx0, dy0, dw, dh, RED, 2)
    cv.rect(dx0, dy0, dw, 22, RED)
    cv.text(dx0 + 10, dy0 + 7, "DATE CHECK - LEFT OUT ON PURPOSE", 1, WHITE, spacing=1)
    iy = dy0 + 28
    for item in DATECHECK:
        cv.text(dx0 + 10, iy, "X", 1, RED, spacing=1)
        cv.text(dx0 + 22, iy, item, 1, INK, spacing=1)
        iy += 9
    cv.text(dx0 + 10, dy0 + 156, "THEY HAPPENED ON OTHER DAYS.", 1, RED, spacing=1)

    # ALSO ON: the other 30 stories, one line each, two columns.
    cv.text(32, 816, "ALSO ON - THE OTHER 30 STORIES", 2, INK, spacing=1)
    cv.rect(442, 822, 550, 1, RULE)
    for i, (num, head) in enumerate(ALSO_ON):
        col = i // 15
        row = i % 15
        ex = 32 + col * 488
        ey = 834 + row * 9
        cv.text(ex, ey, num, 1, RED, spacing=1)
        cv.text(ex + cv.text_w(num + " ", 1, 1), ey, head, 1, INK, spacing=1)

    # Footer.
    cv.rect(32, 974, 960, 1, RULE)
    cv.text(512, 980, "EVERY STORY HERE HAPPENED OR WAS FIRST REPORTED ON SUNDAY "
                      "22 NOVEMBER 2026.", 1, INK, spacing=1, align="center")
    cv.text(512, 990, "SOURCES: BBC, REUTERS, AP, CNN, GUARDIAN AND OTHERS - "
                      "38 STORIES, 8 REGIONS.", 1, SOFT, spacing=1, align="center")


# ---------------------------------------------------------------- png
def png_bytes(rows):
    raw = b"".join(b"\x00" + r for r in rows)
    comp = zlib.compress(raw, 9)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    cv = Canvas()
    draw_page(cv)
    data = png_bytes(cv.downsample())
    with open(out_path, "wb") as f:
        f.write(data)
    print("WROTE %s %d bytes sha256=%s" %
          (out_path, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
