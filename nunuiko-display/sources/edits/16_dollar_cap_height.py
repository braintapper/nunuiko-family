"""Glyph edit 16: $ no taller than the S (shared by Nunuiko and Display).

The $ is an S with the bar sticking out above and below it (Nunuiko
-121..826, Display -115..820 at ExtraLight, against the S's -8..713). It
is scaled down uniformly until its full height, bar ends included, is the
S's own (overshoots included), so the S in it is smaller than a regular
S and the $ sits between the baseline and the cap height. Nunuikode does
the same in its code edit 6.

Stroke weight is kept: scaling by s would thin every stroke by (1-s) x
the stem, so each on-curve point also moves out along its outward normal
by (1-s) x stem / 2 on each axis (ramped near the diagonal), handles
following their on-curve point. The stem is the I's, per master. So
s = (S height - stem) / ($ height - stem).

The $ stays centred where it was across, on its advance, which doesn't
change: like the figures, it is tabular-width. Done unslanted
(x - y tan(italic angle)) in the italic. No composite uses the $.

Run once per source from sources/ (any source; defaults to this folder's):
  python3 edits/16_dollar_cap_height.py [file.glyphs]
"""
import glob
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("*.glyphs"))[0]


def unslanted(layer, tan):
    return [[(n.position.x - n.position.y * tan, n.position.y, n.type != "offcurve")
             for n in p.nodes] for p in layer.paths]


def ybounds(paths):
    ys = [y for p in paths for _, y, on in p if on]
    return min(ys), max(ys)


def main():
    font = GSFont(GLYPHS_FILE)
    for g in font.glyphs:
        for l in g.layers:
            assert not any(c.name == "dollar" for c in l.components), g.name
    masters = {m.name: m for m in font.masters}
    ids = {m.name: m.id for m in font.masters}

    def edit(mname, layer, nodes):
        tan = math.tan(math.radians(masters[mname].italicAngle))
        mid = ids[mname]
        ipaths = unslanted(font.glyphs["I"].layers[mid], tan)
        us = [u for p in ipaths for u, _, on in p if on]
        stem = max(us) - min(us)
        lo, hi = ybounds(unslanted(font.glyphs["S"].layers[mid], tan))
        paths = unslanted(layer, tan)
        y0, y1 = ybounds(paths)
        allu = [u for p in paths for u, _, on in p if on]
        cx = (min(allu) + max(allu)) / 2
        s = (hi - lo - stem) / (y1 - y0 - stem)
        ny = lo + (1 - s) * stem / 2
        clamp = lambda v: max(-1.0, min(1.0, v / 0.3))
        out, base = {}, 0
        for p in paths:
            n = len(p)
            d = [(0.0, 0.0)] * n
            for k in range(n):
                if p[k][2]:
                    (px, py), (qx, qy) = p[(k - 1) % n][:2], p[(k + 1) % n][:2]
                    tx, ty = qx - px, qy - py
                    ln = math.hypot(tx, ty) or 1.0
                    # outward normal (ty, -tx) for Glyphs' counter-clockwise outer paths
                    d[k] = ((1 - s) * stem / 2 * clamp(ty / ln),
                            (1 - s) * stem / 2 * clamp(-tx / ln))
            for k in range(n):
                if not p[k][2]:
                    d[k] = d[(k - 1) % n] if p[(k - 1) % n][2] else d[(k + 1) % n]
            for k, (u, y, _) in enumerate(p):
                yy = ny + (y - y0) * s + d[k][1]
                out[base + k] = (cx + (u - cx) * s + d[k][0] + yy * tan, yy)
            base += n
        print(f"  {mname:32s} stem {stem:.0f}  $ {y0:.0f}..{y1:.0f} -> S {lo:.0f}..{hi:.0f}  scale {s:.3f}")
        return {"nodes": out}

    changed = apply_edit(GLYPHS_FILE, "dollar", edit)
    print("written" if changed else "unchanged", GLYPHS_FILE)


if __name__ == "__main__":
    main()
