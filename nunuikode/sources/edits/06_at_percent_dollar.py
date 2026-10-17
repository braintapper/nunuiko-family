"""Code edit 6: % gets smaller round rings; $ is no taller than the S.
(The @ is done by edit 8, with the © and ®.)

scale_kept, used here and by edit 8, scales an outline while keeping its
stroke weight: scaling down would thin every stroke, so each on-curve
point moves out along its normal by half the lost thickness, handles
following their on-curve point (as build.py does across x when
condensing).

%: the two rings were tall ovals (231 x 431 at ExtraLight once
   condensed). Each is redrawn as a circle of diameter RING x the cap
   height, keeping the original ring's side and top/bottom thickness: the
   upper one sits in the top-left corner, top on the O's top; the lower
   one in the bottom-right corner, bottom on the O's bottom. The glyph is
   made WIDTH wide around the slash's centre, which is left as it was, so
   it fits the cell without condensing. Heavy's thick strokes are capped
   at MAXT x the radius so a counter stays. ‰ keeps its rings.

$: Nunuiko's $ is an S with the bar sticking out above and below it
   (-121..826 at ExtraLight). It is scaled down uniformly until its full
   height, bar ends included, is the S's own, so the S in it is smaller
   than a regular S. Stroke weight is kept (scale_kept). Since Nunuiko's
   edit 16 its $ already has the S's height, so this is a no-op on a
   snapshot taken after that.
"""
import math

KAPPA = 0.5522847498
RING = 0.4    # % ring diameter, x cap height
WIDTH = 540   # % overall width: the cell less 30 each side
MAXT = 0.76   # ring thickness at most this x its radius (Heavy only)


def o_bounds(ufo):
    ys = [p.y for c in ufo["O"] for p in c]
    return min(ys), max(ys)


def bounds(g, tan):
    us = [p.x - p.y * tan for c in g for p in c]
    ys = [p.y for c in g for p in c]
    return min(us), min(ys), max(us), max(ys)


def scale_kept(g, s, sy, ox, oy, nx, ny, stem, tan):
    """Scale g by (s, sy) from (ox, oy) to (nx, ny), unslanted, keeping
    stroke weight: on-curve points move out along their normal by half the
    thickness lost on each axis, handles follow their on-curve point."""
    clamp = lambda v: max(-1.0, min(1.0, v / 0.3))
    for c in g:
        pts = list(c)
        n = len(pts)
        un = [(p.x - p.y * tan, p.y) for p in pts]
        d = [(0.0, 0.0)] * n
        for k in range(n):
            if pts[k].segmentType is not None:
                (px, py), (qx, qy) = un[(k - 1) % n], un[(k + 1) % n]
                tx, ty = qx - px, qy - py
                ln = math.hypot(tx, ty) or 1.0
                # outward normal (ty, -tx), as in build.py
                d[k] = ((1 - s) * stem / 2 * clamp(ty / ln),
                        (1 - sy) * stem / 2 * clamp(-tx / ln))
        for k in range(n):
            if pts[k].segmentType is None:
                before = pts[(k - 1) % n].segmentType is not None
                d[k] = d[(k - 1) % n] if before else d[(k + 1) % n]
        for k, p in enumerate(pts):
            y = ny + (un[k][1] - oy) * sy + d[k][1]
            p.x = nx + (un[k][0] - ox) * s + d[k][0] + y * tan
            p.y = y


def shrink_dollar(g, ref, stem, tan):
    """$: uniformly, so its full height (bar ends) is the S's."""
    x0, y0, x1, y1 = bounds(g, tan)
    _, lo, _, hi = bounds(ref, tan)
    s = (hi - lo - stem) / (y1 - y0 - stem)
    cx = (x0 + x1) / 2
    scale_kept(g, s, s, cx, y0, cx, lo + (1 - s) * stem / 2, stem, tan)
    return s


def ring(pen, sl, cx, cy, rx, ry, ccw):
    kx, ky = rx * KAPPA, ry * KAPPA
    if ccw:
        pts = [(cx, cy - ry), (cx + kx, cy - ry), (cx + rx, cy - ky), (cx + rx, cy),
               (cx + rx, cy + ky), (cx + kx, cy + ry), (cx, cy + ry),
               (cx - kx, cy + ry), (cx - rx, cy + ky), (cx - rx, cy),
               (cx - rx, cy - ky), (cx - kx, cy - ry)]
    else:
        pts = [(cx, cy - ry), (cx - kx, cy - ry), (cx - rx, cy - ky), (cx - rx, cy),
               (cx - rx, cy + ky), (cx - kx, cy + ry), (cx, cy + ry),
               (cx + kx, cy + ry), (cx + rx, cy + ky), (cx + rx, cy),
               (cx + rx, cy - ky), (cx + kx, cy - ry)]
    pen.moveTo(sl(*pts[0]))
    for j in range(1, 12, 3):
        pen.curveTo(sl(*pts[j]), sl(*pts[j + 1]), sl(*pts[(j + 2) % 12]))
    pen.closePath()


def redo_percent(ufo, lo, hi, tan):
    g = ufo["percent"]
    assert not g.components and len(g) == 5, len(g)
    ux = lambda p: p.x - p.y * tan
    box = lambda c: (min(ux(p) for p in c), min(p.y for p in c),
                     max(ux(p) for p in c), max(p.y for p in c))
    slash = [c for c in g if len(c) == 8]
    assert len(slash) == 1
    rings = sorted((c for c in g if len(c) != 8), key=lambda c: -box(c)[3])
    # rings[0], rings[1]: upper outer and counter (outer is taller)
    o, i = sorted(rings[:2], key=lambda c: box(c)[1])
    bo, bi = box(o), box(i)
    tx, ty = bi[0] - bo[0], bo[3] - bi[3]
    r = RING * ufo.info.capHeight / 2
    tx, ty = min(tx, MAXT * r), min(ty, MAXT * r)  # Heavy: keep a counter
    sx0, _, sx1, _ = box(slash[0])
    xs = (sx0 + sx1) / 2
    keep = [[((p.x, p.y), p.segmentType, p.smooth) for p in slash[0]]]
    g.clearContours()
    pp = g.getPointPen()
    for pts in keep:
        pp.beginPath()
        for xy, seg, sm in pts:
            pp.addPoint(xy, seg, sm)
        pp.endPath()
    sl = lambda x, y: (x + y * tan, y)
    pen = g.getPen()
    for cx, cy in ((xs - WIDTH / 2 + r, hi - r), (xs + WIDTH / 2 - r, lo + r)):
        ring(pen, sl, cx, cy, r, r, True)
        ring(pen, sl, cx, cy, r - tx, r - ty, False)
    return tx, ty


def apply(ufo, stem, tan):
    for name in ufo.keys():
        assert not any(c.baseGlyph in ("percent", "dollar")
                       for c in ufo[name].components), name
    lo, hi = o_bounds(ufo)
    tx, ty = redo_percent(ufo, lo, hi, tan)
    sd = shrink_dollar(ufo["dollar"], ufo["S"], stem, tan)
    print(f"  % rings {RING * ufo.info.capHeight:.0f}, thickness {tx:.0f}/{ty:.0f}; $ scaled {sd:.2f}")
