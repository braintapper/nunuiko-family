"""Code edit 7: wider crossbars on t and f; the f's top arches down.

Bars: each end of the crossbar reaches BAR (f: 1.3) or BAR_T (t: 1.6) x
   as far from the stem (left end from the stem's left edge, right end
   from its right edge), the
   points stretched away from the edge so the round ends keep their
   shape. If that would make the letter wider than the cell allows, both
   ends are cut back in proportion. Accented and other composites of t
   and f follow.

f top: the hook is redrawn as the n's arch (from the n of the same
   master), like the r: the stem's right edge rises into the n's inner
   curve, the arch is cut ARCH of the way down its descent and ended with
   a round terminal, and the outer edge comes back over the top on the
   n's outer curve, then down to the stem's left edge on a quarter ellipse.
   The inner edge is that outer edge offset inward: by the stem's width
   where it leaves the stem, easing to the r's (the n's) arch weight at the
   apex and keeping it from there to the cut (tapering toward the cut only
   where the arch is too tight for it, at Heavy). The n's own inner curve
   thinned where it left the stem and swelled at the apex,
   and the terminal is cut square to the stroke. The top of the arch stays
   at the old f's height. So the f's top curves down like the r's arm
   instead of ending flat.

All worked unslanted.
"""
import math

from fontTools.misc.bezierTools import splitCubicAtT

KAPPA = 0.5522847498
CELL = 600
SB_MIN = 30
BAR = 1.3     # f's crossbar reach from the stem edges x this
BAR_T = 1.6   # ... the t's
ARCH = 0.55   # f: share of the n's arch descent kept, as on the r
END = 0.9     # f: the stroke at the arch's cut is at most this x the arch's reach right of the apex


def stem_edges(pts, tan, y):
    """Unslanted x of the stem's two edges at height y (polygon of on-curves)."""
    ux = [(p.x - p.y * tan, p.y) for p in pts if p.segmentType is not None]
    xs = []
    for (ax, ay), (bx, by) in zip(ux, ux[1:] + ux[:1]):
        if (ay <= y < by) or (by <= y < ay):
            xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
    xs.sort()
    return xs[0], xs[1]


def widen_bar(g, tan, k):
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


def offset(c, d, d1=None):
    """Tiller-Hanson offset of a cubic by d (to the left of its direction),
    or from d at its start to d1 at its end: each control-polygon edge moved
    out by the distance at its middle, neighbours intersected."""
    d1 = d if d1 is None else d1
    at = lambda t: d + (d1 - d) * t
    k = [0]

    def shift(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        e = at((2 * k[0] + 1) / 6)
        k[0] += 1
        nx, ny = -dy / n * e, dx / n * e
        return (a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny)

    def meet(l1, l2):
        (x1, y1), (x2, y2) = l1
        (x3, y3), (x4, y4) = l2
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-9:
            return l1[1]
        a, b = x1 * y2 - y1 * x2, x3 * y4 - y3 * x4
        return ((a * (x3 - x4) - (x1 - x2) * b) / den, (a * (y3 - y4) - (y1 - y2) * b) / den)

    e01 = shift(c[0], c[1])
    e12 = shift(c[1], c[2])
    e23 = shift(c[2], c[3])
    p0, h1, h2, p3 = e01[0], meet(e01, e12), meet(e12, e23), e23[1]
    # the ends exactly d and d1 out along the curve's normals there
    nrm = lambda a, b, e: (-(b[1] - a[1]) / math.hypot(b[0] - a[0], b[1] - a[1]) * e,
                           (b[0] - a[0]) / math.hypot(b[0] - a[0], b[1] - a[1]) * e)
    n0, n3 = nrm(c[0], c[1], d), nrm(c[2], c[3], d1)
    dh1, dh2 = (h1[0] - p0[0], h1[1] - p0[1]), (h2[0] - p3[0], h2[1] - p3[1])
    p0, p3 = (c[0][0] + n0[0], c[0][1] + n0[1]), (c[3][0] + n3[0], c[3][1] + n3[1])
    h1, h2 = (p0[0] + dh1[0], p0[1] + dh1[1]), (p3[0] + dh2[0], p3[1] + dh2[1])
    d = (d + d1) / 2
    # then both handles scaled together so the curve's midpoint lies on the
    # true offset of the original's midpoint (Tiller-Hanson alone runs thin
    # on a tight curve with a thick stroke)
    q = splitCubicAtT(*c, 0.5)[0]
    m, tx, ty = q[3], q[3][0] - q[2][0], q[3][1] - q[2][1]
    tn = math.hypot(tx, ty)
    mo = (m[0] - ty / tn * d, m[1] + tx / tn * d)
    base = ((p0[0] + p3[0]) / 2, (p0[1] + p3[1]) / 2)
    v = (3 / 8 * (h1[0] - p0[0] + h2[0] - p3[0]), 3 / 8 * (h1[1] - p0[1] + h2[1] - p3[1]))
    al = ((mo[0] - base[0]) * v[0] + (mo[1] - base[1]) * v[1]) / (v[0] ** 2 + v[1] ** 2)
    return (p0, (p0[0] + al * (h1[0] - p0[0]), p0[1] + al * (h1[1] - p0[1])),
            (p3[0] + al * (h2[0] - p3[0]), p3[1] + al * (h2[1] - p3[1])), p3)


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
    # outer edge: the n's outer arch from the cut up to the apex, then a
    # quarter ellipse down to the stem's left edge
    ax, ay = outer[3]
    rx = ax - xl
    ry = rx * (n7[1] - n4[1]) / (n7[0] - n4[0])
    c1 = (outer[0], outer[1], outer[2], outer[3])
    c2 = ((ax, ay), (ax - rx * KAPPA, ay), (xl, ay - ry + ry * KAPPA), (xl, ay - ry))
    # inner edge: the outer one offset by the stem's width, so the stroke is
    # as thick as the stem all the way over the top
    # Toward the cut the stroke may taper, where the arch is too tight for
    # the full width (Heavy): at the cut it is at most END x the arch's
    # reach right of the apex, so the inner edge never folds back.
    # The stroke over the top is the r's (the n's) arch at its apex, h,
    # easing from the stem's width where it leaves the stem.
    w = xr - xl
    we = min(h, END * (c1[0][0] - ax))
    sg = 1 if abs(offset(c2, w)[3][0] - xr) < abs(offset(c2, -w)[3][0] - xr) else -1
    o2, o1 = offset(c2, sg * h, sg * w), offset(c1, sg * we, sg * h)
    pout, pin = c1[0], o1[0]
    mx, my = (pin[0] + pout[0]) / 2, (pin[1] + pout[1]) / 2
    rho = math.hypot(pout[0] - pin[0], pout[1] - pin[1]) / 2
    ex, ey = (pout[0] - pin[0]) / (2 * rho), (pout[1] - pin[1]) / (2 * rho)
    # down the arch: away from the outer curve's first handle
    cx, cy = ey, -ex
    if cx * (c1[1][0] - pout[0]) + cy * (c1[1][1] - pout[1]) > 0:
        cx, cy = -cx, -cy
    k = rho * KAPPA
    apex = (mx + cx * rho, my + cy * rho)
    new = [((p.x, p.y), p.segmentType, p.smooth) for p in pts[:14]]
    new += [(sl(*o2[3]), "line", False),
            (sl(*o2[2]), None, False), (sl(*o2[1]), None, False), (sl(*o2[0]), "curve", True),
            (sl(*o1[2]), None, False), (sl(*o1[1]), None, False), (sl(*pin), "curve", False),
            (sl(pin[0] + cx * k, pin[1] + cy * k), None, False),
            (sl(apex[0] - ex * k, apex[1] - ey * k), None, False), (sl(*apex), "curve", True),
            (sl(apex[0] + ex * k, apex[1] + ey * k), None, False),
            (sl(pout[0] + cx * k, pout[1] + cy * k), None, False), (sl(*pout), "curve", False),
            (sl(*c1[1]), None, False), (sl(*c1[2]), None, False), (sl(ax, ay), "curve", True),
            (sl(*c2[1]), None, False), (sl(*c2[2]), None, False),
            (sl(*c2[3]), "curve", False)]
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
    kt = widen_bar(ufo["t"], tan, BAR_T)
    kf = widen_bar(ufo["f"], tan, BAR)
    print(f"  f arch cut at {cut[0]:.0f}/{cut[1]:.0f}; bars t {kt:.2f} f {kf:.2f}")
