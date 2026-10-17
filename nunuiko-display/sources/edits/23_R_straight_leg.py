"""Glyph edit 23: R — the leg leaves the bowl straight, with no curved
transition (shared by Nunuiko and Display). Reference: Proxima Nova R.

Stock Nunito / Nunito Sans bend both edges of the R's leg into the
horizontal where it meets the bowl: the inner edge curves into the crotch
line under the bowl, the outer edge curves into the bowl's underside (with
a hidden notch). Here both edges run straight on until they meet:
  Inner edge: the straight part of the leg's inner edge (E -> the leg's
    foot) is extended up to the crotch line (the horizontal under the bowl,
    from the stem's inner side). The crotch line's end node moves to that
    point, a sharp corner, and the curve between them (2 handles + E) goes.
  Outer edge: the straight part of the leg's outer edge (from the foot up
    to its line node RE) is extended up until it crosses the bowl's outer
    curve. RE moves to that crossing, a sharp corner; the bowl's curve is
    split there and its upper part kept; the curve into the bowl and the
    notch (2 handles, a curve node and 2 line nodes) go.
Everything else (stem, bowl, counter, foot, advance) is kept; composites
(Ŕ Ř Ŗ ...) follow. Done in place: lines and their crossings don't care
about the italic slant. Nunito: 35 -> 27 nodes; Nunito Sans: 22 -> 14.

Run once per source from sources/:
  python3 edits/23_R_straight_leg.py [file.glyphs]
"""
import glob
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("*.glyphs"))[0]


def bez(p, t):
    s = 1 - t
    return tuple(s**3 * a + 3 * s * s * t * b + 3 * s * t * t * c + t**3 * d
                 for a, b, c, d in zip(*p))


def split(p, t):
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    p01, p12, p23 = lerp(p[0], p[1]), lerp(p[1], p[2]), lerp(p[2], p[3])
    a, b = lerp(p01, p12), lerp(p12, p23)
    c = lerp(a, b)
    return (p[0], p01, a, c), (c, b, p23, p[3])


def plan(nodes):
    m = len(nodes)
    P = [(n.position.x, n.position.y) for n in nodes]
    T = [n.type for n in nodes]
    nx = lambda i: (i + 1) % m
    # inner edge: crotch line end C (a line node after a line node at the same
    # y), 2 handles, E (curve), then the line to the foot F
    c = next(i for i in range(m) if T[i] == "line" and T[(i - 1) % m] == "line"
             and abs(P[i][1] - P[(i - 1) % m][1]) < 0.5 and P[i][0] > P[(i - 1) % m][0]
             and T[nx(i)] == T[nx(nx(i))] == "offcurve")
    e, f = nx(nx(nx(c))), nx(nx(nx(nx(c))))
    assert T[e] == "curve" and T[f] == "line" and P[f][1] < P[e][1], "inner edge"
    cy = P[c][1]
    ex, ey, fx, fy = *P[e], *P[f]
    cx = ex + (cy - ey) * (fx - ex) / (fy - ey)
    # outer edge: RE (line) after the foot, 2 handles, curve, line, line BO
    # (start of the bowl's outer curve), 2 handles, BE (end of it)
    re_ = next(i for i in range(m) if T[i] == "line"
               and [T[(i + k) % m] for k in range(1, 9)] ==
               ["offcurve", "offcurve", "curve", "line", "line", "offcurve", "offcurve", "curve"])
    bo, be = (re_ + 5) % m, (re_ + 8) % m
    a0, a1 = P[(re_ - 1) % m], P[re_]  # the straight outer edge
    bowl = (P[bo], P[(bo + 1) % m], P[(bo + 2) % m], P[be])
    side = lambda pt: (a1[0] - a0[0]) * (pt[1] - a0[1]) - (a1[1] - a0[1]) * (pt[0] - a0[0])
    lo, hi = 0.0, 1.0
    slo = side(bez(bowl, lo))
    assert slo * side(bez(bowl, hi)) < 0, "outer edge doesn't cross the bowl"
    for _ in range(60):
        mid = (lo + hi) / 2
        if side(bez(bowl, mid)) * slo > 0:
            lo = mid
        else:
            hi = mid
    _, keep = split(bowl, (lo + hi) / 2)
    x = keep[0]

    drop = {nx(c), nx(nx(c)), e} | {(re_ + k) % m for k in range(1, 6)}
    out = []
    for i in range(m):
        if i in drop:
            continue
        n = nodes[i]
        if i == c:
            out.append((cx, cy, "line", False))
        elif i == re_:
            out.append((x[0], x[1], "line", False))
        elif i == (bo + 1) % m:
            out.append((*keep[1], "offcurve", False))
        elif i == (bo + 2) % m:
            out.append((*keep[2], "offcurve", False))
        else:
            out.append((n.position.x, n.position.y, n.type, n.smooth))
    info = f"crotch {P[c][0]:.0f} -> {cx:.0f} at {cy:.0f}; leg meets the bowl at ({x[0]:.0f}, {x[1]:.0f}); {m} -> {len(out)} nodes"
    return out, info


def main():
    font = GSFont(GLYPHS_FILE)

    def edit(mname, layer, nodes):
        assert len(layer.paths) == 2, mname
        n0 = len(layer.paths[0].nodes)
        out, info = plan(nodes[:n0])
        print(f"  {mname:32s} {info}")
        return {"replace_nodes": out, "path": 0}

    changed = apply_edit(GLYPHS_FILE, "R", edit)
    print("written" if changed else "unchanged", GLYPHS_FILE)


if __name__ == "__main__":
    main()
