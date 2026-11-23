#!/usr/bin/env python3
# This program draws the world-news front page for 22 November 2026.
"""Sunday 22 November 2026 - one-day world news front page.

Draws a 1024x1024 PNG newspaper front page summing up Sunday
22 November 2026: masthead, 3 drawn lead panels, a numbers strip,
a region bar, the full 38-story list, a dot-matrix world map,
an ALSO ON list, a red DATE CHECK box and a footer.

Python 3.13 standard library only. No network, no third-party
imports, no wall clock, no unseeded randomness: two runs write
byte-identical files.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

CREAM = (247, 242, 231)
PAPER = (255, 253, 247)
INK = (22, 22, 22)
RED = (172, 28, 28)
NAVY = (30, 50, 110)
GREY = (120, 114, 102)
WHITE = (255, 255, 255)
SKY = (168, 198, 224)
SEA = (28, 72, 122)
NIGHT = (14, 22, 52)
DARK = (30, 35, 70)
GOLD = (240, 200, 80)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, one string per row, "1" = ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
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
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
}

BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.pixels = bytearray(bytes(CREAM) * (W * H))

    def px(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.pixels[i:i + len(row)] = row

    def hline(self, x1, y, x2, color):
        if x2 < x1:
            x1, x2 = x2, x1
        self.fill_rect(x1, y, x2 - x1 + 1, 1, color)

    def vline(self, x, y1, y2, color):
        if y2 < y1:
            y1, y2 = y2, y1
        self.fill_rect(x, y1, 1, y2 - y1 + 1, color)

    def rect_outline(self, x, y, w, h, color, t=1):
        for k in range(t):
            self.hline(x + k, y + k, x + w - 1 - k, color)
            self.hline(x + k, y + h - 1 - k, x + w - 1 - k, color)
            self.vline(x + k, y + k, y + h - 1 - k, color)
            self.vline(x + w - 1 - k, y + k, y + h - 1 - k, color)

    def line(self, x1, y1, x2, y2, color):
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        x, y = x1, y1
        while True:
            self.px(x, y, color)
            if x == x2 and y == y2:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle_fill(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = math.isqrt(max(0, r * r - dy * dy))
            self.hline(cx - dx, cy + dy, cx + dx, color)

    def arc_up(self, cx, cy, r, color):
        # Upper half of a circle outline, integer math, deterministic.
        for x in range(cx - r, cx + r + 1):
            dx = x - cx
            dy = math.isqrt(max(0, r * r - dx * dx))
            self.px(x, cy - dy, color)

    def triangle_fill(self, p1, p2, p3, color):
        pts = sorted([p1, p2, p3], key=lambda p: p[1])
        (x1, y1), (x2, y2), (x3, y3) = pts

        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) // (yb - ya)

        for y in range(y1, y3 + 1):
            if y < y2:
                xa = edge_x(x1, y1, x2, y2, y)
                xb = edge_x(x1, y1, x3, y3, y)
            else:
                xa = edge_x(x2, y2, x3, y3, y)
                xb = edge_x(x1, y1, x3, y3, y)
            if xa > xb:
                xa, xb = xb, xa
            self.hline(xa, y, xb, color)

    # ---- text ----
    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale

    def text_centered(self, cx, y, s, scale, color):
        x = cx - self.text_width(s, scale) // 2
        return self.text(x, y, s, scale, color)


def wrap(text, width):
    """Greedy word wrap to lines of at most `width` characters."""
    lines = []
    cur = ""
    for word in text.split(" "):
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= width:
            cur = cur + " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- png
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += canvas.pixels[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# ---------------------------------------------------------------- data
# (number, city, summary) - every story happened or was first reported
# on Sunday 22 November 2026. Disputed figures printed only as the
# verified log instructs (attributed ranges, no invented precision).
STORIES = [
    (1, "ANTALYA", "COP31 ends with NO deal, two days overtime, the longest climate summit on record. Draft pact rejected for omitting fossil fuels. (CNN, BBC)"),
    (2, "DYMER", "Russia launches 186 drones overnight; 161 shot down. A drone partly destroys a 5-storey block; at least 3 killed, 14 missing. (AP, BBC)"),
    (3, "BENGHAZI", "Russian corvette Merkury hit by sea drones, capsizes and sinks at Benghazi naval base. Cargo ship Ascalon also hit. (WSJ, BBC)"),
    (4, "UK", "Ex-PM Theresa May is aghast PM Andy Burnham may consider rejoining the EU; UK firms welcome the EU food deal. (GUARDIAN, ANSA)"),
    (5, "BELGIUM", "Air traffic controllers join Monday's national strike; all flights in Belgium expected to be cancelled. (STRAITS TIMES)"),
    (6, "ISTANBUL", "Thousands march after the state takes control of opposition media including Sozcu TV. (LE MONDE, TAGESSCHAU)"),
    (7, "EU-RWANDA", "Five EU countries strike a deal with Rwanda on deportation centres. (EL PAIS)"),
    (8, "HONG KONG", "Election Committee vote draws record turnout; about 5,700 voters choose the college that picks the city leader. (SCMP)"),
    (9, "NEW DELHI", "Nepal PM Balendra Shah arrives for a 2-day state visit, his first foreign trip since March; talks with Modi on Monday. (IANS)"),
    (10, "WELLINGTON", "India declare 720/9, the highest Test total ever in New Zealand. Pant 128, Rahul 136; NZ 119/2, trail by 233. (CRICBUZZ)"),
    (11, "EU-INDONESIA", "EU and Indonesia sign a trade deal after 10 years; it removes 98.5% of tariffs on EU goods. (EURONEWS, THE HINDU)"),
    (12, "SEOUL", "Education minister Choi Kyo-jin resigns over an AI cheating scandal in a tax exam. (BBC, GUARDIAN, YONHAP)"),
    (13, "BANTEN", "Rescuers search a candy factory after Saturday's blaze; 3 dead, 37 unaccounted for, officials said. (AP, REUTERS)"),
    (14, "TOKYO", "Saudi Arabia agrees to triple crude stored in Japan to 24 million barrels. (JAPAN TODAY)"),
    (15, "BAHRAIN/GULF", "Iran's Bahrain strike is condemned by Saudi Arabia, Qatar and the UAE; Tehran says two Patriot radars were hit, a claim the Gulf side rejects. (MEE, FRANCE 24)"),
    (16, "RABIGH", "Houthis say they hit the Rabigh oil refinery; the coalition says it intercepted a drone and a missile. (STRAITS TIMES, MEE)"),
    (17, "GAZA", "Israeli fire kills 2 Palestinians in Gaza; a drone strike near Deir al-Balah kills 1. Settlers torch vehicles near Ramallah. (FRANCE 24)"),
    (18, "IRAN", "Trump dares Iran to break the US port blockade, day 130; Iran starts scheduled power rationing. (FOX NEWS, CBS)"),
    (19, "BEIRUT", "President Aoun says Israeli occupation and Iranian interference are two linked obstacles to independence. (AL JAZEERA, MEE)"),
    (20, "KHARTOUM", "Drone strikes damage homes and a UN building; the army accuses Ethiopia; RSF strikes kill civilians. (FRANCE 24, LE MONDE)"),
    (21, "SOUTH AFRICA", "Phumzile Mlambo-Ngcuka, first woman deputy president and ex-UN Women head, dies at 71. (ALLAFRICA)"),
    (22, "ZIMBABWE", "Author Simbarashe Kundizeza cleared of using AI for his prize-winning story. (AFRICANEWS)"),
    (23, "DOHA", "Tanzania draw 2-2 with Costa Rica at the U17 World Cup in Doha, on their debut. (AFRICANEWS)"),
    (24, "US HOUSE", "Democrats secure at least 258 House seats after a recount win in North Carolina, the largest majority since 1992. (BBC, GUARDIAN)"),
    (25, "WASHINGTON", "Trump orders federal contractors to tell the White House of any congressional requests. (GUARDIAN, UPI)"),
    (26, "SEATTLE", "Video shows masked ICE agents detaining two people at Seattle-Tacoma airport. (AL JAZEERA, UPI)"),
    (27, "LAS VEGAS", "Max Verstappen wins the Las Vegas Grand Prix, his third win there in four years. (CBC SPORTS)"),
    (28, "NBA", "Wembanyama scores 50 points and 19 rebounds as the Spurs beat the Pelicans 114-91; Harden scores 51. (BBC SPORT)"),
    (29, "BRASILIA", "Ex-president Bolsonaro remains stable in intensive care, the hospital said Sunday. (LA NACION, ANSA)"),
    (30, "HAITI", "Haiti and El Salvador agree to build three prisons after Salvadoran troops were sent. (LA NACION, GUARDIAN)"),
    (31, "BUENOS AIRES", "Argentina approves a $50 billion LNG export project. (OILPRICE)"),
    (32, "BARRANQUILLA", "Boca Juniors beat Atletico Mineiro 2-0 to win the Copa Sudamericana, their first trophy in 18 years. (BUENOS AIRES TIMES)"),
    (33, "COOK ISLANDS", "Cyclone Xavier weakens near the Cook Islands; everyone on Nassau is safe, the PM says. (RNZ PACIFIC)"),
    (34, "AUSTRALIA", "Molly Meldrum, the broadcaster who hosted Countdown, dies at 83. (GUARDIAN)"),
    (35, "MERCURY", "Probe BepiColombo enters orbit around Mercury after an 8-year journey; the second craft ever to do so. (BBC SCIENCE)"),
    (36, "GENEVA", "UN talks on AI weapons end with no binding rules; the Red Cross warns time to regulate is running out. (CBC, GUARDIAN)"),
    (37, "SPACE", "Earth gets a new mini-moon, 2026 QQ8, found in August and temporarily orbiting Earth. (BBC)"),
    (38, "GENEVA", "India's Gukesh defends his world title against Uzbekistan's Sindarov; the match opens in Geneva. (AL JAZEERA)"),
]

NUMBERS = [
    ("186", "DRONES LAUNCHED AT UKRAINE", "161 SHOT DOWN"),
    ("258", "DEMOCRAT HOUSE SEATS", "LARGEST SINCE 1992"),
    ("720/9", "INDIA TOTAL AT WELLINGTON", "TEST RECORD IN NZ"),
    ("37", "WORKERS STILL MISSING", "BANTEN FACTORY FIRE"),
    ("$50BN", "ARGENTINA LNG PROJECT", "APPROVED"),
    ("130", "DAYS OF US BLOCKADE", "OF IRAN"),
]

REGION_BAR = ("EUROPE 7 - ASIA 7 - MIDDLE EAST 5 - AFRICA 4 - "
              "NORTH AMERICA 5 - LATIN AMERICA 4 - OCEANIA 2 - GLOBAL 4")

ALSO_ON = [
    "CRISPR GENE THERAPY CUTS CHOLESTEROL 52%",
    "BRENT CRUDE NEAR $90 A BARREL",
    "ALCARAZ WINS FIRST ATP FINALS TITLE",
    "MARQUEZ TIES AGOSTINI WITH 8TH MOTOGP TITLE",
    "KC CURRENT WIN FIRST NWSL TITLE 2-1",
    "SKUBAL AGREES $450M, 9-YEAR METS DEAL",
    "MILEY CYRUS MARRIES MAXX MORANDO",
    "FRANCE REACH NATIONS FINAL, BEAT ARGENTINA 45-17",
    "SHURI CASTLE MAIN HALL RESTORED AFTER FIRE",
    "MONGOLIA FACES SNAP PRESIDENTIAL VOTE",
    "BASRA: FIRE AT HARTHA POWER STATION KILLS 4",
    "BANGLADESH GARMENT WORKERS CLASH WITH POLICE",
    "UK TO HOST 2035 WOMEN'S WORLD CUP",
    "LEEDS WIN AT CHELSEA 4-1, FIRST SINCE 1999",
]

DATE_CHECK = [
    "PERU M6.9 QUAKE - STRUCK FRI 20 NOV, REPORTED 21 NOV",
    "IRAN STRIKE ON US BASE IN KUWAIT - WED 18 NOV",
    "BAHRAIN STRIKE ITSELF - SAT 21 NOV (SUNDAY: CONDEMNATIONS ONLY)",
    "EL CHAPO ISIDRO CAPTURED - SAT 21 NOV",
    "FBI CRIME DATABASE HACK - FIRST REPORTED 21 NOV",
    "ESTONIA ORDERS RUSSIA BORDER SHUT - ANNOUNCED 21 NOV",
    "SHENZHEN TRUMP-XI-PUTIN SUMMIT - 20 NOV",
    "MAMDANI'S RIKERS CLOSURE PLAN - FRI 20 NOV",
    "NIGERIA FUNERAL BOAT - CAPSIZED FRI 20 NOV",
    "ICJ: MYANMAR GENOCIDE RULING - 19 NOV",
    "AI SELL-OFF, S&P 500 -3.7% - FRI 20 NOV CLOSE",
    "SOUTH AFRICA LOCAL ELECTIONS - VOTED 4 NOV",
    "CYCLONE AKVAN LANDFALL - 20 NOV",
    "PILOTLESS AIR TAXI FLIGHT IN JAPAN - 20 NOV",
]

# World map: 48 columns x 24 rows, land cells as (col_start, col_end)
# pairs per row. Lon step 7.5 deg, lat step 6.25 deg.
MAP_ROWS = {
    1: [(5, 8), (17, 20)],
    2: [(2, 13), (16, 21), (30, 47)],
    3: [(3, 14), (24, 47)],
    4: [(3, 15), (23, 47)],
    5: [(4, 15), (23, 46)],
    6: [(5, 15), (23, 44)],
    7: [(5, 15), (22, 28), (34, 43)],
    8: [(6, 14), (22, 28), (29, 32), (34, 41)],
    9: [(6, 13), (22, 30), (31, 35), (36, 40)],
    10: [(7, 12), (22, 31), (33, 35), (37, 39)],
    11: [(9, 12), (22, 31), (33, 35), (37, 39)],
    12: [(10, 12), (22, 27), (28, 31), (37, 38)],
    13: [(13, 18), (23, 31), (37, 41)],
    14: [(13, 18), (24, 31), (37, 42)],
    15: [(13, 18), (25, 30), (38, 43)],
    16: [(13, 18), (25, 29), (40, 44)],
    17: [(14, 18), (26, 29), (39, 44)],
    18: [(14, 17), (26, 28), (39, 44)],
    19: [(14, 16), (26, 28), (40, 43)],
    20: [(14, 15), (40, 42), (46, 47)],
    21: [(14, 15), (46, 46)],
    22: [(14, 14)],
}

# (label, col, row, dx, dy) - numbered pins for the 3 leads, dots for others.
PINS = [
    ("1", 28, 6, 0, -3),    # Dymer
    ("2", 28, 8, 3, 3),     # Antalya (COP31)
    ("3", 27, 9, -3, 1),    # Benghazi
    ("", 39, 11, 0, 0),     # Hong Kong
    ("", 38, 15, 0, 0),     # Banten
    ("", 47, 21, 0, 0),     # Wellington
    ("", 25, 7, 0, 0),      # Geneva
    ("", 9, 9, 0, 0),       # Las Vegas
    ("", 18, 17, 0, 0),     # Brasilia
]


# ---------------------------------------------------------------- scenes
def draw_cop31(c, sx, sy, sw, sh):
    c.fill_rect(sx, sy, sw, sh, (206, 222, 232))
    c.fill_rect(sx, sy, sw, 24, (38, 58, 110))
    c.text_centered(sx + sw // 2, sy + 8, "COP31 - ANTALYA", 1, WHITE)
    flag_colors = [(172, 28, 28), (30, 80, 160), (40, 140, 60),
                   (220, 170, 30), (200, 90, 20), (120, 60, 140),
                   (20, 140, 140)]
    for i, col in enumerate(flag_colors):
        fx = sx + 24 + i * 40
        c.vline(fx, sy + 30, sy + 42, INK)
        c.fill_rect(fx, sy + 30, 12, 7, col)
    for ry in (sy + 46, sy + 58):
        for i in range(6):
            dx = sx + 14 + i * 50
            c.fill_rect(dx, ry, 38, 7, (120, 90, 60))
            c.fill_rect(dx + 6, ry + 2, 10, 3, PAPER)
    c.fill_rect(sx, sy + 68, sw, sh - 68, (190, 180, 165))
    c.fill_rect(sx + 26, sy + 74, 34, 22, (60, 60, 70))
    c.line(sx + 43, sy + 74, sx + 49, sy + 66, INK)
    cx = sx + sw // 2
    c.rect_outline(cx - 15, sy + 56, 30, 26, RED, 2)
    c.fill_rect(cx - 15, sy + 82, 30, 6, RED)
    c.vline(cx - 12, sy + 88, sy + 95, RED)
    c.vline(cx + 12, sy + 88, sy + 95, RED)
    c.text(sx + 236, sy + 80, "NO DEAL", 1, RED)


def draw_dymer(c, sx, sy, sw, sh):
    c.fill_rect(sx, sy, sw, sh, NIGHT)
    stars = [(10, 8), (30, 14), (60, 6), (90, 12), (130, 8), (170, 16),
             (210, 6), (250, 10), (290, 14), (40, 22), (110, 20),
             (200, 22), (270, 20), (160, 10)]
    for dx, dy in stars:
        c.px(sx + dx, sy + dy, WHITE)
    c.circle_fill(sx + 282, sy + 16, 9, (230, 230, 200))
    for bx, by, bw, bh in [(8, 48, 34, 49), (46, 38, 28, 59),
                           (78, 55, 40, 42), (250, 45, 36, 52)]:
        c.fill_rect(sx + bx, sy + by, bw, bh, DARK)
    for wx, wy in [(14, 56), (22, 56), (14, 66), (22, 76), (52, 46),
                   (60, 56), (52, 66), (256, 52), (264, 62), (256, 72)]:
        c.fill_rect(sx + wx, sy + wy, 3, 4, GOLD)
    # Damaged block: broken top, smoke, blast.
    c.triangle_fill((sx + 78, sy + 55), (sx + 86, sy + 46), (sx + 94, sy + 55), DARK)
    c.triangle_fill((sx + 94, sy + 55), (sx + 104, sy + 48), (sx + 118, sy + 55), DARK)
    c.circle_fill(sx + 88, sy + 40, 5, (120, 120, 130))
    c.circle_fill(sx + 100, sy + 32, 6, (120, 120, 130))
    c.circle_fill(sx + 112, sy + 24, 5, (120, 120, 130))
    c.circle_fill(sx + 98, sy + 50, 6, (255, 140, 0))
    c.circle_fill(sx + 98, sy + 50, 3, (255, 220, 80))
    # Drone arcs across the night sky.
    for acx, r in [(150, 55), (190, 40), (120, 70)]:
        c.arc_up(sx + acx, sy + 95, r, (200, 200, 180))
    for dx, dy in [(150, 40), (190, 55), (120, 25)]:
        c.fill_rect(sx + dx, sy + dy, 2, 2, WHITE)


def draw_benghazi(c, sx, sy, sw, sh):
    c.fill_rect(sx, sy, sw, 44, SKY)
    c.fill_rect(sx, sy + 44, sw, sh - 44, SEA)
    c.circle_fill(sx + 40, sy + 14, 8, (240, 220, 150))
    # Distant second ship, also hit.
    c.fill_rect(sx + 230, sy + 36, 44, 8, (50, 55, 65))
    c.fill_rect(sx + 246, sy + 30, 12, 6, (50, 55, 65))
    c.circle_fill(sx + 252, sy + 26, 4, (140, 140, 145))
    # Merkury, listing and burning.
    c.fill_rect(sx + 70, sy + 52, 130, 14, (40, 45, 55))
    c.triangle_fill((sx + 200, sy + 52), (sx + 200, sy + 66),
                    (sx + 224, sy + 66), (40, 45, 55))
    c.fill_rect(sx + 60, sy + 50, 10, 16, (40, 45, 55))
    c.fill_rect(sx + 110, sy + 40, 34, 12, (70, 75, 85))
    c.vline(sx + 150, sy + 28, sy + 40, (40, 45, 55))
    c.hline(sx + 142, sy + 32, sx + 158, (40, 45, 55))
    c.line(sx + 70, sy + 52, sx + 200, sy + 58, (120, 125, 135))
    c.triangle_fill((sx + 160, sy + 52), (sx + 166, sy + 34),
                    (sx + 172, sy + 52), (255, 120, 0))
    c.triangle_fill((sx + 176, sy + 52), (sx + 182, sy + 38),
                    (sx + 188, sy + 52), (255, 120, 0))
    c.triangle_fill((sx + 164, sy + 52), (sx + 168, sy + 42),
                    (sx + 172, sy + 52), (255, 220, 80))
    c.circle_fill(sx + 166, sy + 30, 6, (120, 120, 125))
    c.circle_fill(sx + 178, sy + 22, 7, (130, 130, 135))
    c.circle_fill(sx + 190, sy + 28, 5, (120, 120, 125))
    # Waterline swallows the lower hull.
    c.fill_rect(sx + 70, sy + 60, 130, 6, SEA)
    c.fill_rect(sx + 200, sy + 60, 24, 6, SEA)
    for wy in (sy + 72, sy + 80, sy + 88):
        for wx in range(sx + 8, sx + sw - 8, 36):
            c.hline(wx, wy, wx + 20, (200, 220, 235))


PANELS = [
    ("1 ANTALYA - COP31 ENDS WITH NO DEAL",
     "LONGEST CLIMATE SUMMIT ON RECORD", draw_cop31),
    ("2 DYMER - 186 DRONES OVERNIGHT",
     "AT LEAST 3 KILLED, 14 MISSING", draw_dymer),
    ("3 BENGHAZI - MERKURY SUNK",
     "HIT BY SEA DRONES, CAPSIZED", draw_benghazi),
]


# ---------------------------------------------------------------- layout
def main():
    c = Canvas()
    c.rect_outline(4, 4, W - 8, H - 8, INK, 1)

    # Masthead.
    mast_x = 512 - c.text_width("SUNDAY 22 NOVEMBER 2026", 6) // 2
    c.text(mast_x, 14, "SUNDAY 22 NOVEMBER 2026", 6, INK)
    masthead_date = "22 NOVEMBER 2026"
    c.text(mast_x + 7 * 36, 14, masthead_date, 6, RED)
    c.hline(16, 60, 1007, INK)
    c.text_centered(512, 66, "THE WORLD IN ONE DAY - 38 STORIES, 8 REGIONS", 2, INK)
    c.hline(16, 86, 1007, INK)

    # Lead sub-headline.
    c.text_centered(512, 92,
                    "COP31 COLLAPSES WITH NO DEAL - 186 DRONES OVER UKRAINE,", 2, INK)
    c.text_centered(512, 108,
                    "DYMER BLOCK HIT - RUSSIAN WARSHIP MERKURY SUNK AT BENGHAZI", 2, INK)

    # Numbers strip: 6 boxes.
    box_w = 162
    for i, (num, lab1, lab2) in enumerate(NUMBERS):
        bx = 16 + i * (box_w + 4)
        c.fill_rect(bx, 128, box_w, 56, PAPER)
        c.rect_outline(bx, 128, box_w, 56, INK, 1)
        c.text_centered(bx + box_w // 2, 134, num, 3, RED)
        c.text_centered(bx + box_w // 2, 160, lab1, 1, INK)
        c.text_centered(bx + box_w // 2, 170, lab2, 1, INK)

    # Region bar.
    c.hline(16, 190, 1007, INK)
    c.text_centered(512, 196, REGION_BAR, 1, INK)
    c.hline(16, 208, 1007, INK)

    # Three drawn lead panels.
    for i, (cap1, cap2, scene) in enumerate(PANELS):
        px = 16 + i * 336
        py = 214
        c.fill_rect(px, py, 320, 128, PAPER)
        c.rect_outline(px, py, 320, 128, INK, 1)
        scene(c, px + 2, py + 2, 316, 98)
        c.hline(px + 2, py + 100, px + 317, GREY)
        c.text_centered(px + 160, py + 104, cap1, 1, INK)
        c.text_centered(px + 160, py + 113, cap2, 1, RED)

    # Story list header.
    c.text(16, 348, "THE DAY IN 38 STORIES", 2, INK)
    c.text(750, 352, "EVERY STORY BELOW HAPPENED ON 22 NOV 2026", 1, RED)
    c.hline(16, 366, 1007, INK)

    # Story list, two columns of 19.
    c.vline(512, 372, 752, GREY)
    for i, (num, city, text) in enumerate(STORIES):
        col = 0 if i < 19 else 1
        row = i % 19
        x = 16 if col == 0 else 524
        y = 372 + row * 20
        prefix = "%d. %s - " % (num, city)
        lines = wrap(prefix + text, 79)
        assert len(lines) == 2, "story %d wraps to %d lines" % (num, len(lines))
        c.text(x, y, lines[0], 1, INK)
        c.text(x, y + 9, lines[1], 1, INK)
        c.text(x, y, prefix, 1, RED)

    # World map + ALSO ON.
    c.text(16, 760, "WHERE IT HAPPENED", 2, RED)
    c.text(336, 760, "ALSO ON", 2, RED)
    mx, my = 16, 776
    for row in sorted(MAP_ROWS):
        for c0, c1 in MAP_ROWS[row]:
            for col in range(c0, c1 + 1):
                c.fill_rect(mx + col * 6, my + row * 3, 4, 2, (60, 70, 85))
    for label, col, row, dx, dy in PINS:
        cx = mx + col * 6 + 3 + dx
        cy = my + row * 3 + 1 + dy
        if label:
            c.fill_rect(cx - 4, cy - 4, 9, 9, RED)
            c.text(cx - 2, cy - 3, label, 1, WHITE)
        else:
            c.fill_rect(cx - 2, cy - 2, 5, 5, RED)
    c.text(16, 852, "1 ANTALYA  2 DYMER  3 BENGHAZI", 1, INK)
    c.text(16, 861, "DOTS: HONG KONG, BANTEN,", 1, INK)
    c.text(16, 870, "WELLINGTON, GENEVA, LAS VEGAS, BRASILIA", 1, INK)
    for i, item in enumerate(ALSO_ON):
        col = 0 if i < 7 else 1
        row = i % 7
        x = 336 if col == 0 else 676
        y = 776 + row * 12
        assert len(item) <= 53, "also-on item too long: %s" % item
        c.text(x, y, "- " + item, 1, INK)

    # Red DATE CHECK box.
    c.rect_outline(16, 886, 992, 100, RED, 2)
    c.text_centered(512, 892,
                    "DATE CHECK: THESE STORIES ARE NOT 22 NOVEMBER - LEFT OUT ON PURPOSE",
                    2, RED)
    for i, item in enumerate(DATE_CHECK):
        col = 0 if i < 7 else 1
        row = i % 7
        x = 28 if col == 0 else 520
        y = 910 + row * 10
        assert len(item) <= 78, "date-check item too long: %s" % item
        c.text(x + 12, y, item, 1, INK)
        c.text(x, y, "X", 1, RED)

    # Footer.
    c.text_centered(512, 994,
                    "EVERY STORY HERE HAPPENED, OR WAS FIRST REPORTED, "
                    "ON SUNDAY 22 NOVEMBER 2026.", 1, INK)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path, c)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
