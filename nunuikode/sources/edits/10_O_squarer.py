"""Code edit 10: a boxier O (and so Q, Ö, Ø and the other O composites).

Nunuiko's O is a near-ellipse: each quarter is one cubic whose handles
run 0.6-0.65 of the way to the corner of its box. Here every handle of
the outer contour goes SQUARE (0.35) of the rest of the way to that
corner, so the sides run straighter and the corners turn on a smaller
radius. The counter's handles are then set so the stroke across each
corner's diagonal is CORNER (1.06) x the mean of the stroke at the
quarter's two ends: a boxy O whose corners are as thick as its sides
looks thinner there, and the monospace step's condensing thins them
a little more. The counter's tension stays at most MAX_T, past which it
would read as a rectangle.

The corner of each quarter is where its two handle lines meet, so the
same code works on the upright and the slanted (italic) masters. Node
count and types are unchanged. Q is O plus its slash part, so the slash
still crosses the ring; OE is drawn on its own and is left as it is.
"""
import math

SQUARE = 0.35   # share of the remaining way to the corner each outer handle moves
CORNER = 1.06   # stroke at each corner's diagonal / the mean of the stroke at its two ends
MAX_T = 0.85    # the counter's handles stop at this tension


def quarters(c):
    """(P0, h1, h2, P3) point quadruples of a 12-point O contour."""
    pts = list(c)
    n = len(pts)
    on = [k for k in range(n) if pts[k].segmentType is not None]
    assert n == 12 and len(on) == 4, n
    out = []
    for k in on:
        a, b, d = pts[(k + 1) % n], pts[(k + 2) % n], pts[(k + 3) % n]
        assert a.segmentType is None and b.segmentType is None and d.segmentType, "O quarter"
        out.append((pts[k], a, b, d))
    return out


def corner(p0, h1, h2, p3):
    """Where the lines p0-h1 and p3-h2 meet."""
    ax, ay = h1.x - p0.x, h1.y - p0.y
    bx, by = h2.x - p3.x, h2.y - p3.y
    det = ax * by - ay * bx
    assert abs(det) > 1e-6, "parallel handles"
    s = ((p3.x - p0.x) * by - (p3.y - p0.y) * bx) / det
    return p0.x + ax * s, p0.y + ay * s


def plan(q):
    p0, h1, h2, p3 = q
    cx, cy = corner(*q)
    l1 = math.hypot(cx - p0.x, cy - p0.y)
    l2 = math.hypot(cx - p3.x, cy - p3.y)
    t1 = math.hypot(h1.x - p0.x, h1.y - p0.y) / l1
    t2 = math.hypot(h2.x - p3.x, h2.y - p3.y) / l2
    return (cx, cy), (l1, l2), (t1, t2)


def set_t(p, h, c, t):
    h.x, h.y = p.x + (c[0] - p.x) * t, p.y + (c[1] - p.y) * t


def bez(q, t):
    s = 1 - t
    return (s ** 3 * q[0].x + 3 * s * s * t * q[1].x + 3 * s * t * t * q[2].x + t ** 3 * q[3].x,
            s ** 3 * q[0].y + 3 * s * s * t * q[1].y + 3 * s * t * t * q[2].y + t ** 3 * q[3].y)


def near(m, p):
    """m's end point nearest p."""
    return min((m[0], m[3]), key=lambda r: math.hypot(r.x - p.x, r.y - p.y))


def diagonal(q, m):
    """Stroke across the corner: from the outer curve's midpoint to the
    nearest point of the counter's curve."""
    x, y = bez(q, 0.5)
    return min(math.hypot(x - a, y - b) for a, b in (bez(m, k / 200) for k in range(201)))


def apply(ufo, stem, tan):
    g = ufo["O"]
    assert not g.components and len(g) == 2, "O"
    area = lambda c: sum(a.x * b.y - b.x * a.y for a, b in zip(list(c), list(c)[1:] + list(c)[:1]))
    outer, inner = sorted(g, key=lambda c: -abs(area(c)))
    qo, qi = quarters(outer), quarters(inner)
    # match each counter quarter to the outer one facing the same way
    mid = lambda q: ((q[0].x + q[3].x) / 2, (q[0].y + q[3].y) / 2)
    cxo = sum(p.x for p in outer) / 12
    cyo = sum(p.y for p in outer) / 12
    ang = lambda q: math.atan2(mid(q)[1] - cyo, mid(q)[0] - cxo)
    log = []
    for q in qo:
        c, (l1, l2), (t1, t2) = plan(q)
        m = min(qi, key=lambda r: abs(math.remainder(ang(r) - ang(q), 2 * math.pi)))
        ci, (k1, k2), (u1, u2) = plan(m)
        n1, n2 = t1 + SQUARE * (1 - t1), t2 + SQUARE * (1 - t2)
        set_t(q[0], q[1], c, n1)
        set_t(q[3], q[2], c, n2)
        # the counter: one tension for both handles, solved so the stroke
        # across the diagonal is CORNER x the mean of the ends' strokes
        ends = (math.hypot(q[0].x - near(m, q[0]).x, q[0].y - near(m, q[0]).y)
                + math.hypot(q[3].x - near(m, q[3]).x, q[3].y - near(m, q[3]).y)) / 2
        target = CORNER * ends
        lo, hi = 0.3, MAX_T
        for _ in range(40):
            v = (lo + hi) / 2
            set_t(m[0], m[1], ci, v)
            set_t(m[3], m[2], ci, v)
            if diagonal(q, m) > target:
                lo = v  # too thick: square the counter more
            else:
                hi = v
        log.append(f"{t1:.2f}->{n1:.2f}/{min(u1, u2):.2f}->{v:.2f} ({diagonal(q, m):.0f}/{ends:.0f})")
    print("  O tension outer/counter:", ", ".join(log))
