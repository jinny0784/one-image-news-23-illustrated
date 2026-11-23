#!/usr/bin/env python3
"""Draw the illustrated front page for 23 November 2026.

A single 1024x1024 newspaper front page: masthead, COP31-collapse lead
with a dusk-skyline illustration, a Gulf banner, and nine region blocks
(66 stories) in two columns, each with its own flat illustrated strip.
Pure PIL, fully deterministic: same input -> same bytes every run.

Usage: python3 draw_frontpage.py [output.png]
"""

import math
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---- palette -----------------------------------------------------------
CREAM = (246, 240, 223)
INK = (26, 26, 46)
RED = (176, 30, 40)
TEAL = (14, 107, 107)
GOLD = (255, 220, 120)
FOOT_GREY = (88, 84, 74)

DJV_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJV_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DJV_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
NOTO_SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
NOTO_SERIF_BI = "/usr/share/fonts/truetype/noto/NotoSerif-BoldItalic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(d, box, top, bottom):
    """Vertical gradient inside box (x0, y0, x1, y1), top -> bottom colour."""
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        d.line([(x0, y), (x1, y)], fill=lerp(top, bottom, (y - y0) / span))


def star(d, cx, cy, r, fill):
    """Five-point star centred on (cx, cy)."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


# ---- story data --------------------------------------------------------
# (header label, count, header/bullet colour, headline, [bullet lines])
REGIONS_LEFT = [
    ("SOUTH ASIA", 10, (198, 90, 30),
     "Modi, Nepal PM flag off Saryu-Kamala Express to Janakpur",
     ["Nepal PM Balendra Shah on first India visit; talks on energy, trade, hydropower",
      "India-China end 10-day Corps Commander talks to ease LAC tensions in Arunachal",
      "Amit Shah in Arunachal: border villages push, 40 see reverse migration",
      "Congress-SP seat-sharing talks likely today",
      "Tata Sons: go public or stay private - decision expected this week",
      "India-EU free trade pact likely signed Dec 16 in Brussels",
      "IFFI 2026 hosts BRICS Roundtable; restored classics showcased",
      "Tainted alcohol kills 11 in Manipur",
      "ICJ Myanmar verdict: Rohingya hail 'small victory'; Myanmar rejects ruling"]),
    ("MIDDLE EAST", 9, (14, 107, 107),
     "Gulf on fire: tankers hit, Bahrain struck, blockade showdown looms",
     ["Bahrain intercepts Iranian attacks; civilian facility struck, fire, no casualties",
      "IRGC: two 'violating' supertankers hit mines east of Hormuz - CLAIM",
      "US struck tanker exporting Iranian oil near blockade line - unconfirmed",
      "Houthis claim strikes on Saudi oil refinery + radar, at least 6 injured",
      "Netanyahu-Eisenkot coalition talks end without deal on Israel government",
      "Settler arson attacks on Palestinian villages; Eisenkot calls it 'Jewish terrorism'",
      "US + Israel hold joint operational plans; no decision on escalation yet",
      "CENTCOM: helped Gulf states export 1.5bn barrels via Hormuz since summer"]),
    ("EUROPE", 7, (122, 31, 61),
     "EU led 130-country bloc that rejected the COP31 draft",
     ["Ex-UK PM Theresa May: 'move on' from Brexit; 'aghast' at rejoin talk",
      "Thousands march in Lisbon as living costs fuel anger",
      "Enraged young protesters take the streets of Europe",
      "India-EU free trade pact signing set for Dec 16 in Brussels",
      "Drones attack Russian cargo ship in Gulf of Finland; ship still on fire",
      "EU: 'We will not endorse a deal that does not even mention fossil fuels'"]),
    ("SPORT / CULTURE", 8, (158, 27, 50),
     "Liverpool hammer ten-man United 4-0 in Pochettino's debut",
     ["Day 5, 1st Test: IND 720/9d, NZ 368 & 239/5 \u2014 DRAWN; Mitchell 49*, Phillips 26* defy India",
      "Verstappen wins Las Vegas GP, holding off Norris; 35 lead changes",
      "Gukesh draws black for Game 1 (Tue) vs Sindarov - youngest title match ever",
      "India women crush Thailand 7-0, stay top of Asian Champions Trophy hockey",
      "Anupama retains IBSF World Women's Snooker title in Indore, beats So Man Yan 3-1",
      "Pakistan A beat India A by 48 runs in Asia Cup Rising Stars, Doha",
      "Mohun Bagan top ISL table after nervy 2-1 win at Churchill Brothers"]),
]

REGIONS_RIGHT = [
    ("US / AMERICAS", 9, (43, 76, 155),
     "Democrats' historic House win: biggest majority since 1992",
     ["Trump vows to work with Democrats to cap credit card interest at 10%",
      "Father + daughter detained by masked ICE officers on Seattle jet bridge",
      "Pentagon moves to restrict US-Canada defence ties",
      "San Francisco braces for exceptionally high king tides; flood risk",
      "Nvidia CEO Jensen Huang's exit + SEC probe turmoil",
      "AI brain drain: ~90% of Indian-educated elite AI researchers went abroad",
      "Princeton student Eva Yi Xie detained amid US suspicion of Chinese tech access",
      "Thanksgiving week: markets shut Thu, early close Fri; PCE + GDP Wed"]),
    ("EAST ASIA", 5, (166, 43, 43),
     "Kim: North Korea seeks security, not supremacy",
     ["South Korea's Lee: speed is decisive in the AI race",
      "China exchanges cut margin ratio 100% to 80% from Nov 30",
      "China produces AI talent, America acquires it, India loses it",
      "Kospi -3.5%, Hang Seng slides as AI rout spreads across Asia"]),
    ("SOUTHEAST ASIA & PACIFIC", 4, (46, 125, 50),
     "7 body bags found, 50 missing after Indonesian factory fire",
     ["Myanmar calls ASEAN review of peace plan 'unfair and imbalanced'",
      "COP31 co-chair Australia: Bowen calls outcome 'very disappointing'",
      "Albanese blames fossil-fuel fault lines for the collapse"]),
    ("AFRICA", 4, (141, 90, 43),
     "Sea drones hit Russian warship at Benghazi naval base, Libya",
     ["Drone strikes hit homes + a UN building in Sudan's capital",
      "COP32 goes to Addis Ababa, Ethiopia",
      "'Worst ever COP': Power Shift Africa says collapse must be a wake-up call"]),
    ("BUSINESS / MARKETS", 9, (138, 109, 27),
     "Nasdaq -5.28% Friday, worst week since Covid crash",
     ["Monday whipsaw: Sensex \u22121,484 to 82,436; Nifty \u2212451 to 25,350; US futures +2.8%",
      "Nvidia -14% Friday to $125.53 after reported SEC probe; ~$491bn erased in a day",
      "Bitcoin ~$55,252 Sat, lowest since Sep 2024; back above $60,000",
      "Anthropic IPO: +17% debut Thu, then -11% Friday",
      "JPM now expects Fed rate HIKES in Dec, Jan, Mar",
      "Paolo Bulgari dies at 89; built a family silversmith shop into a luxury empire",
      "Opposition protests hit Meta offices in India",
      "Oil: Brent ~$93 on Hormuz risk, down from $110+ a month ago"]),
]

LEAD_BODY = [
    'Guterres: "deeply disappointing" - \'no ambiguity in the science\'',
    'EU: "hijacked by some oil states" - Ireland\'s O\'Brien',
    "Next: COP32 in Addis Ababa; China calls it a 'deep disappointment'",
]

FOOTER = ("Stories as reported on 23 November 2026 \u00b7 The Hindu \u00b7 CNN "
          "\u00b7 Reuters \u00b7 Gulf News \u00b7 Moneycontrol \u00b7 The Hindu Morning Digest")


# ---- illustrations -----------------------------------------------------
def lead_art(d):
    x0, y0, x1, y1 = 14, 86, 506, 269
    vgrad(d, (x0, y0, x1, y1), (58, 32, 86), (172, 90, 62))
    # EU flag, top right of the picture
    d.rectangle([390, 100, 470, 150], fill=(28, 52, 140))
    for k in range(12):
        ang = -math.pi / 2 + k * math.pi / 6
        star(d, 430 + 18 * math.cos(ang), 125 + 18 * math.sin(ang), 3, GOLD)
    d.ellipse([420, 152, 440, 162], fill=GOLD)
    # cracked globe, left
    cx, cy, r = 150, 178, 78
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(52, 120, 150),
              outline=(20, 40, 70), width=3)
    d.ellipse([95, 128, 142, 172], fill=(86, 160, 84))
    d.ellipse([164, 124, 206, 160], fill=(86, 160, 84))
    d.ellipse([128, 196, 186, 236], fill=(86, 160, 84))
    d.line([(96, 128), (122, 158), (106, 192), (142, 222)], fill=GOLD, width=3)
    d.line([(206, 150), (182, 178), (196, 208)], fill=GOLD, width=3)
    # skyline with lit windows
    for bx, bw, bh in [(20, 42, 46), (66, 30, 34), (100, 38, 52), (300, 40, 48),
                       (344, 30, 36), (378, 42, 54), (424, 36, 40), (464, 38, 48)]:
        d.rectangle([bx, 252 - bh, bx + bw, 252], fill=(30, 22, 48))
        for wx in range(bx + 6, bx + bw - 4, 12):
            for wy in range(252 - bh + 6, 248, 12):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=GOLD)
    # dark tower at the right edge
    d.rectangle([478, 178, 492, 252], fill=(20, 20, 30))
    d.polygon([(474, 178), (496, 178), (485, 162)], fill=(20, 20, 30))
    # bottom band with red blocks
    d.rectangle([x0, 252, x1, y1], fill=(30, 22, 48))
    for bx in range(24, 480, 46):
        d.rectangle([bx, 240, bx + 30, 262], fill=(150, 52, 60))
    d.rectangle([380, 236, 420, 262], fill=(120, 90, 40))


def train_art(d, x0, y0, x1, y1):
    vgrad(d, (x0, y0, x1, y1), (250, 214, 150), (238, 176, 110))
    d.polygon([(28, y1), (28, y0 + 8), (52, y0 + 2), (58, y0 + 14), (58, y1)],
              fill=(120, 70, 30))
    # red train, left
    d.rectangle([100, y0 + 6, 232, y0 + 26], fill=(190, 50, 45))
    for wx in range(108, 228, 26):
        d.rectangle([wx, y0 + 10, wx + 16, y0 + 20], fill=(255, 240, 200))
    # blue train, right
    d.rectangle([280, y0 + 6, 472, y0 + 26], fill=(28, 76, 150))
    for wx in range(288, 468, 26):
        d.rectangle([wx, y0 + 10, wx + 16, y0 + 20], fill=(180, 210, 240))
    for wx in (120, 200, 310, 400, 450):
        d.ellipse([wx - 6, y0 + 26, wx + 6, y0 + 34], fill=(20, 20, 26))
    d.ellipse([452, y0 + 4, 478, y0 + 30], fill=GOLD)
    d.rectangle([x0, y1 - 3, x1, y1], fill=(80, 52, 24))


def capitol_art(d, x0, y0, x1, y1):
    vgrad(d, (x0, y0, x1, y1), (200, 215, 238), (150, 175, 215))
    # white capitol block
    d.rectangle([620, y0 + 16, 900, y1 - 6], fill=(245, 245, 240))
    d.ellipse([722, y0 - 6, 798, y0 + 24], fill=(245, 245, 240))
    d.rectangle([756, y0 - 12, 764, y0], fill=(245, 245, 240))
    for cx in range(640, 900, 24):
        d.rectangle([cx, y0 + 22, cx + 8, y1 - 6], fill=(215, 215, 205))
    # birds
    for bx, by in [(560, 14), (580, 20), (940, 18), (960, 12)]:
        d.arc([bx - 5, by - 3, bx + 5, by + 3], 200, 340, fill=(30, 30, 50), width=2)
    d.rectangle([x0, y1 - 6, x1, y1 - 3], fill=(176, 30, 40))
    d.rectangle([x0, y1 - 3, x1, y1], fill=(245, 245, 240))


def tanker_art(d, x0, y0, x1, y1):
    vgrad(d, (x0, y0, x1, y1), (250, 189, 119), (238, 160, 90))
    d.ellipse([440, y0 - 2, 486, y0 + 30], fill=GOLD)
    # sea band
    d.rectangle([x0, y0 + 18, x1, y1], fill=(15, 62, 108))
    # red tanker, left
    d.polygon([(40, y0 + 14), (270, y0 + 14), (250, y0 + 30), (60, y0 + 30)],
              fill=(140, 30, 30))
    d.rectangle([120, y0 + 2, 170, y0 + 14], fill=(90, 90, 95))
    d.ellipse([140, y0 - 6, 180, y0 + 6], fill=(60, 60, 60))
    # mine in the water
    mx, my = 330, y0 + 24
    d.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(10, 10, 14))
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(mx + 8 * math.cos(a), my + 8 * math.sin(a)),
                (mx + 13 * math.cos(a), my + 13 * math.sin(a))],
               fill=(10, 10, 14), width=2)
    # dark tanker silhouette, right
    d.polygon([(420, y0 + 10), (500, y0 + 10), (488, y0 + 28), (432, y0 + 28)],
              fill=(30, 30, 40))
    d.rectangle([455, y0 + 2, 465, y0 + 10], fill=(30, 30, 40))


def pagoda_art(d, x0, y0, x1, y1):
    vgrad(d, (x0, y0, x1, y1), (250, 200, 150), (235, 150, 110))
    d.ellipse([930, y0 + 2, 962, y0 + 34], fill=(240, 120, 60))
    # purple mountains, low and rolling
    d.polygon([(x0, y1), (620, y0 + 16), (720, y1)], fill=(70, 45, 90))
    d.polygon([(640, y1), (860, y0 + 20), (1010, y1)], fill=(60, 38, 80))
    # pagoda, centre
    for i, (ty, tw) in enumerate([(0, 110), (9, 92), (18, 74)]):
        yy = y0 + 2 + i * 9
        d.rectangle([760 - tw // 2, yy, 760 + tw // 2, yy + 6], fill=(230, 180, 60))
        d.rectangle([760 - tw // 2 - 7, yy + 6, 760 + tw // 2 + 7, yy + 9],
                    fill=(176, 30, 40))
    d.rectangle([746, y0 + 29, 774, y1], fill=(230, 180, 60))
    # black train, left
    d.rectangle([530, y0 + 8, 600, y0 + 26], fill=(25, 25, 32))
    d.rectangle([540, y0 + 12, 560, y0 + 20], fill=GOLD)
    d.line([(600, y0 + 26), (640, y0 + 26)], fill=(25, 25, 32), width=2)


def factory_art(d, x0, y0, x1, y1):
    vgrad(d, (x0, y0, x1, y1), (120, 60, 50), (90, 40, 40))
    # factory block with flames
    d.rectangle([540, y0 + 14, 760, y1], fill=(60, 60, 70))
    for wx in range(550, 750, 28):
        d.rectangle([wx, y0 + 20, wx + 16, y0 + 28], fill=GOLD)
    for fx in (570, 640, 710):
        d.polygon([(fx - 12, y0 + 14), (fx, y0 - 2), (fx + 12, y0 + 14)],
                  fill=(240, 140, 40))
        d.polygon([(fx - 6, y0 + 14), (fx, y0 + 4), (fx + 6, y0 + 14)],
                  fill=GOLD)
    d.rectangle([790, y0 + 8, 812, y1], fill=(80, 80, 88))
    d.rectangle([826, y0 + 12, 844, y1], fill=(80, 80, 88))
    # palm, right
    d.rectangle([958, y0 + 10, 964, y1], fill=(90, 60, 30))
    for ang in range(-70, 71, 35):
        a = math.radians(ang - 90)
        d.line([(961, y0 + 10), (961 + 22 * math.cos(a), y0 + 10 + 12 * math.sin(a))],
               fill=(60, 120, 60), width=3)


def europe_art(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(28, 52, 140))
    for k in range(6):
        ang = -math.pi / 2 + (k - 2.5) * math.pi / 6
        star(d, x0 + 216 + 52 * math.cos(ang), y0 + 16 + 14 * math.sin(ang),
             7, GOLD)
    # Union Jack, simplified: white field, red cross and diagonals
    d.rectangle([x1 - 70, y0 + 4, x1 - 8, y1 - 4], fill=(245, 245, 240))
    d.line([(x1 - 70, y0 + 4), (x1 - 8, y1 - 4)], fill=(200, 30, 40), width=3)
    d.line([(x1 - 70, y1 - 4), (x1 - 8, y0 + 4)], fill=(200, 30, 40), width=3)
    d.rectangle([x1 - 40, y0 + 4, x1 - 34, y1 - 4], fill=(200, 30, 40))
    d.rectangle([x1 - 70, y0 + 13, x1 - 8, y0 + 19], fill=(200, 30, 40))


def africa_art(d, x0, y0, x1, y1):
    vgrad(d, (x0, y0, x1, y1), (245, 200, 130), (230, 170, 100))
    d.ellipse([556, y0 + 4, 584, y0 + 32], fill=GOLD)
    d.rectangle([620, y0 + 18, 700, y1 - 6], fill=(40, 40, 50))
    star(d, 720, y0 + 12, 10, (240, 140, 40))
    d.rectangle([x0, y1 - 6, x1, y1], fill=(40, 90, 140))
    # acacia, right
    d.rectangle([952, y0 + 12, 958, y1 - 6], fill=(90, 60, 30))
    d.ellipse([920, y0 + 2, 992, y0 + 14], fill=(60, 120, 60))


def pitch_art(d, x0, y0, x1, y1):
    vgrad(d, (x0, y0, x1, y1), (140, 190, 120), (110, 170, 95))
    d.line([(x0, y0 + 18), (x1, y0 + 18)], fill=(245, 245, 240), width=2)
    d.line([(x0 + 250, y0), (x0 + 250, y1)], fill=(245, 245, 240), width=2)
    # scoreboard
    d.rectangle([x0 + 20, y0 + 4, x0 + 120, y0 + 20], fill=INK)
    d.text((x0 + 28, y0 + 12), "LIV 4-0 MUN", font=font(DJV_SANS_B, 11),
           fill=(255, 255, 255), anchor="lm")
    # ball
    d.ellipse([x0 + 286, y0 + 8, x0 + 304, y0 + 26], fill=(245, 245, 240),
              outline=(20, 20, 26), width=2)
    d.polygon([(x0 + 295, y0 + 13), (x0 + 300, y0 + 17), (x0 + 295, y0 + 21),
               (x0 + 290, y0 + 17)], fill=(20, 20, 26))
    # bat and red ball
    d.line([(x0 + 330, y0 + 26), (x0 + 390, y0 + 6)], fill=(210, 180, 120),
           width=4)
    d.ellipse([x0 + 418, y0 + 6, x0 + 432, y0 + 20], fill=(200, 40, 40))
    # goal, right
    d.rectangle([x1 - 56, y0 + 6, x1 - 8, y0 + 26], outline=(245, 245, 240),
                width=2)


def chart_art(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(12, 18, 40))
    pts = [(x0 + 6, y0 + 6), (600, y0 + 8), (680, y0 + 14), (750, y0 + 22),
           (820, y0 + 18), (900, y0 + 28)]
    d.line(pts, fill=(220, 60, 60), width=2)
    d.ellipse([894, y0 + 22, 906, y0 + 34], fill=(220, 60, 60))
    for cx in (780, 810, 840):
        d.ellipse([cx - 7, y0 + 20, cx + 7, y0 + 34], fill=(255, 200, 60),
                  outline=(180, 130, 20), width=1)
        d.text((cx, y0 + 27), "$", font=font(DJV_SANS_B, 9), fill=(120, 80, 10),
               anchor="mm")
    d.line([(920, y0 + 28), (960, y0 + 14), (1000, y0 + 18)], fill=(60, 200, 100),
           width=3)
    d.polygon([(1000, y0 + 18), (988, y0 + 12), (988, y0 + 24)], fill=(60, 200, 100))


ART = {
    "SOUTH ASIA": train_art,
    "US / AMERICAS": capitol_art,
    "MIDDLE EAST": tanker_art,
    "EAST ASIA": pagoda_art,
    "SOUTHEAST ASIA & PACIFIC": factory_art,
    "EUROPE": europe_art,
    "AFRICA": africa_art,
    "SPORT / CULTURE": pitch_art,
    "BUSINESS / MARKETS": chart_art,
}

# row-1 header tops and the header tops for the remaining blocks
LEFT_TOPS = [302, 479, 645, 789]
RIGHT_TOPS = [302, 468, 590, 701, 812]


# ---- page --------------------------------------------------------------
def draw_region(d, x, hy, label, count, colour, headline, bullets):
    """One region block: header bar, illustrated strip, headline, bullets."""
    d.rectangle([x, hy, x + 490, hy + 18], fill=colour)
    lab = font(DJV_SANS_B, 11)
    d.text((x + 9, hy + 14), label, font=lab, fill=(255, 255, 255), anchor="ls")
    d.text((x + 480, hy + 14), str(count), font=lab, fill=(255, 255, 255),
           anchor="rs")
    ART[label](d, x, hy + 18, x + 490, hy + 50)
    d.line([(x, hy + 50), (x + 490, hy + 50)], fill=INK, width=1)
    d.text((x + 9, hy + 57), headline, font=font(DJV_SERIF_B, 12),
           fill=INK, anchor="la")
    body = font(DJV_SANS, 10)
    for i, line in enumerate(bullets):
        by = hy + 74 + i * 11
        d.rectangle([x + 7, by + 1, x + 14, by + 8], fill=colour)
        d.text((x + 19, by), line, font=body, fill=INK, anchor="la")


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # masthead
    d.text((15, 14), "THE WORLD IN ONE DAY", font=font(DJV_SERIF_B, 48),
           fill=INK, anchor="lt")
    d.text((1009, 14), "MONDAY 23 NOVEMBER 2026", font=font(DJV_SERIF_B, 19),
           fill=INK, anchor="rt")
    d.text((1009, 49), "66 STORIES \u00b7 9 REGIONS \u00b7 ONE DAY",
           font=font(DJV_SANS_B, 11), fill=RED, anchor="rb")
    d.line([(14, 76), (1010, 76)], fill=INK, width=1)
    d.line([(14, 80), (1010, 80)], fill=INK, width=1)

    # lead: illustration + text
    lead_art(d)
    d.text((520, 92), "LEAD \u00b7 CLIMATE", font=font(DJV_SANS_B, 11),
           fill=RED, anchor="la")
    d.text((520, 114), "COP31", font=font(DJV_SERIF_B, 40), fill=RED, anchor="la")
    d.text((520, 154), "COLLAPSES", font=font(DJV_SERIF_B, 40), fill=RED,
           anchor="la")
    d.text((520, 196), "No deal in Antalya", font=font(NOTO_SERIF_BI, 28),
           fill=INK, anchor="la")
    lead_body = font(DJV_SANS, 12)
    for i, line in enumerate(LEAD_BODY):
        d.text((520, 226 + i * 15), line, font=lead_body, fill=INK, anchor="la")

    # Gulf banner
    d.rectangle([14, 272, 1010, 296], fill=TEAL)
    banner = font(DJV_SANS_B, 14)
    d.text((25, 290), "GULF ON FIRE \u2014 Iran 'reported' to send 14 tankers "
           "to test the US blockade; Trump: 'bottom of the sea'",
           font=banner, fill=(255, 255, 255), anchor="ls")
    d.text((1000, 290), "CLAIM: plan unconfirmed",
           font=font(DJV_SANS_B, 10), fill=GOLD, anchor="rs")

    # region columns
    for hy, region in zip(LEFT_TOPS, REGIONS_LEFT):
        draw_region(d, 14, hy, *region)
    for hy, region in zip(RIGHT_TOPS, REGIONS_RIGHT):
        draw_region(d, 520, hy, *region)

    # footer
    d.line([(14, 1010), (1010, 1010)], fill=INK, width=1)
    d.text((14, 1014), FOOTER, font=font(DJV_SANS, 9), fill=FOOT_GREY,
           anchor="la")
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = build()
    img.save(out, format="PNG")
    print(f"wrote {out} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
