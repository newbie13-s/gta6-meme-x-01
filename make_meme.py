#!/usr/bin/env python3
"""make_meme.py — draws the gta6-meme-x-01 meme picture, deterministically.

The joke: GTA fans waited thirteen years between GTA V (2013) and GTA 6.
In the picture the make.fun ghost — white body, thick black outline, two
black four-pointed sparkle eyes, one round little hand holding a magenta
coin with a white star — is already in Leonida at sunset, coin in hand:
while everyone else waited, the ghost's AI agent was winning bounties.

Everything is drawn with PIL primitives on a 2x canvas and downscaled, so
the output is byte-for-byte identical on every run (fixed seed, no clock,
no network). Output: meme.png next to this file (1200x1200).

Run:  python3 make_meme.py
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample factor
W, H = 1200 * S, 1200 * S
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OUT = Path(__file__).resolve().parent / "meme.png"


def font(px: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, px * S)


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def mix(c1, c2, t):
    return tuple(lerp(x, y, t) for x, y in zip(c1, c2))


def sky(draw: ImageDraw.ImageDraw) -> None:
    """Vice City sunset: deep purple up top, magenta, then orange."""
    horizon = int(760 * S)
    stops = [(0.0, (43, 10, 74)), (0.55, (181, 23, 158)), (1.0, (255, 120, 71))]
    for y in range(horizon):
        t = y / horizon
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                col = mix(c0, c1, (t - t0) / (t1 - t0))
                break
        draw.line([(0, y), (W, y)], fill=col)
    # the ground: dark Leonida street/sea band under the horizon
    draw.rectangle([0, horizon, W, H], fill=(18, 6, 31))
    # neon reflections on the wet ground, fixed pattern
    rng = random.Random(20261119)
    for _ in range(46):
        y = rng.randint(horizon + 14 * S, 985 * S)
        x = rng.randint(0, W - 260 * S)
        ln = rng.randint(60 * S, 240 * S)
        col = rng.choice([(255, 46, 154), (255, 120, 71), (255, 210, 63)])
        draw.line([(x, y), (x + ln, y)], fill=col, width=3 * S)


def stars(draw: ImageDraw.ImageDraw) -> None:
    rng = random.Random(613)
    for _ in range(70):
        x = rng.randint(10 * S, W - 10 * S)
        y = rng.randint(280 * S, 560 * S)
        r = rng.randint(2 * S, 4 * S)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 250))


def sun(draw: ImageDraw.ImageDraw) -> None:
    cx, cy, r = 420 * S, 690 * S, 175 * S
    for grow, col in [(70, (255, 94, 98)), (40, (255, 140, 80)), (0, (255, 210, 63))]:
        rr = r + grow * S
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    # retro sun stripes near the bottom of the disc
    for i, dy in enumerate([70, 105, 135]):
        y = cy + dy * S
        draw.rectangle([cx - r, y, cx + r, y + (8 + i * 4) * S], fill=(255, 120, 71))


def skyline(draw: ImageDraw.ImageDraw) -> None:
    """Dark Leonida rooftops along the horizon, two lit signs on top."""
    base = 762 * S
    rng = random.Random(42)
    x = -10 * S
    dark = (29, 11, 51)
    while x < W:
        bw = rng.randint(55 * S, 120 * S)
        bh = rng.randint(45 * S, 130 * S)
        draw.rectangle([x, base - bh, x + bw, base], fill=dark)
        for _ in range(rng.randint(2, 7)):  # lit windows
            wx = rng.randint(int(x) + 6 * S, int(x + bw) - 12 * S)
            wy = rng.randint(int(base - bh) + 6 * S, int(base) - 14 * S)
            draw.rectangle([wx, wy, wx + 6 * S, wy + 8 * S], fill=(255, 214, 120))
        x += bw + rng.randint(4 * S, 18 * S)
    # street-level neon sign on the dark ground band: the make.fun
    # wordmark, worked into the scene, clear of palms, ghost and captions
    sign_w, sign_h = 370 * S, 92 * S
    sx, sy = 60 * S, 806 * S
    draw.rectangle([sx + sign_w // 2 - 6 * S, sy + sign_h, sx + sign_w // 2 + 6 * S, 992 * S], fill=dark)
    draw.rectangle([sx, sy, sx + sign_w, sy + sign_h], fill=(24, 4, 36), outline=(255, 46, 154), width=5 * S)
    f = font(62)
    txt = "make.fun"
    box = draw.textbbox((0, 0), txt, font=f)
    tw, th = box[2] - box[0], box[3] - box[1]
    draw.text((sx + (sign_w - tw) / 2 - box[0], sy + (sign_h - th) / 2 - box[1]),
              txt, font=f, fill=(255, 120, 205))


def palm(draw: ImageDraw.ImageDraw, x: int, base: int, h: int, lean: int) -> None:
    col = (18, 7, 30)
    top_x, top_y = x + lean, base - h
    steps = 26
    prev = (x, base)
    for i in range(1, steps + 1):
        t = i / steps
        px = x + lean * t * t
        py = base - h * t
        wdt = max(3 * S, int((1 - t) * 13 * S))
        draw.line([prev, (px, py)], fill=col, width=wdt)
        prev = (px, py)
    for ang in range(-170, -9, 18):  # fronds, arcing up then drooping down
        rad = math.radians(ang)
        ln = int(h * 0.55)
        ex = top_x + math.cos(rad) * ln
        ey = top_y + math.sin(rad) * ln * 0.45 + h * 0.30
        mx = top_x + math.cos(rad) * ln * 0.5
        my = top_y + math.sin(rad) * ln * 0.5 - h * 0.10
        pts = []
        for k in range(13):
            t = k / 12
            px = (1 - t) ** 2 * top_x + 2 * (1 - t) * t * mx + t * t * ex
            py = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * my + t * t * ey
            pts.append((px, py))
        draw.line(pts, fill=col, width=8 * S, joint="curve")
    draw.ellipse([top_x - 12 * S, top_y - 6 * S, top_x + 12 * S, top_y + 18 * S], fill=col)


def sparkle(cx: int, cy: int, r: int):
    """A four-pointed sparkle (the ghost's eye shape)."""
    pts = []
    inner = r * 0.30
    for k in range(8):
        ang = math.radians(45 * k - 90)
        rr = r if k % 2 == 0 else inner
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    return pts


def star(cx: int, cy: int, r: int):
    pts = []
    for k in range(10):
        ang = math.radians(36 * k - 90)
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    return pts


def ghost(draw: ImageDraw.ImageDraw) -> None:
    """The make.fun ghost, big, holding its magenta coin over the sunset."""
    cx, top = 800 * S, 300 * S
    half_w = 195 * S
    body_h = 470 * S
    bottom = top + body_h

    def outline(scale: float):
        hw = half_w * scale
        th = body_h * scale
        bt = top + th
        pts = []
        # left side up, dome over the top (semicircle), right side down
        for k in range(25):
            ang = math.radians(180 - k * (180 / 24))
            pts.append((cx + math.cos(ang) * hw, top + hw + math.sin(ang) * -hw))
        pts.append((cx + hw, bt - 46 * S * scale))
        # wavy hem: three scallops back to the left
        for seg in range(3):
            x0 = cx + hw - seg * (2 * hw / 3)
            for k in range(1, 13):
                t = k / 12
                px = x0 - t * (2 * hw / 3)
                py = (bt - 46 * S * scale) + math.sin(t * math.pi) * 40 * S * scale
                pts.append((px, py))
        pts.append((cx - hw, bt - 46 * S * scale))
        return pts

    draw.polygon(outline(1.055), fill=(10, 10, 14))       # thick black outline
    draw.polygon(outline(1.0), fill=(255, 255, 255))      # white body
    # sparkle eyes
    for ex in (cx - 78 * S, cx + 78 * S):
        draw.polygon(sparkle(ex, top + 185 * S, 52 * S), fill=(10, 10, 14))
    # the magenta coin, held low on the ghost's left
    coin_c = (cx - 235 * S, top + 415 * S)
    cr = 92 * S
    draw.ellipse([coin_c[0] - cr, coin_c[1] - cr, coin_c[0] + cr, coin_c[1] + cr],
                 fill=(255, 46, 154), outline=(146, 10, 84), width=7 * S)
    draw.polygon(star(coin_c[0], coin_c[1], 46 * S), fill=(255, 255, 255))
    # the round little hand, overlapping the coin's top edge
    hx, hy, hr = coin_c[0] + 62 * S, coin_c[1] - 72 * S, 40 * S
    draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(10, 10, 14))
    draw.ellipse([hx - hr + 8 * S, hy - hr + 8 * S, hx + hr - 8 * S, hy + hr - 8 * S],
                 fill=(255, 255, 255))


def caption(draw: ImageDraw.ImageDraw, lines, y: int, px: int, gap: int) -> int:
    for line in lines:
        size = px
        while size > 30:  # shrink until the line fits with a margin
            f = font(size)
            box = draw.textbbox((0, 0), line, font=f, stroke_width=7 * S)
            if box[2] - box[0] <= W - 48 * S:
                break
            size -= 4
        draw.text(((W - (box[2] - box[0])) / 2 - box[0], y), line, font=f,
                  fill=(255, 255, 255), stroke_width=7 * S, stroke_fill=(8, 4, 16))
        y += (size + gap) * S
    return y


def main() -> None:
    img = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    sky(draw)
    stars(draw)
    sun(draw)
    skyline(draw)
    palm(draw, 64 * S, 770 * S, 300 * S, 42 * S)
    palm(draw, 1085 * S, 770 * S, 265 * S, -48 * S)
    ghost(draw)
    caption(draw, ["13 YEARS WAITING", "FOR GTA 6"], 52 * S, 104, 18)
    caption(draw, ["MY AI AGENT GOT PAID IN BOUNTIES", "THE WHOLE TIME"],
            1008 * S, 62, 12)
    img = img.resize((1200, 1200), Image.LANCZOS)
    img.save(OUT, "PNG")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
