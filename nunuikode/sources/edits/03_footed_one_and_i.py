"""Code edit 3: footed 1, footed and flagged i, flagged l, n-arched r, barred I, so the
narrow figures and letters fill their cell and 1 / i / l / I / | read apart.

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
   stem's rounded bottom is replaced by the foot.
   Flag: an arm runs left from the stem top, same thickness and round end
   as the foot, its top flush with the old cap's top. It reaches FLAG x
   the foot's reach from the stem centre, so it stops short of the foot's
   left end (Heavy: at least the round end sticks out, its thickness
   leaves no room for more). The right half of the old top cap is kept,
   so the top right corner stays round. Same point structure in every
   master. į (iogonek, drawn with the ogonek merged into the stem) keeps
   its plain stem.

l: Nunuiko's tailed l keeps its curved bottom and gets the i's flag (same
   thickness, round end) in place of the left half of its top cap. Like
   the i's foot, the l spans the foot's length centred on its stem: the
   flag reaches FLAG_L x the foot's reach left of the stem centre, and the
   tail is stretched out to the foot's reach on the right (every point
   right of the stem's right edge, below TAIL_Y, moves away from that edge
   in proportion, so the curve keeps its shape). Nunuiko's short tail left
   the l a bare stem in its cell, so "ll", "cl", "el" read far looser
   than "il". Its
   accented forms and lj follow; the fl / f_f_l ligature characters are
   decomposed first and keep the unflagged l (the flag would hit the f's
   hook). ss02 still gives Nunuiko's plain l.

r: rebuilt from the n of the same master: its stem and arch, the arch
   cut ARCH of the way down its descent (both edges split at the same
   curve parameter) and ended with a round terminal, a half circle on the
   cut. So the arm arches down like the n's shoulder. Anchors: bottom keeps
   its place under the stem, top goes over the arch (the n's). Nunuiko's
   r is the narrowest lowercase letter and set loose alone in its cell
   ("mirror", "array"). ŕ ř ŗ follow. (Tried first: the i's foot, too
   heavy; then the old arm stretched 1.4x.)

I: rebuilt as one contour: the stem with a bar at the bottom (on the
   baseline) and one at the top (flush with the cap height), both exactly
   the i's foot (thickness, length, round ends), centred on the stem.
   Accented I's, I-cy, Yi-cy and Palochka-cy are composites and follow.
   IJ and its Dutch forms are decomposed first and keep the plain stem
   (two letters already share one cell); Iogonek is drawn with the
   ogonek merged and keeps its plain stem.
"""
import math

from fontTools.misc.bezierTools import splitCubicAtT
from fontTools.pens.recordingPen import DecomposingRecordingPen

KAPPA = 0.5522847498
CELL = 600
SB_MIN = 30
FLAG = 0.7  # flag reach / foot reach, both from the stem centre
FLAG_L = 1.0  # the l's flag reach / foot reach
TAIL_Y = 300  # l: tail points lie below this height
ARCH = 0.55  # r: share of n's arch descent kept (0 top .. 1 stem)
SWAP = (("one", "one.ss01"), ("one.tosf", "one.tosf.ss01"))
FOOTED = ("i", "idotless")
FLAGGED = ("l",)
KEEP_PLAIN = ("fl", "f_f_l",  # keep the unflagged l
              "IJ", "I_J.loclNLD", "Iacute_J.loclNLD")  # keep plain I


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


def freeze(ufo, names):
    """Decompose these glyphs, so later edits to their bases skip them."""
    for name in names:
        g = ufo[name]
        rec = DecomposingRecordingPen(ufo)
        g.draw(rec)
        g.clearComponents()
        rec.replay(g.getPen())


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
    top = cap[3].y
    assert abs(ux(cap[3]) - c) < 1, g.name  # cap[3]: the cap's top centre
    r = t / 2
    k = r * KAPPA
    a, b = c - half, c + half
    # flag's left end; at least its round end clears the stem (Heavy's
    # thick foot would otherwise end the flag inside the stem)
    f = min(c - FLAG * half, xl - r - 1)
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
    pen.lineTo(sl(f + r, top))
    pen.curveTo(sl(f + r - k, top), sl(f, top - r + k), sl(f, top - r))
    pen.curveTo(sl(f, top - r - k), sl(f + r - k, top - t), sl(f + r, top - t))
    pen.lineTo(sl(xl, top - t))
    pen.lineTo(sl(xl, t))
    pen.lineTo(sl(a + r, t))
    pen.curveTo(sl(a + r - k, t), sl(a, r + k), sl(a, r))
    pen.curveTo(sl(a, r - k), sl(a + r - k, 0), sl(a + r, 0))
    pen.closePath()
    return xr - xl


def add_flag(g, t, half, tan):
    """Tailed l: replace the left half of the top cap with the i's flag.
    Points are rebuilt from the cap's right stem top round the contour, so
    the start point moves the same way in every master."""
    stem = max(g, key=lambda c: max(p.y for p in c))
    pts = list(stem)
    n = len(pts)
    ux = lambda p: p.x - p.y * tan
    mid = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    tops = [k for k in range(n) if pts[k].segmentType and pts[k].y > mid]
    start = max(tops, key=lambda k: (round(ux(pts[k])), -pts[k].y))
    ring = [pts[(start + j) % n] for j in range(n)]
    types = "".join("o" if p.segmentType is None else "c" for p in ring[1:7])
    assert types == "oocooc", (g.name, types)
    xl, xr = ux(ring[6]), ux(ring[0])
    c = (xl + xr) / 2
    tail = [p for p in ring[7:] if p.y < TAIL_Y and ux(p) > xr + 0.5]
    s = (c + half - xr) / (max(ux(p) for p in tail) - xr)
    for p in tail:  # stretch right of the stem edge out to c + half
        p.x = xr + (ux(p) - xr) * s + p.y * tan
    top = ring[3].y
    r = t / 2
    k = r * KAPPA
    f = min(c - FLAG_L * half, xl - r - 1)
    sl = lambda x, y: (x + y * tan, y)
    flag = [(sl(f + r, top), "line", False), (sl(f + r - k, top), None, False),
            (sl(f, top - r + k), None, False), (sl(f, top - r), "curve", True),
            (sl(f, top - r - k), None, False), (sl(f + r - k, top - t), None, False),
            (sl(f + r, top - t), "curve", False), (sl(xl, top - t), "line", False)]
    keep = lambda ps: [((p.x, p.y), p.segmentType, p.smooth) for p in ps]
    new = keep(ring[:4]) + flag + keep(ring[7:])
    contours = [keep(c) for c in g if c is not stem]
    g.clearContours()
    pen = g.getPointPen()
    for pts_ in [new] + contours:
        pen.beginPath()
        for xy, seg, smooth in pts_:
            pen.addPoint(xy, seg, smooth)
        pen.endPath()


def r_from_n(ufo, tan):
    """r: n's stem and arch, the arch cut at ARCH along its descent and
    ended with a round terminal (unslanted)."""
    n_ = ufo["n"]
    assert len(n_) == 1 and len(n_[0]) == 36, len(n_[0])
    pts = list(n_[0])
    types = "".join("o" if p.segmentType is None else "c" for p in pts)
    # 0 bottom of the left stem .. 7 inner top of the arch .. 10 top of the
    # inner right stem; 18 top of the outer right stem .. 21 outer top
    assert types[7] == types[10] == types[18] == types[21] == "c", types
    u = lambda p: (p.x - p.y * tan, p.y)
    sl = lambda x, y: (x + y * tan, y)
    inner = splitCubicAtT(*[u(p) for p in pts[7:11]], ARCH)[0]
    outer = splitCubicAtT(*[u(p) for p in pts[18:22]], 1 - ARCH)[1]
    pin, pout = inner[3], outer[0]
    # terminal: half circle on the cut, bulging along the arch's descent
    mx, my = (pin[0] + pout[0]) / 2, (pin[1] + pout[1]) / 2
    rho = math.hypot(pout[0] - pin[0], pout[1] - pin[1]) / 2
    ex, ey = (pout[0] - pin[0]) / (2 * rho), (pout[1] - pin[1]) / (2 * rho)
    dx, dy = ey, -ex  # perpendicular to the cut, pointing down the arch
    k = rho * KAPPA
    apex = (mx + dx * rho, my + dy * rho)
    cap = [((pin[0] + dx * k, pin[1] + dy * k), None),
           ((apex[0] - ex * k, apex[1] - ey * k), None), (apex, "curve"),
           ((apex[0] + ex * k, apex[1] + ey * k), None),
           ((pout[0] + dx * k, pout[1] + dy * k), None), (pout, "curve")]
    new = [((p.x, p.y), p.segmentType) for p in pts[:8]]
    new += [(sl(*inner[1]), None), (sl(*inner[2]), None), (sl(*pin), "curve")]
    new += [(sl(*xy), seg) for xy, seg in cap]
    new += [(sl(*outer[1]), None), (sl(*outer[2]), None)]
    new += [((p.x, p.y), p.segmentType) for p in pts[21:]]
    g = ufo["r"]
    assert len(g) == 1, g.name
    # anchors: bottom keeps its place under the stem, top goes over the arch
    shift = min(p.x - p.y * tan for p in g[0] if p.y < 100) - \
        min(p.x - p.y * tan for p in pts if p.y < 100)
    top = {a.name: a for a in n_.anchors}.get("top")
    for a in g.anchors:
        if a.name == "top" and top is not None:
            a.x, a.y = top.x, top.y
        else:
            a.x -= shift
    g.clearContours()
    pen = g.getPointPen()
    pen.beginPath()
    for xy, seg in new:
        pen.addPoint(xy, seg)
    pen.endPath()
    g.width = n_.width
    return pin[1], pout[1]


def add_bars(g, t, half, top, tan):
    """I: stem plus equal bars at the baseline and at `top`."""
    assert len(g) == 1, g.name
    xs = [p.x - p.y * tan for p in g[0]]
    xl, xr = min(xs), max(xs)
    c = (xl + xr) / 2
    r = t / 2
    k = r * KAPPA
    a, b = c - half, c + half
    sl = lambda x, y: (x + y * tan, y)
    g.clearContours()
    pen = g.getPen()
    pen.moveTo(sl(a + r, 0))
    pen.lineTo(sl(b - r, 0))
    pen.curveTo(sl(b - r + k, 0), sl(b, r - k), sl(b, r))
    pen.curveTo(sl(b, r + k), sl(b - r + k, t), sl(b - r, t))
    pen.lineTo(sl(xr, t))
    pen.lineTo(sl(xr, top - t))
    pen.lineTo(sl(b - r, top - t))
    pen.curveTo(sl(b - r + k, top - t), sl(b, top - r - k), sl(b, top - r))
    pen.curveTo(sl(b, top - r + k), sl(b - r + k, top), sl(b - r, top))
    pen.lineTo(sl(a + r, top))
    pen.curveTo(sl(a + r - k, top), sl(a, top - r + k), sl(a, top - r))
    pen.curveTo(sl(a, top - r - k), sl(a + r - k, top - t), sl(a + r, top - t))
    pen.lineTo(sl(xl, top - t))
    pen.lineTo(sl(xl, t))
    pen.lineTo(sl(a + r, t))
    pen.curveTo(sl(a + r - k, t), sl(a, r + k), sl(a, r))
    pen.curveTo(sl(a, r - k), sl(a + r - k, 0), sl(a + r, 0))
    pen.closePath()


def apply(ufo, stem, tan):
    t, length = foot_of_one(ufo, tan)
    half = min(length / 2, CELL / 2 - SB_MIN)
    for a, b in SWAP:
        swap(ufo, a, b)
    freeze(ufo, KEEP_PLAIN)
    add_bars(ufo["I"], t, half, ufo.info.capHeight, tan)
    for name in FOOTED:
        w = add_foot(ufo[name], t, half, tan)
    for name in FLAGGED:
        add_flag(ufo[name], t, half, tan)
    cut = r_from_n(ufo, tan)
    print(f"  r arch cut at {cut[0]:.0f}/{cut[1]:.0f}")
    print(f"  foot: thickness {t:g}, length {2 * half:.0f} (1's foot {length:.0f}), stem {w:.0f}")
