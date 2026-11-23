#!/usr/bin/env python3
"""Draw the illustrated front page for 23 November 2026.
All art is drawn from scratch with PIL primitives in this session.
Layout: masthead, big illustrated COP31 lead, Hormuz strip, then a
two-column grid of 9 region blocks, each with its own drawn scene.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 240, 223)
INK = (26, 26, 46)
RED = (176, 30, 40)
TEAL = (14, 107, 107)
ORANGE = (214, 108, 44)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
GREY = (90, 86, 76)

FD = "/usr/share/fonts/truetype/dejavu/"

def F(name, size):
    return ImageFont.truetype(FD + name, size)

f_mast = F("DejaVuSerif-Bold.ttf", 46)
f_mast_sm = F("DejaVuSerif-Bold.ttf", 20)
f_lead = F("DejaVuSerif-Bold.ttf", 40)
f_lead2 = F("DejaVuSerif-Bold.ttf", 26)
f_head = F("DejaVuSans-Bold.ttf", 12)
f_sub = F("DejaVuSans.ttf", 12)
f_sub_b = F("DejaVuSans-Bold.ttf", 13)
f_bullet = F("DejaVuSans.ttf", 10)
f_small = F("DejaVuSans.ttf", 10)
f_small_b = F("DejaVuSans-Bold.ttf", 10)
f_kick = F("DejaVuSans-Bold.ttf", 11)
f_strip = F("DejaVuSans-Bold.ttf", 14)
f_foot = F("DejaVuSans.ttf", 9)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img, "RGBA")

def text(x, y, s, font, fill=INK, anchor="la"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)

def wrap(s, font, width):
    """Greedy wrap to at most 2 lines; returns list of lines."""
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if font.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def sky(x0, y0, x1, y1, top, bottom):
    """Vertical gradient sky."""
    h = y1 - y0
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)

def sun(x, y, r, col=(255, 196, 66)):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)

def wave(x0, y0, x1, y1, col, amp=4, step=14):
    pts = [(x0, y0 + (y1 - y0) // 2)]
    x = x0
    up = True
    while x < x1:
        pts.append((x, y0 + (y1 - y0) // 2 + (-amp if up else amp)))
        x += step
        up = not up
    pts.append((x1, y0 + (y1 - y0) // 2))
    pts.append((x1, y1))
    pts.append((x0, y1))
    d.polygon(pts, fill=col)

# ---------------------------------------------------------------- scenes
def scene_cop31(x0, y0, x1, y1):
    """Cracked globe over an empty summit hall at dusk, Antalya."""
    sky(x0, y0, x1, y1, (58, 32, 86), (214, 110, 52))
    sun(x1 - 52, y0 + 34, 22, (255, 205, 90))
    # distant skyline / hall roofline
    d.rectangle([x0, y1 - 46, x1, y1], fill=(30, 22, 48))
    for bx, bw, bh in [(18, 46, 26), (74, 34, 38), (118, 52, 22), (180, 30, 32),
                        (220, 44, 26), (274, 36, 36), (320, 48, 24), (378, 32, 30)]:
        d.rectangle([x0 + bx, y1 - 46 - bh, x0 + bx + bw, y1 - 46], fill=(44, 32, 66))
        for wy in range(y1 - 46 - bh + 6, y1 - 50, 10):
            for wx in range(x0 + bx + 5, x0 + bx + bw - 4, 10):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 205, 90))
    # row of empty chairs
    cy = y1 - 18
    for cx in range(x0 + 16, x1 - 30, 34):
        d.rectangle([cx, cy - 12, cx + 20, cy], fill=(120, 40, 48))
        d.rectangle([cx + 2, cy - 20, cx + 18, cy - 12], fill=(150, 52, 60))
    # big cracked globe, centre-left
    gx, gy, gr = x0 + 118, y0 + 78, 62
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(52, 120, 150),
              outline=(20, 40, 70), width=3)
    # continents (green blobs)
    d.ellipse([gx - 48, gy - 34, gx - 6, gy + 2], fill=(86, 160, 84))
    d.ellipse([gx + 2, gy + 6, gx + 44, gy + 40], fill=(86, 160, 84))
    d.ellipse([gx + 8, gy - 40, gx + 40, gy - 8], fill=(110, 175, 96))
    # crack: jagged black line across the globe
    crack = [(gx - 52, gy - 44), (gx - 30, gy - 18), (gx - 38, gy + 4),
             (gx - 8, gy + 22), (gx - 16, gy + 44), (gx + 14, gy + 56),
             (gx + 6, gy + 30), (gx + 34, gy + 12), (gx + 52, gy - 20)]
    d.line(crack, fill=(18, 18, 26), width=4)
    d.line(crack, fill=(255, 220, 120), width=1)
    # gavel lying on the floor, bottom right
    d.rectangle([x1 - 96, y1 - 30, x1 - 44, y1 - 22], fill=(120, 82, 40))
    d.rectangle([x1 - 82, y1 - 44, x1 - 58, y1 - 22], fill=(90, 58, 28))
    # EU flag circle of stars, top right
    fx, fy = x1 - 58, y0 + 30
    d.rectangle([fx - 34, fy - 20, fx + 34, fy + 20], fill=(28, 52, 140))
    for k in range(12):
        a = -math.pi / 2 + k * math.pi / 6
        sx, sy = fx + 15 * math.cos(a), fy + 12 * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 215, 0))
    # oil derrick silhouette, right edge
    d.polygon([(x1 - 16, y1 - 46), (x1 - 4, y1 - 46), (x1 - 8, y1 - 96),
               (x1 - 12, y1 - 96)], fill=(20, 20, 30))
    d.line([(x1 - 10, y1 - 96), (x1 - 26, y1 - 78)], fill=(20, 20, 30), width=3)

def scene_train(x0, y0, x1, y1):
    sky(x0, y0, x1, y1, (250, 214, 150), (238, 170, 110))
    sun(x1 - 40, y0 + 16, 13)
    # temple dome (Ayodhya) left
    d.polygon([(x0 + 8, y1 - 18), (x0 + 34, y1 - 52), (x0 + 60, y1 - 18)],
              fill=(176, 90, 40))
    d.rectangle([x0 + 26, y1 - 58, x0 + 42, y1 - 52], fill=(176, 90, 40))
    d.ellipse([x0 + 30, y1 - 64, x0 + 38, y1 - 56], fill=(255, 205, 90))
    # train: engine + 2 coaches
    ty = y1 - 26
    d.rectangle([x0 + 78, ty - 22, x0 + 150, ty], fill=(176, 30, 40))
    d.polygon([(x0 + 150, ty - 22), (x0 + 168, ty - 12), (x0 + 168, ty),
               (x0 + 150, ty)], fill=(140, 22, 30))
    d.rectangle([x0 + 84, ty - 18, x0 + 100, ty - 8], fill=(255, 230, 150))
    d.rectangle([x0 + 106, ty - 18, x0 + 122, ty - 8], fill=(255, 230, 150))
    d.rectangle([x0 + 128, ty - 18, x0 + 144, ty - 8], fill=(255, 230, 150))
    for cx in (x0 + 182, x0 + 236, x0 + 290):
        d.rectangle([cx, ty - 20, cx + 52, ty], fill=(28, 76, 150))
        d.rectangle([cx + 6, ty - 16, cx + 20, ty - 8], fill=(200, 230, 255))
        d.rectangle([cx + 26, ty - 16, cx + 40, ty - 8], fill=(200, 230, 255))
    for cx in (x0 + 96, x0 + 132, x0 + 200, x0 + 258, x0 + 312):
        d.ellipse([cx - 6, ty - 2, cx + 6, ty + 8], fill=(30, 30, 40))
    d.rectangle([x0, y1 - 6, x1, y1 - 2], fill=(90, 60, 30))
    # Janakpur flag on last coach
    d.line([(x0 + 330, ty - 20), (x0 + 330, ty - 34)], fill=(30, 30, 40), width=2)
    d.polygon([(x0 + 330, ty - 34), (x0 + 348, ty - 30), (x0 + 330, ty - 26)],
              fill=(220, 40, 40))

def scene_tanker(x0, y0, x1, y1):
    sky(x0, y0, x1, y1, (250, 190, 120), (220, 120, 60))
    sun(x1 - 44, y0 + 18, 15, (255, 230, 160))
    # sea
    d.rectangle([x0, y1 - 26, x1, y1], fill=(24, 68, 110))
    wave(x0, y1 - 30, x1, y1 - 14, (36, 96, 140))
    # tanker hull + deck, smoke from a hit
    d.polygon([(x0 + 30, y1 - 30), (x0 + 210, y1 - 30), (x0 + 196, y1 - 12),
               (x0 + 44, y1 - 12)], fill=(120, 30, 30))
    d.rectangle([x0 + 60, y1 - 46, x0 + 150, y1 - 30], fill=(90, 22, 22))
    d.rectangle([x0 + 164, y1 - 52, x0 + 196, y1 - 30], fill=(240, 240, 230))
    d.rectangle([x0 + 168, y1 - 48, x0 + 178, y1 - 42], fill=(30, 60, 90))
    d.rectangle([x0 + 182, y1 - 48, x0 + 192, y1 - 42], fill=(30, 60, 90))
    # fire + smoke plume
    d.polygon([(x0 + 96, y1 - 46), (x0 + 108, y1 - 66), (x0 + 120, y1 - 46)],
              fill=(255, 140, 20))
    d.polygon([(x0 + 102, y1 - 46), (x0 + 108, y1 - 58), (x0 + 114, y1 - 46)],
              fill=(255, 220, 80))
    for i, (sx, sy, sr) in enumerate([(108, y0 + 12, 9), (118, y0 + 20, 7),
                                      (100, y0 + 22, 6)]):
        d.ellipse([x0 + sx - sr, sy - sr, x0 + sx + sr, sy + sr],
                  fill=(70, 70, 80))
    # warship silhouette right
    d.polygon([(x1 - 96, y1 - 26), (x1 - 8, y1 - 26), (x1 - 18, y1 - 14),
               (x1 - 86, y1 - 14)], fill=(40, 44, 52))
    d.rectangle([x1 - 70, y1 - 38, x1 - 40, y1 - 26], fill=(40, 44, 52))
    d.line([(x1 - 56, y1 - 38), (x1 - 56, y1 - 52)], fill=(40, 44, 52), width=3)
    # mine in the water, left
    d.ellipse([x0 + 232, y1 - 22, x0 + 246, y1 - 8], fill=(20, 20, 26))
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(x0 + 239 + 6 * math.cos(a), y1 - 15 + 6 * math.sin(a)),
                (x0 + 239 + 10 * math.cos(a), y1 - 15 + 10 * math.sin(a))],
               fill=(20, 20, 26), width=2)

def scene_capitol(x0, y0, x1, y1):
    sky(x0, y0, x1, y1, (150, 180, 220), (240, 225, 190))
    # capitol dome
    d.rectangle([x0 + 60, y1 - 30, x0 + 260, y1 - 8], fill=(240, 238, 228),
                outline=(150, 148, 140))
    d.rectangle([x0 + 90, y1 - 44, x0 + 230, y1 - 30], fill=(240, 238, 228),
                outline=(150, 148, 140))
    d.pieslice([x0 + 110, y1 - 78, x0 + 210, y1 - 10], 180, 360,
               fill=(245, 244, 236))
    d.rectangle([x0 + 156, y1 - 88, x0 + 164, y1 - 76], fill=(200, 190, 170))
    d.ellipse([x0 + 154, y1 - 92, x0 + 166, y1 - 84], fill=(200, 190, 170))
    for cx in range(x0 + 100, x0 + 230, 18):
        d.rectangle([cx, y1 - 28, cx + 8, y1 - 8], fill=(200, 198, 184))
    # stars
    for sx, sy in [(x0 + 30, y0 + 12), (x0 + 300, y0 + 10), (x0 + 330, y0 + 26),
                   (x0 + 18, y0 + 34)]:
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(28, 52, 140))
    # red/blue stripes base
    for i, c in enumerate([(176, 30, 40), (255, 255, 255), (28, 52, 140),
                           (255, 255, 255), (176, 30, 40)]):
        d.rectangle([x0, y1 - 8 + i * 1, x1, y1 - 7 + i * 1], fill=c)

def scene_eu(x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(28, 52, 140))
    cx, cy = (x0 + x1) // 2 - 60, (y0 + y1) // 2
    for k in range(12):
        a = -math.pi / 2 + k * math.pi / 6
        sx, sy = cx + 52 * math.cos(a), cy + 40 * math.sin(a)
        d.polygon([(sx, sy - 6), (sx + 2, sy - 2), (sx + 6, sy - 2),
                   (sx + 3, sy + 1), (sx + 4, sy + 5), (sx, sy + 3),
                   (sx - 4, sy + 5), (sx - 3, sy + 1), (sx - 6, sy - 2),
                   (sx - 2, sy - 2)], fill=(255, 215, 0))
    # small flags row right: UK + tricolour hints
    d.rectangle([x1 - 92, y0 + 10, x1 - 34, y1 - 10], fill=(255, 255, 255),
                outline=(26, 26, 46))
    d.line([(x1 - 92, y0 + 10), (x1 - 34, y1 - 10)], fill=(200, 30, 40), width=4)
    d.line([(x1 - 34, y0 + 10), (x1 - 92, y1 - 10)], fill=(200, 30, 40), width=4)
    d.rectangle([x1 - 92, (y0 + y1) // 2 - 3, x1 - 34, (y0 + y1) // 2 + 3],
                fill=(200, 30, 40))

def scene_pagoda(x0, y0, x1, y1):
    sky(x0, y0, x1, y1, (250, 200, 170), (200, 120, 90))
    sun(x1 - 46, y0 + 18, 16, (255, 120, 60))
    # mountains
    d.polygon([(x0, y1), (x0 + 90, y0 + 26), (x0 + 180, y1)], fill=(90, 60, 80))
    d.polygon([(x0 + 140, y1), (x0 + 240, y0 + 34), (x0 + 330, y1)],
              fill=(70, 48, 70))
    # pagoda
    px = x0 + 210
    for i, w_ in enumerate([64, 54, 44]):
        yy = y1 - 12 - i * 16
        d.rectangle([px - w_ // 2, yy - 10, px + w_ // 2, yy], fill=(150, 40, 40))
        d.polygon([(px - w_ // 2 - 8, yy), (px + w_ // 2 + 8, yy),
                   (px + w_ // 2, yy - 6), (px - w_ // 2, yy - 6)],
                  fill=(220, 160, 60))
    d.polygon([(px - 8, y1 - 60), (px + 8, y1 - 60), (px, y1 - 74)],
              fill=(220, 160, 60))
    # chip
    d.rectangle([x0 + 16, y1 - 34, x0 + 52, y1 - 6], fill=(30, 30, 44))
    for k in range(3):
        d.line([(x0 + 16, y1 - 28 + k * 8), (x0 + 10, y1 - 28 + k * 8)],
               fill=(200, 200, 210), width=2)
        d.line([(x0 + 52, y1 - 28 + k * 8), (x0 + 58, y1 - 28 + k * 8)],
               fill=(200, 200, 210), width=2)
    d.rectangle([x0 + 26, y1 - 26, x0 + 42, y1 - 14], fill=(255, 215, 0))

def scene_fire(x0, y0, x1, y1):
    sky(x0, y0, x1, y1, (60, 50, 60), (140, 70, 50))
    # factory block
    d.rectangle([x0 + 20, y1 - 34, x0 + 200, y1 - 6], fill=(70, 70, 78))
    d.rectangle([x0 + 210, y1 - 52, x0 + 226, y1 - 6], fill=(90, 90, 98))
    d.rectangle([x0 + 240, y1 - 44, x0 + 254, y1 - 6], fill=(90, 90, 98))
    for wx in range(x0 + 34, x0 + 190, 26):
        d.rectangle([wx, y1 - 28, wx + 14, y1 - 16], fill=(255, 200, 90))
    # flames
    for fx, fh in [(60, 26), (90, 36), (120, 28), (150, 32)]:
        d.polygon([(x0 + fx - 10, y1 - 34), (x0 + fx, y1 - 34 - fh),
                   (x0 + fx + 10, y1 - 34)], fill=(255, 140, 20))
        d.polygon([(x0 + fx - 5, y1 - 34), (x0 + fx, y1 - 34 - fh + 12),
                   (x0 + fx + 5, y1 - 34)], fill=(255, 220, 80))
    # smoke
    for sx, sy, sr in [(80, y0 + 12, 10), (100, y0 + 20, 8), (130, y0 + 10, 9)]:
        d.ellipse([x0 + sx - sr, sy - sr, x0 + sx + sr, sy + sr],
                  fill=(80, 80, 88))
    # palm right
    d.line([(x1 - 40, y1 - 6), (x1 - 40, y1 - 40)], fill=(90, 60, 30), width=4)
    for ang in (-50, -20, 10, 40):
        a = math.radians(ang - 90)
        d.line([(x1 - 40, y1 - 40),
                (x1 - 40 + 26 * math.cos(a), y1 - 40 + 26 * math.sin(a))],
               fill=(40, 120, 60), width=3)

def scene_sea_blast(x0, y0, x1, y1):
    sky(x0, y0, x1, y1, (240, 200, 130), (200, 130, 70))
    sun(x0 + 40, y0 + 16, 13, (255, 220, 120))
    d.rectangle([x0, y1 - 22, x1, y1], fill=(30, 80, 120))
    wave(x0, y1 - 26, x1, y1 - 12, (48, 110, 150))
    # warship + explosion
    d.polygon([(x0 + 30, y1 - 22), (x0 + 150, y1 - 22), (x0 + 138, y1 - 10),
               (x0 + 44, y1 - 10)], fill=(50, 54, 62))
    d.rectangle([x0 + 60, y1 - 34, x0 + 110, y1 - 22], fill=(50, 54, 62))
    ex, ey = x0 + 120, y1 - 44
    for k in range(8):
        a = k * math.pi / 4
        r1 = 18 if k % 2 == 0 else 10
        d.polygon([(ex, ey),
                   (ex + r1 * math.cos(a - 0.25), ey + r1 * math.sin(a - 0.25)),
                   (ex + r1 * math.cos(a + 0.25), ey + r1 * math.sin(a + 0.25))],
                  fill=(255, 150, 30))
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(255, 220, 80))
    # acacia tree right
    d.line([(x1 - 36, y1 - 6), (x1 - 36, y1 - 30)], fill=(90, 60, 30), width=4)
    d.ellipse([x1 - 62, y1 - 40, x1 - 10, y1 - 28], fill=(60, 110, 50))

def scene_chart(x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(24, 28, 44))
    # grid
    for gy in range(y0 + 10, y1 - 6, 12):
        d.line([(x0 + 6, gy), (x1 - 6, gy)], fill=(60, 66, 90), width=1)
    # plunging red line
    pts = [(x0 + 14, y0 + 12), (x0 + 70, y0 + 16), (x0 + 120, y0 + 12),
           (x0 + 170, y0 + 26), (x0 + 220, y0 + 22), (x0 + 260, y0 + 40),
           (x0 + 300, y0 + 34), (x0 + 330, y1 - 14)]
    d.line(pts, fill=(255, 70, 70), width=4)
    d.ellipse([pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5],
              fill=(255, 70, 70))
    text(x0 + 10, y0 + 6, "-5.28%", f_small_b, (255, 120, 120))
    # green bounce arrow right
    d.line([(x1 - 52, y1 - 12), (x1 - 30, y1 - 26), (x1 - 14, y1 - 20)],
           fill=(80, 220, 120), width=3)
    d.polygon([(x1 - 14, y1 - 26), (x1 - 14, y1 - 14), (x1 - 4, y1 - 20)],
              fill=(80, 220, 120))
    # coins
    for i, cx in enumerate([x0 + 250, x0 + 268, x0 + 286]):
        d.ellipse([cx, y1 - 16, cx + 14, y1 - 4], fill=(255, 215, 0),
                  outline=(180, 140, 0))
        text(cx + 7, y1 - 15, "$", f_small_b, (140, 100, 0), anchor="ma")

def scene_footy(x0, y0, x1, y1):
    sky(x0, y0, x1, y1, (140, 190, 120), (90, 150, 80))
    # pitch
    d.rectangle([x0, y1 - 22, x1, y1], fill=(46, 120, 58))
    d.line([(x0, y1 - 22), (x1, y1 - 22)], fill=(255, 255, 255), width=2)
    # goal
    d.rectangle([x1 - 90, y0 + 12, x1 - 14, y1 - 22], fill=None,
                outline=(255, 255, 255), width=3)
    for gy in range(y0 + 16, y1 - 24, 8):
        d.line([(x1 - 90, gy), (x1 - 14, gy)], fill=(255, 255, 255), width=1)
    # ball
    bx, by = x0 + 150, y1 - 34
    d.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(255, 255, 255),
              outline=(30, 30, 30), width=2)
    d.polygon([(bx, by - 6), (bx + 5, by - 2), (bx + 3, by + 5),
               (bx - 3, by + 5), (bx - 5, by - 2)], fill=(30, 30, 30))
    # score badge
    d.rectangle([x0 + 12, y0 + 8, x0 + 108, y0 + 30], fill=(26, 26, 46))
    text(x0 + 60, y0 + 10, "LIV 4-0 MUN", f_small_b, WHITE, anchor="ma")
    # cricket bat + ball hint left-bottom
    d.line([(x0 + 250, y1 - 8), (x0 + 290, y1 - 40)], fill=(200, 170, 110),
           width=6)
    d.ellipse([x0 + 296, y1 - 46, x0 + 308, y1 - 34], fill=(176, 30, 40))

SCENES = {
    "train": scene_train, "tanker": scene_tanker, "capitol": scene_capitol,
    "eu": scene_eu, "pagoda": scene_pagoda, "fire": scene_fire,
    "sea_blast": scene_sea_blast, "chart": scene_chart, "footy": scene_footy,
}

# Pre-render every region scene once on a 490x56 canvas, so the layout can
# shrink the scene strip without redrawing (and without coordinate breaks).
_scene_imgs = {}
for _name, _fn in SCENES.items():
    _tmp = Image.new("RGB", (490, 56), PAPER)
    _old_d = d
    d = ImageDraw.Draw(_tmp, "RGBA")
    _fn(0, 0, 490, 56)
    d = _old_d
    _scene_imgs[_name] = _tmp

# ------------------------------------------------------------------ data
# Counts are honest: headline story + bullets below it.
REGIONS = [
 dict(name="SOUTH ASIA", color=(198, 90, 30), scene="train",
      headline="Modi, Nepal PM flag off Saryu-Kamala Express to Janakpur",
      bullets=[
       "Nepal PM Balendra Shah on first India visit; talks on energy, trade, hydropower",
       "India-China end 10-day Corps Commander talks to ease LAC tensions in Arunachal",
       "Amit Shah in Arunachal: border villages push, 40 see reverse migration",
       "Congress-SP seat-sharing talks likely today",
       "Tata Sons: go public or stay private - decision expected this week",
       "India-EU free trade pact likely signed Dec 16 in Brussels",
       "IFFI 2026 hosts BRICS Roundtable; restored classics showcased",
       "Tainted alcohol kills 11 in Manipur",
       "ICJ Myanmar verdict: Rohingya hail 'small victory'; Myanmar rejects ruling",
      ]),
 dict(name="MIDDLE EAST", color=TEAL, scene="tanker",
      headline="Gulf on fire: tankers hit, Bahrain struck, blockade showdown looms",
      bullets=[
       "Bahrain intercepts Iranian attacks; civilian facility struck, fire, no casualties",
       "IRGC: two 'violating' supertankers hit mines east of Hormuz - CLAIM",
       "US struck tanker exporting Iranian oil near blockade line - unconfirmed",
       "Houthis claim strikes on Saudi oil refinery + radar, at least 6 injured",
       "Netanyahu-Eisenkot coalition talks end without deal on Israel government",
       "Settler arson attacks on Palestinian villages; Eisenkot calls it 'Jewish terrorism'",
       "US + Israel hold joint operational plans; no decision on escalation yet",
       "CENTCOM: helped Gulf states export 1.5bn barrels via Hormuz since summer",
      ]),
 dict(name="US / AMERICAS", color=(43, 76, 155), scene="capitol",
      headline="Democrats' historic House win: biggest majority since 1992",
      bullets=[
       "Trump vows to work with Democrats to cap credit card interest at 10%",
       "Father + daughter detained by masked ICE officers on Seattle jet bridge",
       "Pentagon moves to restrict US-Canada defence ties",
       "San Francisco braces for exceptionally high king tides; flood risk",
       "Nvidia CEO Jensen Huang's exit + SEC probe turmoil",
       "AI brain drain: ~90% of Indian-educated elite AI researchers went abroad",
       "Princeton student Eva Yi Xie detained amid US suspicion of Chinese tech access",
       "Thanksgiving week: markets shut Thu, early close Fri; PCE + GDP Wed",
      ]),
 dict(name="EUROPE", color=(122, 31, 61), scene="eu",
      headline="EU led 130-country bloc that rejected the COP31 draft",
      bullets=[
       "Ex-UK PM Theresa May: 'move on' from Brexit; 'aghast' at rejoin talk",
       "Thousands march in Lisbon as living costs fuel anger",
       "Enraged young protesters take the streets of Europe",
       "India-EU free trade pact signing set for Dec 16 in Brussels",
       "Drones attack Russian cargo ship in Gulf of Finland; ship still on fire",
       "EU: 'We will not endorse a deal that does not even mention fossil fuels'",
      ]),
 dict(name="EAST ASIA", color=(166, 43, 43), scene="pagoda",
      headline="Kim: North Korea seeks security, not supremacy",
      bullets=[
       "South Korea's Lee: speed is decisive in the AI race",
       "China exchanges cut margin ratio 100% to 80% from Nov 30",
       "China produces AI talent, America acquires it, India loses it",
       "Kospi -3.5%, Hang Seng slides as AI rout spreads across Asia",
      ]),
 dict(name="SOUTHEAST ASIA & PACIFIC", color=(46, 125, 50), scene="fire",
      headline="7 body bags found, 50 missing after Indonesian factory fire",
      bullets=[
       "Myanmar calls ASEAN review of peace plan 'unfair and imbalanced'",
       "COP31 co-chair Australia: Bowen calls outcome 'very disappointing'",
       "Albanese blames fossil-fuel fault lines for the collapse",
      ]),
 dict(name="AFRICA", color=(141, 90, 43), scene="sea_blast",
      headline="Sea drones hit Russian warship at Benghazi naval base, Libya",
      bullets=[
       "Drone strikes hit homes + a UN building in Sudan's capital",
       "COP32 goes to Addis Ababa, Ethiopia",
       "'Worst ever COP': Power Shift Africa says collapse must be a wake-up call",
      ]),
 dict(name="BUSINESS / MARKETS", color=(138, 109, 27), scene="chart",
      headline="Nasdaq -5.28% Friday, worst week since Covid crash",
      bullets=[
       "Monday whipsaw: GIFT Nifty pointed up, Sensex slipped at open; US futures +2.8%",
       "Nvidia -14% Friday to $125.53 after reported SEC probe; ~$491bn erased in a day",
       "Bitcoin ~$55,252 Sat, lowest since Sep 2024; back above $60,000",
       "Anthropic IPO: +17% debut Thu, then -11% Friday",
       "JPM now expects Fed rate HIKES in Dec, Jan, Mar",
       "Paolo Bulgari dies at 89; built a family silversmith shop into a luxury empire",
       "Opposition protests hit Meta offices in India",
       "Oil: Brent ~$93 on Hormuz risk, down from $110+ a month ago",
      ]),
 dict(name="SPORT / CULTURE", color=(158, 27, 50), scene="footy",
      headline="Liverpool hammer ten-man United 4-0 in Pochettino's debut",
      bullets=[
       "Day 5, 1st Test: IND 720/9d, NZ 368 & 202/5 - Conway 59* firm; no result yet",
       "Verstappen wins Las Vegas GP, holding off Norris; 35 lead changes",
       "Gukesh draws black for Game 1 (Tue) vs Sindarov - youngest title match ever",
       "India women crush Thailand 7-0, stay top of Asian Champions Trophy hockey",
       "Anupama retains IBSF World Women's Snooker title in Indore, beats So Man Yan 3-1",
       "Pakistan A beat India A by 48 runs in Asia Cup Rising Stars, Doha",
       "Mohun Bagan top ISL table after nervy 2-1 win at Churchill Brothers",
      ]),
]

LEAD_SUB = [
    ("Guterres: ", "\"deeply disappointing\" - 'no ambiguity in the science'"),
    ("EU: ", "\"hijacked by some oil states\" - Ireland's O'Brien"),
    ("Next: ", "COP32 in Addis Ababa; China calls it a 'deep disappointment'"),
]

# ------------------------------------------------------------------ layout
GRID_TOP = 302
GRID_BOT = 1006
COL_W = 490
COL_X = [14, 520]

def block_height(reg, scene_h, lead_px):
    w_ = COL_W - 16
    hl = wrap(reg["headline"], f_head, w_)
    hgt = 18 + scene_h + 4 + len(hl) * 14 + 3
    for b in reg["bullets"]:
        hgt += len(wrap(b, f_bullet, w_ - 12)) * lead_px
    return hgt

LEFT_COL = ["SOUTH ASIA", "MIDDLE EAST", "EUROPE", "SPORT / CULTURE"]
RIGHT_COL = ["US / AMERICAS", "EAST ASIA", "SOUTHEAST ASIA & PACIFIC",
             "AFRICA", "BUSINESS / MARKETS"]

def fit_columns(scene_h, lead_px):
    """Explicit balanced assignment (measured actual heights)."""
    by_name = {r["name"]: r for r in REGIONS}
    cols = []
    hs = []
    for names in (LEFT_COL, RIGHT_COL):
        col = [(by_name[n], block_height(by_name[n], scene_h, lead_px))
               for n in names]
        cols.append(col)
        hs.append(sum(h for _, h in col) + 6 * len(col))
    return cols, max(hs)

scene_h, lead_px = 32, 11
cols, need = fit_columns(scene_h, lead_px)
while need > (GRID_BOT - GRID_TOP) and scene_h > 30:
    scene_h -= 2
    cols, need = fit_columns(scene_h, lead_px)
while need > (GRID_BOT - GRID_TOP) and lead_px > 10.5:
    lead_px -= 0.5
    cols, need = fit_columns(scene_h, lead_px)
print("scene_h", scene_h, "leading", lead_px, "col heights", need,
      "avail", GRID_BOT - GRID_TOP)

# ---------------------------------------------------------------- masthead
d.rectangle([0, 0, W, 80], fill=PAPER)
text(14, 6, "THE WORLD IN ONE DAY", f_mast, INK)
text(1010, 10, "MONDAY 23 NOVEMBER 2026", f_mast_sm, INK, anchor="ra")
text(1010, 40, "66 STORIES  ·  9 REGIONS  ·  ONE DAY", f_small_b, RED, anchor="ra")
d.line([(14, 76), (1010, 76)], fill=INK, width=2)
d.line([(14, 80), (1010, 80)], fill=INK, width=1)

# ---------------------------------------------------------------- lead
LX0, LY0, LX1, LY1 = 14, 86, 1010, 268
scene_cop31(LX0, LY0, 500, LY1)
d.rectangle([500, LY0, LX1, LY1], fill=PAPER)
d.rectangle([500, LY0, 506, LY1], fill=RED)
text(518, LY0 + 4, "LEAD  ·  CLIMATE", f_kick, RED)
text(518, LY0 + 20, "COP31", f_lead, RED)
text(518, LY0 + 60, "COLLAPSES", f_lead, RED)
text(518, LY0 + 106, "No deal in Antalya", f_lead2, INK)
y = LY0 + 138
for lab, rest in LEAD_SUB:
    lines = wrap(lab + rest, f_sub, LX1 - 518 - 6)
    for ln in lines:
        text(518, y, ln, f_sub, INK)
        y += 14
    y += 1

# ---------------------------------------------------------------- strip
SY0, SY1 = 272, 296
d.rectangle([14, SY0, 1010, SY1], fill=TEAL)
text(24, SY0 + 5, "GULF ON FIRE — Iran 'reported' to send 14 tankers to test the US blockade; "
                   "Trump: 'bottom of the sea'", f_strip, WHITE)
text(1010 - 12, SY0 + 5, "CLAIM: plan unconfirmed", f_small_b, (255, 220, 120),
     anchor="ra")

# ---------------------------------------------------------------- regions
def draw_region(reg, x0, y0, hgt):
    x1 = x0 + COL_W
    d.rectangle([x0, y0, x1, y0 + 18], fill=reg["color"])
    text(x0 + 8, y0 + 2, reg["name"], f_small_b, WHITE)
    n = 1 + len(reg["bullets"])
    text(x1 - 8, y0 + 2, str(n), f_small_b, WHITE, anchor="ra")
    sy0 = y0 + 18
    img.paste(_scene_imgs[reg["scene"]].resize((COL_W, scene_h), Image.LANCZOS),
              (x0, sy0))
    d.rectangle([x0, sy0 + scene_h, x1, sy0 + scene_h + 1], fill=(26, 26, 46))
    yy = sy0 + scene_h + 5
    for ln in wrap(reg["headline"], f_head, COL_W - 16):
        text(x0 + 8, yy, ln, f_head, INK)
        yy += 14
    yy += 3
    for b in reg["bullets"]:
        for ln in wrap(b, f_bullet, COL_W - 16 - 12):
            d.rectangle([x0 + 8, yy + 4, x0 + 13, yy + 9], fill=reg["color"])
            text(x0 + 18, yy, ln, f_bullet, INK)
            yy += lead_px
    return int(yy)

for ci, col in enumerate(cols):
    y = GRID_TOP
    for reg, hgt in col:
        y = draw_region(reg, COL_X[ci], y, hgt)
        y += 6

# ---------------------------------------------------------------- footer
d.line([(14, 1010), (1010, 1010)], fill=INK, width=1)
text(14, 1013, "Stories as reported on 23 November 2026  ·  The Hindu  ·  CNN  ·  Reuters  ·  "
                "Gulf News  ·  Moneycontrol  ·  The Hindu Morning Digest",
     f_foot, GREY)

img.save("entry.png", optimize=True)
import os
print("saved entry.png", os.path.getsize("entry.png"), "bytes")
total = 1 + sum(1 + len(r["bullets"]) for r in REGIONS)  # lead + regions
print("stories:", total)
for r in REGIONS:
    print(" ", r["name"], 1 + len(r["bullets"]))
