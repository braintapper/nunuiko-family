"""Code edit 3: footed 1 and i, so the narrow figures and letters fill
their cell (and 1 / i / l / I / | read apart).

1: Nunuiko's default 1 is footless (its edit 12) with the stock footed 1
   in ss01. Here the two swap contents: one / one.tosf get the footed
   outlines (and widths), one.ss01 / one.tosf.ss01 the footless ones, so
   ss01 still means "the other 1". tnum is dropped in build.py: every
   figure is 600 already, and its one.tf targets would now be footless.
   Super/subscript and fraction 1s stay footless.

i: the stem (of i and idotless; accented i's are composites of idotless
   and follow) is rebuilt as one contour standing on a foot copied from
   the footed 1 of the same master (worked unslanted):
     thickness  = height of the 1's foot
     half-length = half the 1's foot length, at most CELL/2 - SB_MIN so
                   the i is never condensed
   centred on the stem, ends rounded (radius = half the thickness). The
   stem's top cap is kept as drawn; its rounded bottom is replaced by the
   foot. Same point structure in every master. į (iogonek, drawn with
   the ogonek merged into the stem) keeps its plain stem.
"""
KAPPA = 0.5522847498
CELL = 600
SB_MIN = 30
SWAP = (("one", "one.ss01"), ("one.tosf", "one.tosf.ss01"))
FOOTED = ("i", "idotless")


def swap(ufo, a, b):
    ga, gb = ufo[a], ufo[b]
    assert not ga.components and not gb.components, (a, b)
    ca, cb = [list(c) for c in ga], [list(c) for c in gb]
    wa, wb = ga.width, gb.width
    for g, contours, w in ((ga, cb, wb), (gb, ca, wa)):
        g.clearContours()
        pen = g.getPointPen()
        for pts in contours:
            pen.beginPath()
            for p in pts:
                pen.addPoint((p.x, p.y), p.segmentType, p.smooth)
            pen.endPath()
        g.width = w


def foot_of_one(ufo, tan):
    """(thickness, length) of the footed 1's foot, unslanted."""
    pts = [p for c in ufo["one.ss01"] for p in c if p.y < 200]
    t = max(p.y for p in pts)
    xs = [p.x - p.y * tan for p in pts]
    return t, max(xs) - min(xs)


def add_foot(g, t, half, tan):
    stem = min(g, key=lambda c: min(p.y for p in c))
    pts = list(stem)
    n = len(pts)
    ux = lambda p: p.x - p.y * tan
    mid = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    # top cap: from the right stem's top on-curve, 6 points round to the left
    tops = [k for k in range(n) if pts[k].segmentType and pts[k].y > mid]
    start = max(tops, key=lambda k: (round(ux(pts[k])), -pts[k].y))
    cap = [pts[(start + j) % n] for j in range(7)]
    types = "".join("o" if p.segmentType is None else "c" for p in cap[1:])
    assert types == "oocooc", (g.name, types)
    xr, xl = ux(cap[0]), ux(cap[6])
    assert xr > xl, g.name
    c = (xl + xr) / 2
    r = t / 2
    k = r * KAPPA
    a, b = c - half, c + half
    sl = lambda x, y: (x + y * tan, y)
    g.contours.remove(stem)
    pen = g.getPen()
    pen.moveTo(sl(a + r, 0))
    pen.lineTo(sl(b - r, 0))
    pen.curveTo(sl(b - r + k, 0), sl(b, r - k), sl(b, r))
    pen.curveTo(sl(b, r + k), sl(b - r + k, t), sl(b - r, t))
    pen.lineTo(sl(xr, t))
    pen.lineTo((cap[0].x, cap[0].y))
    pen.curveTo(*[(p.x, p.y) for p in cap[1:4]])
    pen.curveTo(*[(p.x, p.y) for p in cap[4:7]])
    pen.lineTo(sl(xl, t))
    pen.lineTo(sl(a + r, t))
    pen.curveTo(sl(a + r - k, t), sl(a, r + k), sl(a, r))
    pen.curveTo(sl(a, r - k), sl(a + r - k, 0), sl(a + r, 0))
    pen.closePath()
    return xr - xl


def apply(ufo, stem, tan):
    t, length = foot_of_one(ufo, tan)
    half = min(length / 2, CELL / 2 - SB_MIN)
    for a, b in SWAP:
        swap(ufo, a, b)
    for name in FOOTED:
        w = add_foot(ufo[name], t, half, tan)
    print(f"  foot: thickness {t:g}, length {2 * half:.0f} (1's foot {length:.0f}), stem {w:.0f}")
