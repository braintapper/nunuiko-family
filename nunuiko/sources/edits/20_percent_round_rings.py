"""Glyph edit 20: % with round rings (shared by Nunuiko and Display).

Stock Nunito / Nunito Sans draw the % rings as tall ovals (326 x 431 at
ExtraLight), narrower than an o. Each ring becomes a circle as wide as
the old ring, with an even stroke all round (the old ring's side
thickness), so its counter is a circle too. The upper ring keeps its top,
the lower ring its bottom, both keep their centre across; the slash, the
advance and the per mille sign are unchanged. In the italic the circles
are drawn unslanted and then slanted, like the rest of the glyph.

Each ring keeps its 12 nodes (4 quarter arcs) in the same order and
direction; every node is redrawn on the circle by its role (right, top,
left, bottom), so masters stay compatible. If a heavy master's stroke
would leave a counter under MIN_COUNTER x the ring's radius, the stroke is
thinned to keep it.

Run once per source from sources/:
  python3 edits/20_percent_round_rings.py [file.glyphs]
"""
import glob
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("*.glyphs"))[0]
KAPPA = 0.5522847498
MIN_COUNTER = 0.35


def main():
    font = GSFont(GLYPHS_FILE)
    angles = {m.name: m.italicAngle for m in font.masters}

    def edit(mname, layer, nodes):
        tan = math.tan(math.radians(angles[mname]))
        paths = layer.paths
        assert len(paths) == 5, (mname, len(paths))
        un = [[(n.position.x - n.position.y * tan, n.position.y, n.type) for n in p.nodes]
              for p in paths]
        rings = [i for i, p in enumerate(un) if len(p) == 12]
        assert len(rings) == 4, mname

        def box(i):
            on = [(u, y) for u, y, t in un[i] if t != "offcurve"]
            us, ys = [u for u, _ in on], [y for _, y in on]
            return min(us), min(ys), max(us), max(ys)

        by_y = sorted(rings, key=lambda i: -(box(i)[1] + box(i)[3]))
        pairs = [sorted(by_y[:2], key=lambda i: box(i)[2] - box(i)[0], reverse=True),
                 sorted(by_y[2:], key=lambda i: box(i)[2] - box(i)[0], reverse=True)]
        out, starts, base = {}, [], 0
        for p in un:
            starts.append(base)
            base += len(p)
        info = []
        for upper, (o, i) in zip((True, False), pairs):
            bo, bi = box(o), box(i)
            r = (bo[2] - bo[0]) / 2
            t = bi[0] - bo[0]
            t = min(t, (1 - MIN_COUNTER) * r)
            cx = (bo[0] + bo[2]) / 2
            cy = bo[3] - r if upper else bo[1] + r
            for ci, rad in ((o, r), (i, r - t)):
                b = box(ci)
                ocx, ocy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
                pts = un[ci]
                on = [k for k in range(12) if pts[k][2] != "offcurve"]
                assert len(on) == 4
                # the first on-curve node's role by its angle, the rest in
                # path order (counter-clockwise: right, top, left, bottom)
                P = [pts[k][:2] for k in on]
                ccw = sum(P[j][0] * P[(j + 1) % 4][1] - P[(j + 1) % 4][0] * P[j][1]
                          for j in range(4)) > 0
                q0 = round(math.atan2(P[0][1] - ocy, P[0][0] - ocx) / (math.pi / 2))
                dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                unit = {k: dirs[(q0 + (j if ccw else -j)) % 4] for j, k in enumerate(on)}
                pos = {k: (cx + rad * unit[k][0], cy + rad * unit[k][1]) for k in on}
                for j, k in enumerate(on):
                    nk = on[(j + 1) % 4]
                    h1, h2 = (k + 1) % 12, (k + 2) % 12
                    assert pts[h1][2] == pts[h2][2] == "offcurve" and (k + 3) % 12 == nk
                    a, bb = unit[k], unit[nk]
                    pos[h1] = (pos[k][0] + KAPPA * rad * bb[0], pos[k][1] + KAPPA * rad * bb[1])
                    pos[h2] = (pos[nk][0] + KAPPA * rad * a[0], pos[nk][1] + KAPPA * rad * a[1])
                for k, (u, y) in pos.items():
                    out[starts[ci] + k] = (u + y * tan, y)
            info.append(f"{'upper' if upper else 'lower'} {2 * r:.0f} ⌀ (was {bo[3] - bo[1]:.0f} tall), stroke {t:.0f}")
        print(f"  {mname:32s} " + "; ".join(info))
        return {"nodes": out}

    changed = apply_edit(GLYPHS_FILE, "percent", edit)
    print("written" if changed else "unchanged", GLYPHS_FILE)


if __name__ == "__main__":
    main()
