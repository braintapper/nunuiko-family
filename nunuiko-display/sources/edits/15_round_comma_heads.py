"""Glyph edit 15: round heads on commas and quotes, as in Nunuiko.

Nunito Sans draws the comma, the quotes ' ' , and the comma accents as a
square head with a tail curving out of one side. Edit 10 made the dots
round; this does the same for these heads, so , ; ' ' ‚ " " „ and the
comma accents (ģ ķ ļ ņ ŗ ș ț ...) match the round period, as Nunuiko's do.

Which contours: a path has a square head when, in EVERY master, it has
this run of nodes: E (the tail's outer curve ending on the head's side),
C1 C2 C3 (three line corners: C1-C2 horizontal, C2-C3 vertical or at the
italic angle, aspect 0.6-1.7), P (a line node on the edge after C3) and N
(the line node of the notch where the tail's inner edge leaves the head).
Turned forms (quoteleft, the turned comma above) are the same run rotated.

Operation, per master: C1 C2 C3 P are replaced by a circle, sized as edit
10's dots (same area as a square of side sqrt(w*h), capped at 1.128x the
height) and centred on the head's centre (midpoint of C1 and C3). The
circle starts at E's side: E moves onto it and its incoming handle is
turned to the circle's tangent there (same length), so the tail flows
into the head smoothly. Three quarter arcs then go round to the side
opposite C3 -> P, which joins N by a line, as in Nunuiko's comma. Heads
stay round in the italic (not slanted). The path is rewritten starting at
N, the same in every master, so masters stay compatible.

Composites (quotedbl*, the accented letters) follow.
Run once per source:
  python3 edits/15_round_comma_heads.py
  python3 edits/15_round_comma_heads.py NunuikoDisplay-Italic.glyphs
Add --dry-run to list the heads without writing.
"""
import math
import re
import sys

from glyphsLib import GSFont

args = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY = "--dry-run" in sys.argv
GLYPHS_FILE = args[0] if args else "NunuikoDisplay.glyphs"
KAPPA = 0.5522847498
AREA = 2 / math.sqrt(math.pi)  # circle diameter / square side, equal area
SLANT_TOL = 1.5  # degrees from the italic angle
NODES_RE = re.compile(r"nodes = \(\n(.*?)\n\);", re.S)
TOKEN_RE = re.compile(r"\(-?[\d.]+,-?[\d.]+,(?:o|c|cs|l|ls|q|qs)\)")


def head(path, italic_angle):
    """(i, c, a, b, r) for a square head whose E node is at index i: centre
    c, a = unit vector toward E's side, b = toward the first arc's end;
    else None."""
    n = path.nodes
    m = len(n)
    P = [(q.position.x, q.position.y) for q in n]
    T = [q.type for q in n]
    for i in range(m):
        e, c1, c2, c3, p, nn = (P[(i + k) % m] for k in range(6))
        if T[i] != "curve" or any(T[(i + k) % m] != "line" for k in range(1, 6)):
            continue
        if abs(c1[1] - c2[1]) > 0.5 or abs(p[1] - c3[1]) > 0.5:
            continue
        w, h = abs(c1[0] - c2[0]), abs(c2[1] - c3[1])
        if h <= 0 or not 0.6 < w / h < 1.7:
            continue
        top, bot = (c2, c3) if c2[1] > c3[1] else (c3, c2)
        slant = math.degrees(math.atan2(top[0] - bot[0], top[1] - bot[1]))
        if abs(slant - italic_angle) > SLANT_TOL:
            continue
        # E on C1's side edge (the line through C1 parallel to C2-C3)
        sx, sy = c2[0] - c3[0], c2[1] - c3[1]
        if abs((e[0] - c1[0]) * sy - (e[1] - c1[1]) * sx) / math.hypot(sx, sy) > 1:
            continue
        a = (math.copysign(1, c1[0] - c2[0]), 0.0)
        b = (0.0, math.copysign(1, c2[1] - c3[1]))
        c = ((c1[0] + c3[0]) / 2, (c1[1] + c3[1]) / 2)
        d = min(AREA * math.sqrt(w * h), AREA * h)
        return i, c, a, b, d / 2
    return None


def rebuild(tokens, path, shape):
    """New node lines: N ... H, E', three quarter arcs."""
    i, c, a, b, r = shape
    m = len(tokens)
    k = r * KAPPA
    pt = lambda u: (c[0] + r * u[0], c[1] + r * u[1])
    neg = lambda u: (-u[0], -u[1])
    fmt = lambda xy, code: f"({round(xy[0])},{round(xy[1])},{code})"
    out = [tokens[(i + 5 + j) % m] for j in range(m - 5)]  # N .. H
    hx, hy = path.nodes[(i - 1) % m].position.x, path.nodes[(i - 1) % m].position.y
    ex, ey = path.nodes[i].position.x, path.nodes[i].position.y
    e2 = pt(a)
    hl = math.hypot(hx - ex, hy - ey)
    out[-1] = fmt((e2[0] - b[0] * hl, e2[1] - b[1] * hl), "o")  # H on the tangent
    out.append(fmt(e2, "cs"))
    for u, v in ((a, b), (b, neg(a)), (neg(a), neg(b))):
        p0, p1 = pt(u), pt(v)
        out += [fmt((p0[0] + k * v[0], p0[1] + k * v[1]), "o"),
                fmt((p1[0] + k * u[0], p1[1] + k * u[1]), "o"),
                fmt(p1, "cs")]
    return out


def main():
    text = open(GLYPHS_FILE).read()
    font = GSFont(GLYPHS_FILE)
    masters = {m.id: m for m in font.masters}
    total = 0
    for g in font.glyphs:
        layers = [l for l in g.layers if l.layerId in masters]
        if len(layers) != len(masters):
            continue
        npaths = {len(l.paths) for l in layers}
        if len(npaths) != 1:
            continue
        heads = {}
        for ci in range(npaths.pop()):
            shapes = [head(l.paths[ci], masters[l.layerId].italicAngle) for l in layers]
            if all(shapes) and len({s[0] for s in shapes}) == 1 \
                    and len({len(l.paths[ci].nodes) for l in layers}) == 1:
                heads[ci] = shapes
        if not heads:
            continue
        total += len(heads)
        print(f"{g.name:30s} heads at contour {sorted(heads)}"
              f"  r {min(s[4] for s in heads[min(heads)]):.0f}..{max(s[4] for s in heads[min(heads)]):.0f}")
        if DRY:
            continue

        marker = f"glyphname = {g.name};"
        if marker not in text:
            marker = f'glyphname = "{g.name}";'
        bs = text.index(marker)
        be = text.index("\nglyphname = ", bs + 1) if "\nglyphname = " in text[bs + 1:] else len(text)
        block = text[bs:be]
        for li, l in enumerate(layers):
            ls = block.index(f'layerId = "{l.layerId}";')
            le = re.compile(r"\nwidth = ").search(block, ls).start()
            region = block[ls:le]
            found = list(NODES_RE.finditer(region))
            assert len(found) == len(l.paths), (g.name, l.layerId, len(found))
            pieces, prev = [], 0
            for ci, mt in enumerate(found):
                pieces.append(region[prev:mt.start()])
                if ci in heads:
                    tokens = mt.group(1).split(",\n")
                    assert len(tokens) == len(l.paths[ci].nodes) \
                        and all(TOKEN_RE.fullmatch(t) for t in tokens), (g.name, tokens)
                    new = rebuild(tokens, l.paths[ci], heads[ci][li])
                    pieces.append("nodes = (\n" + ",\n".join(new) + "\n);")
                else:
                    pieces.append(mt.group(0))
                prev = mt.end()
            pieces.append(region[prev:])
            block = block[:ls] + "".join(pieces) + block[le:]
        text = text[:bs] + block + text[be:]
    print(f"{total} head contours" + (" (dry run)" if DRY else ""))
    if not DRY:
        open(GLYPHS_FILE, "w").write(text)
        print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
