"""Code edit 7: wider crossbars on t and f; the f's top arches down.

Bars: each end of the crossbar reaches BAR x as far from the stem (left
   end from the stem's left edge, right end from its right edge), the
   points stretched away from the edge so the round ends keep their
   shape. If that would make the letter wider than the cell allows, both
   ends are cut back in proportion. Accented and other composites of t
   and f follow.

f top: the hook is redrawn as the n's arch (from the n of the same
   master), like the r: the stem's right edge rises into the n's inner
   curve, the arch is cut ARCH of the way down its descent and ended with
   a round terminal, and the outer edge comes back over the top on the
   n's outer curve, then down to the stem's left edge on a quarter ellipse.
   The top of the arch stays at the old f's height. So the f's top curves
   down like the r's arm instead of ending flat.

All worked unslanted.
"""
import math

from fontTools.misc.bezierTools import splitCubicAtT

KAPPA = 0.5522847498
CELL = 600
SB_MIN = 30
BAR = 1.3     # crossbar reach from the stem edges x this
ARCH = 0.55   # f: share of the n's arch descent kept, as on the r


def stem_edges(pts, tan, y):
    """Unslanted x of the stem's two edges at height y (polygon of on-curves)."""
    ux = [(p.x - p.y * tan, p.y) for p in pts if p.segmentType is not None]
    xs = []
    for (ax, ay), (bx, by) in zip(ux, ux[1:] + ux[:1]):
        if (ay <= y < by) or (by <= y < ay):
            xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
    xs.sort()
    return xs[0], xs[1]


def widen_bar(g, tan):
    pts = [p for c in g for p in c]
    ux = lambda p: p.x - p.y * tan
    xs = [ux(p) for p in pts]
    left_pts = [p for p in pts if ux(p) < min(xs) + 1]  # the bar's left end
    # the bar: from the stem's left edge, scan the leftmost points' heights
    ylo = min(p.y for p in pts if ux(p) < min(xs) + 40)
    yhi = max(p.y for p in pts if ux(p) < min(xs) + 40)
    assert left_pts and yhi - ylo < 200, g.name
    xl, xr = stem_edges(g[0], tan, ylo - 30)
    band = [p for p in pts if ylo - 1 <= p.y <= yhi + 1]
    lreach = xl - min(ux(p) for p in band)
    rreach = max(ux(p) for p in band) - xr
    k = BAR
    others = [ux(p) for p in pts if not (ylo - 1 <= p.y <= yhi + 1)]
    room = CELL - 2 * SB_MIN
    # cut back if the widened bar would overflow the cell
    for _ in range(30):
        lo = min([xl - lreach * k] + others)
        hi = max([xr + rreach * k] + others)
        if hi - lo <= room or k <= 1:
            break
        k -= 0.01
    for p in band:
        u = ux(p)
        if u < xl - 0.5:
            p.x = xl - (xl - u) * k + p.y * tan
        elif u > xr + 0.5:
            p.x = xr + (u - xr) * k + p.y * tan
    return k


def f_arch(ufo, tan):
    n_ = ufo["n"]
    npts = list(n_[0])
    assert len(n_) == 1 and len(npts) == 36
    u = lambda p: (p.x - p.y * tan, p.y)
    sl = lambda x, y: (x + y * tan, y)
    g = ufo["f"]
    assert len(g) == 1, g.name
    pts = list(g[0])
    types = "".join("o" if p.segmentType is None else "c" for p in pts)
    # 14: stem's right edge where the arch begins; 25: stem's left edge
    # where the arch comes back down
    assert pts[14].segmentType == "line" and pts[25].segmentType == "curve", types
    xr, xl = u(pts[14])[0], u(pts[25])[0]
    top = max(p.y for p in pts)
    # n: 4 inner stem top, 7 inner apex, 10 inner right stem top,
    # 18 outer right stem top, 21 outer apex
    n4, n7, n21 = u(npts[4]), u(npts[7]), u(npts[21])
    h = n21[1] - n7[1]  # arch thickness at the apex
    dx, dy = xr - n4[0], (top - h) - n7[1]
    mv = lambda q: (q[0] + dx, q[1] + dy)
    rise = [mv(u(p)) for p in npts[4:8]]  # inner: stem up to the apex
    inner = splitCubicAtT(*[mv(u(p)) for p in npts[7:11]], ARCH)[0]
    outer = splitCubicAtT(*[mv(u(p)) for p in npts[18:22]], 1 - ARCH)[1]
    pin, pout = inner[3], outer[0]
    mx, my = (pin[0] + pout[0]) / 2, (pin[1] + pout[1]) / 2
    rho = math.hypot(pout[0] - pin[0], pout[1] - pin[1]) / 2
    ex, ey = (pout[0] - pin[0]) / (2 * rho), (pout[1] - pin[1]) / (2 * rho)
    cx, cy = ey, -ex  # down the arch
    k = rho * KAPPA
    apex = (mx + cx * rho, my + cy * rho)
    # outer apex back down to the stem's left edge: quarter ellipse
    ax, ay = outer[3]
    rx = ax - xl
    ry = rx * (n7[1] - n4[1]) / (n7[0] - n4[0])
    new = [((p.x, p.y), p.segmentType, p.smooth) for p in pts[:14]]
    new += [(sl(*rise[0]), "line", False),
            (sl(*rise[1]), None, False), (sl(*rise[2]), None, False), (sl(*rise[3]), "curve", True),
            (sl(*inner[1]), None, False), (sl(*inner[2]), None, False), (sl(*pin), "curve", False),
            (sl(pin[0] + cx * k, pin[1] + cy * k), None, False),
            (sl(apex[0] - ex * k, apex[1] - ey * k), None, False), (sl(*apex), "curve", True),
            (sl(apex[0] + ex * k, apex[1] + ey * k), None, False),
            (sl(pout[0] + cx * k, pout[1] + cy * k), None, False), (sl(*pout), "curve", False),
            (sl(*outer[1]), None, False), (sl(*outer[2]), None, False), (sl(ax, ay), "curve", True),
            (sl(ax - rx * KAPPA, ay), None, False), (sl(xl, ay - ry + ry * KAPPA), None, False),
            (sl(xl, ay - ry), "curve", False)]
    new += [((p.x, p.y), p.segmentType, p.smooth) for p in pts[26:]]
    g.clearContours()
    pen = g.getPointPen()
    pen.beginPath()
    for xy, seg, sm in new:
        pen.addPoint(xy, seg, sm)
    pen.endPath()
    return pin[1], pout[1]


def apply(ufo, stem, tan):
    cut = f_arch(ufo, tan)
    kt = widen_bar(ufo["t"], tan)
    kf = widen_bar(ufo["f"], tan)
    print(f"  f arch cut at {cut[0]:.0f}/{cut[1]:.0f}; bars t {kt:.2f} f {kf:.2f}")
