"""Glyph edit 22: & — the arm stops a little past the diagonal (shared by
Nunuiko and Display).

Stock Nunito / Nunito Sans run the &'s right arm from where it crosses
the diagonal (the junction above the bowl's bottom right) all the way up
to near the x-height. It is cut so it ends only a little past the
diagonal: its outer edge now ends TAIL (0.3) of the way from the junction
height to where it used to end.

Operation, per master, in place (no unslanting: the cut is perpendicular
to the stroke as drawn):
  Arm outer edge: the curve from the line node Q (arm start) to Po (the
    arm's highest outer point, the rightmost on-curve node above the
    junction) is split at y = J.y + TAIL x (Po.y - J.y), J the on-curve
    node where the arm's inner edge meets the diagonal. The lower part
    is kept.
  Arm inner edge: the curve from Pi (inner end of the old end) down to J
    is split where the line through the new outer end, perpendicular to
    the stroke there, crosses it; the lower part is kept.
  End: Nunuiko's rounded end is rebuilt as a half-circle across the
    stroke (two quarter arcs, apex along the stroke's direction); Display
    keeps a flat cut (a straight line from the outer to the inner end).
Node count and types are unchanged, so masters stay compatible.

Run once per source from sources/:
  python3 edits/22_ampersand_short_arm.py [file.glyphs]
"""
import glob
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("*.glyphs"))[0]
TAIL = 0.3
KAPPA = 0.5522847498


def bez(p, t):
    s = 1 - t
    return tuple(s**3 * a + 3 * s * s * t * b + 3 * s * t * t * c + t**3 * d
                 for a, b, c, d in zip(*p))


def split(p, t):
    """(first, second) halves of a cubic at t."""
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    p01, p12, p23 = lerp(p[0], p[1]), lerp(p[1], p[2]), lerp(p[2], p[3])
    a, b = lerp(p01, p12), lerp(p12, p23)
    c = lerp(a, b)
    return (p[0], p01, a, c), (c, b, p23, p[3])


def solve(f, lo=0.0, hi=1.0):
    """t in [lo, hi] where f changes sign (bisection)."""
    flo = f(lo)
    assert flo * f(hi) <= 0, "no crossing"
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) * flo > 0:
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return (lo + hi) / 2


def plan(nodes, rounded):
    m = len(nodes)
    P = [(n.position.x, n.position.y) for n in nodes]
    T = [n.type for n in nodes]
    nx = lambda i: (i + 1) % m
    pv = lambda i: (i - 1) % m
    on = [i for i in range(m) if T[i] != "offcurve"]
    po = max((i for i in on if P[i][1] > 250), key=lambda i: P[i][0])
    q = pv(pv(pv(po)))
    assert T[pv(po)] == T[pv(pv(po))] == "offcurve" and T[q] == "line", "arm outer"
    # the old end: Nunuiko's round cap is 2 handles, apex, 2 handles; Display's
    # flat cut is a single line node. Then Pi, 2 handles, J.
    pi = (po + (6 if rounded else 1)) % m
    j = (pi + 3) % m
    assert T[pi] != "offcurve" and T[nx(pi)] == T[nx(nx(pi))] == "offcurve" \
        and T[j] == "curve" and P[j][1] < P[pi][1] - 50, "arm inner"
    cap = list(range(nx(po), pi))  # Nunuiko: 2 handles, apex, 2 handles; Display: none
    assert len(cap) == (5 if rounded else 0), len(cap)

    outer = (P[q], P[pv(pv(po))], P[pv(po)], P[po])
    inner = (P[pi], P[nx(pi)], P[nx(nx(pi))], P[j])
    yo = P[j][1] + TAIL * (P[po][1] - P[j][1])
    to = solve(lambda t: bez(outer, t)[1] - yo)
    o1, _ = split(outer, to)
    a = o1[3]
    d = (o1[3][0] - o1[2][0], o1[3][1] - o1[2][1])
    dl = math.hypot(*d)
    d = (d[0] / dl, d[1] / dl)
    # inner point on the line through a, perpendicular to d
    side = lambda t: ((bez(inner, t)[0] - a[0]) * d[0] + (bez(inner, t)[1] - a[1]) * d[1])
    ti = solve(side)
    _, i2 = split(inner, ti)
    b = i2[0]

    new = {pv(pv(po)): o1[1], pv(po): o1[2], po: a,
           nx(pi): i2[1], nx(nx(pi)): i2[2], pi: b}
    if rounded:
        c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        r = math.hypot(a[0] - b[0], a[1] - b[1]) / 2
        k = r * KAPPA
        apex = (c[0] + r * d[0], c[1] + r * d[1])
        ua = ((a[0] - c[0]) / r, (a[1] - c[1]) / r)
        ub = ((b[0] - c[0]) / r, (b[1] - c[1]) / r)
        h = [(a[0] + k * d[0], a[1] + k * d[1]), (apex[0] + k * ua[0], apex[1] + k * ua[1]),
             apex,
             (apex[0] + k * ub[0], apex[1] + k * ub[1]), (b[0] + k * d[0], b[1] + k * d[1])]
        new.update(dict(zip(cap, h)))
    info = f"arm end {P[po][1]:.0f} -> {a[1]:.0f} (junction {P[j][1]:.0f}), stroke {2 * math.hypot(a[0] - b[0], a[1] - b[1]) / 2:.0f}"
    return new, info


def main():
    font = GSFont(GLYPHS_FILE)
    rounded = ".formatVersion = 3;" not in open(GLYPHS_FILE).read()

    def edit(mname, layer, nodes):
        n0 = len(layer.paths[0].nodes)
        new, info = plan(nodes[:n0], rounded)
        print(f"  {mname:32s} {info}")
        return {"nodes": new}

    changed = apply_edit(GLYPHS_FILE, "ampersand", edit)
    print("written" if changed else "unchanged", GLYPHS_FILE)


if __name__ == "__main__":
    main()
