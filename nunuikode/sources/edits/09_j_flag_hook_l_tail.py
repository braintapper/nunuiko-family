"""Code edit 9: j with the i's flag and a longer hook; the l's tail turns up.

j: j and jdotless (so ĵ and ј follow) get the i's flag (edit 3) in place
   of the left half of the stem's top cap: same thickness and round end,
   top flush with the old cap's top, reaching FLAG x the foot's reach left
   of the stem centre. The hook is redrawn as half a u's bowl: from the
   stem down round the descender and up a left arm a stem's width wide,
   whose round end tops out CURL of the way up to the baseline. The bowl's
   bottom has the foot's thickness, and the j's ink spans HOOK x the i's
   foot length from the stem's right edge (the i and l span the foot's
   length): Nunuiko's j was a stem with a short hook, set loose in its
   cell like the old l. Worked unslanted.
   lj, nj, Lj, Nj and the Dutch ij forms are frozen first and keep the
   plain j (two letters already share the cell).

l: the end of the tail (every point right of the stem's right edge,
   below TAIL_Y) bends up past BEND_FROM of its reach: each point there
   turns about the tail's bottom at that x by TAIL_UP x a smoothstep of how far out
   it lies, so the round end turns by the full angle and stays round, the
   curve eases into the bend, and the l still stands on the baseline.
   Before bending, that part is stretched by 1 / cos(TAIL_UP) so its end
   still reaches about the foot's reach (edit 3). Accented l's follow;
   the fl ligatures keep their frozen unflagged l, and l.ss02 is unchanged.

Same point structure in every master.
"""
import math

from fontTools.pens.recordingPen import DecomposingRecordingPen

KAPPA = 0.5522847498
CELL = 600
SB_MIN = 30
FLAG = 0.7       # the j's flag reach / foot reach, as the i's
HOOK = 1.0       # the j's ink width / the i's foot length
CURL = 0.85      # the j's curl tops out this share of the way from the descender to the baseline
DEPTH = 0.8      # the bowl's height / half its width, at most
BOWL = 0.6       # the bowl's curve tension (handle share of the way to its box corner)
MIN_IN = 30      # the bowl's counter is at least this tall
TAIL_UP = 20     # degrees the l's tail end turns up
TAIL_Y = 300     # l: tail points lie below this height
BEND_FROM = 0.4  # l: share of the tail's reach (from the stem) before it bends
J = ("j", "jdotless")
KEEP_PLAIN = ("lj", "nj", "Lj", "Nj", "lj.ss02", "i_j.loclNLD", "iacute_j.loclNLD")


def freeze(ufo, names):
    for name in names:
        if name not in ufo:
            continue
        g = ufo[name]
        rec = DecomposingRecordingPen(ufo)
        g.draw(rec)
        g.clearComponents()
        rec.replay(g.getPen())


def foot(ufo, tan):
    """(thickness, half length) of the footed 1's foot (edit 3 made it the
    default one), as edit 3 uses it."""
    pts = [p for c in ufo["one"] for p in c if p.y < 200]
    t = max(p.y for p in pts)
    xs = [p.x - p.y * tan for p in pts]
    return t, min((max(xs) - min(xs)) / 2, CELL / 2 - SB_MIN)


def write(g, rings):
    g.clearContours()
    pen = g.getPointPen()
    for pts in rings:
        pen.beginPath()
        for xy, seg, smooth in pts:
            pen.addPoint(xy, seg, smooth)
        pen.endPath()


def j_flag_hook(g, t, half, tan):
    stem = min(g, key=lambda c: min(p.y for p in c))
    pts = list(stem)
    n = len(pts)
    assert n == 17, (g.name, n)
    ux = lambda p: p.x - p.y * tan
    mid = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    tops = [k for k in range(n) if pts[k].segmentType and pts[k].y > mid]
    start = max(tops, key=lambda k: (round(ux(pts[k])), -pts[k].y))
    ring = [pts[(start + j) % n] for j in range(n)]
    # 0 right stem top, 1-6 top cap to the left stem top, 7 left stem bottom,
    # 10 hook's inner end, 13 its outer end, 16 right stem bottom
    types = "".join("o" if p.segmentType is None else "c" for p in ring)
    assert types == "coocooccoocoocooc", (g.name, types)
    xl, xr = ux(ring[6]), ux(ring[0])
    c = (xl + xr) / 2
    sl = lambda x, y: (x + y * tan, y)
    # hook: half a u's bowl. The outer bowl runs from the stem's right edge
    # down to the descender and up the left arm, HOOK x the foot length
    # out from the stem's right edge; the arm is a stem's width, the bowl's
    # bottom the foot's thickness, and the arm's round end tops out CURL of
    # the way up from the descender to the baseline (higher only where the
    # counter would otherwise close, at the heaviest weights).
    w = xr - xl
    yb = min(p.y for p in ring)
    xL = xr - HOOK * 2 * half
    xa = xL + w  # the arm's right (inner) edge
    rxo, rxi = (xr - xL) / 2, (xl - xa) / 2
    assert rxi > 0, (g.name, rxi)
    y_end = max(yb + CURL * -yb - w / 2, yb + t + MIN_IN)  # where the arm's round end starts
    ryo = min(DEPTH * rxo, y_end - yb)
    ryi = ryo - t
    cxo, cxi = (xr + xL) / 2, (xl + xa) / 2
    ys = yb + ryo  # the straight edges start here, inside and out
    T = BOWL
    hk = (w / 2) * KAPPA
    ca = (xL + xa) / 2
    hook = [(sl(xl, ys), "line", False),
            (sl(xl, ys - T * ryi), None, False), (sl(cxi + T * rxi, yb + t), None, False),
            (sl(cxi, yb + t), "curve", True),
            (sl(cxi - T * rxi, yb + t), None, False), (sl(xa, ys - T * ryi), None, False),
            (sl(xa, ys), "curve", True),
            (sl(xa, y_end), "line", False),
            (sl(xa, y_end + hk), None, False), (sl(ca + hk, y_end + w / 2), None, False),
            (sl(ca, y_end + w / 2), "curve", True),
            (sl(ca - hk, y_end + w / 2), None, False), (sl(xL, y_end + hk), None, False),
            (sl(xL, y_end), "curve", True),
            (sl(xL, ys), "line", False),
            (sl(xL, ys - T * ryo), None, False), (sl(cxo - T * rxo, yb), None, False),
            (sl(cxo, yb), "curve", True),
            (sl(cxo + T * rxo, yb), None, False), (sl(xr, ys - T * ryo), None, False),
            (sl(xr, ys), "curve", True)]
    sl = lambda x, y: (x + y * tan, y)
    # flag, as the i's
    top = ring[3].y
    r = t / 2
    k = r * KAPPA
    f = min(c - FLAG * half, xl - r - 1)
    flag = [(sl(f + r, top), "line", False), (sl(f + r - k, top), None, False),
            (sl(f, top - r + k), None, False), (sl(f, top - r), "curve", True),
            (sl(f, top - r - k), None, False), (sl(f + r - k, top - t), None, False),
            (sl(f + r, top - t), "curve", False), (sl(xl, top - t), "line", False)]
    keep = lambda ks: [((ring[i].x, ring[i].y), ring[i].segmentType, ring[i].smooth) for i in ks]
    new = keep(range(4)) + flag + hook
    others = [[((p.x, p.y), p.segmentType, p.smooth) for p in c_] for c_ in g if c_ is not stem]
    write(g, [new] + others)
    return xL, f, y_end + w / 2


def l_tail_up(g, tan):
    stem = max(g, key=lambda c: max(p.y for p in c))
    ux = lambda p: p.x - p.y * tan
    # the stem's right edge: the rightmost on-curve point above the tail
    xr = max(ux(p) for p in stem if p.segmentType and p.y > TAIL_Y)
    tail = [p for p in stem if p.y < TAIL_Y and ux(p) > xr + 0.5]
    # the bend starts BEND_FROM of the way out along the tail, about where
    # it bottoms out, and turns about that point on the tail's bottom, so
    # the l keeps standing on the baseline
    reach = max(ux(p) for p in tail) - xr
    bx, by = xr + BEND_FROM * reach, min(p.y for p in tail)
    far = reach * (1 - BEND_FROM)
    a = math.radians(TAIL_UP)
    s = 1 / math.cos(a)
    moved = [p for p in tail if ux(p) > bx + 0.5]
    for p in moved:
        d = ux(p) - bx
        w = d / far
        w = w * w * (3 - 2 * w)
        x, y = d * s, p.y - by
        phi = a * w
        x, y = x * math.cos(phi) - y * math.sin(phi), x * math.sin(phi) + y * math.cos(phi)
        y += by
        p.x, p.y = bx + x + y * tan, y
    return far, max(p.y for p in tail)


def apply(ufo, stem, tan):
    t, half = foot(ufo, tan)
    far, end = l_tail_up(ufo["l"], tan)
    freeze(ufo, KEEP_PLAIN)
    for name in J:
        reach, f, top = j_flag_hook(ufo[name], t, half, tan)
    print(f"  l tail: reach {far:.0f}, top now {end:.0f}; j: hook to {reach:.0f}, curl up to {top:.0f}, flag to {f:.0f}")
