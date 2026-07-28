#!/usr/bin/env python3
"""Vygeneruje apple-touch-icon.png bez externích knihoven.

iOS si ikonu sám maskuje do squircle, takže kreslíme celou plochu.
"""
import struct, zlib, sys, math

N = 180
BG = (14, 22, 38)
FG = (103, 212, 255)

px = [[BG for _ in range(N)] for _ in range(N)]


def blend(x, y, color, a):
    if not (0 <= x < N and 0 <= y < N) or a <= 0:
        return
    a = min(1.0, a)
    old = px[y][x]
    px[y][x] = tuple(round(old[i] * (1 - a) + color[i] * a) for i in range(3))


def seg(x1, y1, x2, y2, w, color=FG):
    """Úsečka s tloušťkou a jemným antialiasem podle vzdálenosti od osy."""
    dx, dy = x2 - x1, y2 - y1
    ln2 = dx * dx + dy * dy
    half = w / 2.0
    xs = range(max(0, int(min(x1, x2) - w)), min(N, int(max(x1, x2) + w) + 1))
    ys = range(max(0, int(min(y1, y2) - w)), min(N, int(max(y1, y2) + w) + 1))
    for y in ys:
        for x in xs:
            if ln2 == 0:
                d = math.hypot(x - x1, y - y1)
            else:
                t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / ln2))
                d = math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
            if d <= half - 0.5:
                blend(x, y, color, 1.0)
            elif d < half + 0.5:
                blend(x, y, color, half + 0.5 - d)


# domeček: střecha, boky, podlaha, dveře
W = 11
seg(30, 88, 90, 40, W)
seg(90, 40, 150, 88, W)
seg(46, 84, 46, 146, W)
seg(134, 84, 134, 146, W)
seg(46, 146, 134, 146, W)
seg(76, 146, 76, 112, W)
seg(76, 112, 104, 112, W)
seg(104, 112, 104, 146, W)

raw = b"".join(b"\x00" + b"".join(bytes(px[y][x]) for x in range(N)) for y in range(N))


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


png = (b"\x89PNG\r\n\x1a\n" +
       chunk(b"IHDR", struct.pack(">IIBBBBB", N, N, 8, 2, 0, 0, 0)) +
       chunk(b"IDAT", zlib.compress(raw, 9)) +
       chunk(b"IEND", b""))

out = sys.argv[1] if len(sys.argv) > 1 else "apple-touch-icon.png"
open(out, "wb").write(png)
print("OK %s  %dx%d  %d B" % (out, N, N, len(png)))
