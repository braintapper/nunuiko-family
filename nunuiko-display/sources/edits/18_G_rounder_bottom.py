"""Glyph edit 18: G — the bottom-right follows the O's bowl up to the bar.

References: Bryant (user screenshot, 2026-10-17) and Proxima Nova, keeping
the shape of Nunito's G. Nunito's G runs its right stem straight down
almost to the baseline, about 55 units inside the O's right side at
ExtraLight, so the bottom curve meets it 40-60 units up in a tight corner.
Bryant's G is an O with a gap at the upper right: the bottom-right is the
bowl's own round curve, out to the full width, up to the bar.

So here the G's bottom-right is redrawn on the O's: Nunito's G already
shares the O's skeleton on the left, top and bottom (2026-07-06 log, edit
5). The bar, the upper arm and terminal, the left side and the bottom
point are kept.

Operation, per master, unslanted (x - y tan) in the italic:
  Outer: the curve from the G's outer bottom point B rises to the O's
    rightmost point (its x and height), vertical there, with the tensions
    of the O's own bottom-right quarter. It is cut where it reaches the
    stem's top node L (the bar's top-right corner starts there; the O's
    widest point is just above, at the bar's top), and L moves to the cut.
    The bar's right corner moves across with it. ("cut" construction.)
    Display (Nunito Sans) has a sharp corner L at the bar's top, level with
    or above the O's widest point: there the curve ends vertical at the O's
    widest point (at most 1 below L) and runs straight up to L ("vertical"
    construction). Each file uses one construction for all its masters, so
    they stay compatible.
  Inner: the same with the O's inner contour, from the G's inner bottom
    point up to the O's inner rightmost point, cut at the bar's underside
    U, which moves to the cut. The O's sides are heavier than its bottom
    (Bold: 134 against 110), so the upstroke thickened toward the bar
    (user: "the thickness needs to be a little more consistent on the
    upstroke", subtly); the inner rightmost point is moved out so the side
    keeps only SIDE (0.5) of that extra weight (Bold: 122). The stock inner stem and its notch (a
    hidden overlap) go.
  Advance := the O's (the right side is now the O's), and so for the
    composites built on G (Ğ Ǧ Ĝ Ģ Ġ Ḡ); top and bottom anchors := the O's.

History, same day: the straight stem first started halfway up, then at
~0.7 of the bar height, then with a fuller curve, then 20 units right of
the terminal with the arc rising to the bar; all kept the stock stem's
narrower width, which the user found still off.

The nodes are found by their roles, not their indices, and asserted.
Nunito: 44 -> 38 nodes; Nunito Sans: 31 -> 29. The same in every master.

Run once per source from sources/:
  python3 edits/18_G_rounder_bottom.py [file.glyphs]
"""
import glob
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("*.glyphs"))[0]
SIDE = 0.5   # share of the O's extra side weight (side minus bottom) the G keeps


def bez(p0, p1, p2, p3, t):
    s = 1 - t
    return tuple(s**3 * a + 3 * s * s * t * b + 3 * s * t * t * c + t**3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))

def split(p, t):
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    p01, p12, p23 = lerp(p[0], p[1]), lerp(p[1], p[2]), lerp(p[2], p[3])
    a, b = lerp(p01, p12), lerp(p12, p23)
    c = lerp(a, b)
    return (p[0], p01, a, c), (c, b, p23, p[3])


def at_y(curve, y):
    """t where the curve (rising in y) reaches y."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if bez(*curve, mid)[1] < y:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def o_quarter(o_layer, tan, path):
    """The O's bottom-right quarter on one contour: bottom point, rightmost
    point and their tensions, unslanted."""
    P = [(n.position.x - n.position.y * tan, n.position.y, n.type) for n in o_layer.paths[path].nodes]
    on = [(u, y) for u, y, t in P if t != "offcurve"]
    bot = min(on, key=lambda q: q[1])
    right = max(on, key=lambda q: q[0])
    k = [i for i, (u, y, t) in enumerate(P) if (u, y) == right][0]
    m = len(P)
    # the handles between bottom and right, whichever way the contour runs
    h = [P[(k - 1) % m], P[(k - 2) % m]] if P[(k - 3) % m][:2] == bot else [P[(k + 1) % m], P[(k + 2) % m]]
    assert h[0][2] == h[1][2] == "offcurve"
    hb, hr = (h[1], h[0]) if abs(h[1][1] - bot[1]) < abs(h[0][1] - bot[1]) else (h[0], h[1])
    kx = (hb[0] - bot[0]) / (right[0] - bot[0])
    ky = (right[1] - hr[1]) / (right[1] - bot[1])
    return right, kx, ky


def plan(nodes, tan, o_layer, mode=None):
    """New node list (x, y, type, smooth) for G's single path."""
    m = len(nodes)
    P = [(n.position.x - n.position.y * tan, n.position.y) for n in nodes]
    T = [n.type for n in nodes]
    nx = lambda i: (i + 1) % m

    # outer bottom B and the stem top L
    b = min((i for i in range(m) if T[i] != "offcurve"), key=lambda i: P[i][1])
    li = nx(b)
    while T[li] != "line":
        li = nx(li)
    # inner stem: line U, then a line straight down; the rightmost such pair
    u = max((i for i in range(m) if T[i] == "line" and T[nx(i)] == "line"
             and abs(P[nx(i)][0] - P[i][0]) < 2 and P[i][1] - P[nx(i)][1] > 60),
            key=lambda i: P[i][0])
    run = [nx(u)]
    while T[nx(run[-1])] == "line":
        run.append(nx(run[-1]))
    o1, o2, ib = nx(run[-1]), nx(nx(run[-1])), nx(nx(nx(run[-1])))
    assert T[o1] == T[o2] == "offcurve" and T[ib] == "curve", "inner bottom"

    (ro, kxo, kyo), (ri, kxi, kyi) = o_quarter(o_layer, tan, 0), o_quarter(o_layer, tan, 1)
    if ro[0] < ri[0]:
        (ro, kxo, kyo), (ri, kxi, kyi) = (ri, kxi, kyi), (ro, kxo, kyo)
    bx, by = P[b]
    ibx, iby = P[ib]
    # the O's sides are heavier than its bottom; the G's upstroke keeps only
    # SIDE of that extra weight, so it thickens less toward the bar
    tb, ts = iby - by, ro[0] - ri[0]
    ri = (ro[0] - (tb + SIDE * (ts - tb)), ri[1])
    if mode is None:  # first pass: which way this master would go
        return "cut" if ro[1] > P[li][1] + 5 else "vertical"
    assert ri[1] > P[u][1] + 5, "the O's inner side is widest above the bar's underside"
    if mode == "vertical":
        # Display: the bar's top-right is a sharp corner L at the bar's top,
        # level with (or above) the O's widest point: the curve ends vertical
        # at the O's widest point (at most 1 below L), then straight up to L
        ro = (ro[0], min(ro[1], P[li][1] - 1))
    outer = ((bx, by), (bx + kxo * (ro[0] - bx), by), (ro[0], ro[1] - kyo * (ro[1] - by)), ro)
    inner = ((ibx, iby), (ibx + kxi * (ri[0] - ibx), iby), (ri[0], ri[1] - kyi * (ri[1] - iby)), ri)
    if mode == "cut":
        oc, _ = split(outer, at_y(outer, P[li][1]))
    else:
        oc = outer
    ic, _ = split(inner, at_y(inner, P[u][1]))

    # the bar's right corner moves across with L
    dx = oc[3][0] - P[li][0]
    lpos = oc[3] if mode == "cut" else (oc[3][0], P[li][1])
    i, span = li, []
    while i != u:
        span.append(i)
        i = nx(i)
    mid = (min(P[i][0] for i in span) + P[u][0]) / 2
    moved = {i for i in span if P[i][0] > mid and i != li}
    P = [(x + dx, y) if i in moved else (x, y) for i, (x, y) in enumerate(P)]
    P[li] = lpos
    P[u] = ic[3]

    sl = lambda x, y: (x + y * tan, y)
    drop_outer = []
    i = nx(b)
    while i != li:
        drop_outer.append(i)
        i = nx(i)
    drop_inner = run + [o1, o2]
    outer_new = [(*sl(*oc[1]), "offcurve", False), (*sl(*oc[2]), "offcurve", False)]
    if mode == "vertical":
        outer_new.append((*sl(*oc[3]), "curve", True))
    inner_new = [(*sl(*ic[2]), "offcurve", False), (*sl(*ic[1]), "offcurve", False)]

    out = []
    for i in range(m):
        if i in drop_outer or i in drop_inner:
            if i == drop_outer[0]:
                out += outer_new
            if i == drop_inner[0]:
                out += inner_new
            continue
        n = nodes[i]
        cut = mode == "cut" and i == li
        out.append((*sl(*P[i]), "curve" if cut else n.type, n.smooth or cut))
    info = (f"right side {P[li][0] - dx:.0f} -> {P[li][0]:.0f} (O {ro[0]:.0f} at {ro[1]:.0f}); "
            f"inner meets the bar at {P[u][0]:.0f}; {m} -> {len(out)} nodes")
    return out, info


def main():
    font = GSFont(GLYPHS_FILE)
    angles = {m.name: m.italicAngle for m in font.masters}
    ids = {m.name: m.id for m in font.masters}
    widths = {}
    # one construction for the whole file, so the masters stay compatible
    modes = {plan([n for p in l.paths for n in p.nodes], math.tan(math.radians(m.italicAngle)),
                  font.glyphs["O"].layers[m.id])
             for m in font.masters for l in [font.glyphs["G"].layers[m.id]]}
    mode = "cut" if modes == {"cut"} else "vertical"
    print(f"  construction: {mode}")

    def edit(mname, layer, nodes):
        assert len(layer.paths) == 1, mname
        o = font.glyphs["O"].layers[ids[mname]]
        out, info = plan(nodes, math.tan(math.radians(angles[mname])), o, mode)
        widths[layer.layerId] = (layer.width, o.width)
        print(f"  {mname:32s} {info}; width {layer.width:g} -> {o.width:g}")
        anchors = {a.name: (a.position.x, a.position.y) for a in o.anchors if a.name in ("top", "bottom")}
        return {"replace_nodes": out, "width": round(o.width), "anchors": anchors}

    changed = apply_edit(GLYPHS_FILE, "G", edit)
    # composites built on G (Ğ Ǧ Ĝ Ģ Ġ Ḡ ...) get the same width change
    for g in font.glyphs:
        layers = [l for l in g.layers if l.layerId in widths]
        if g.name == "G" or not layers or not all(
                l.components and l.components[0].name == "G" and not l.paths
                and abs(l.width - widths[l.layerId][0]) < 0.5 for l in layers):
            continue
        apply_edit(GLYPHS_FILE, g.name,
                   lambda mname, layer, nodes: {"width": round(layer.width + widths[layer.layerId][1] - widths[layer.layerId][0])})
        print("  width follows:", g.name)
    print("written" if changed else "unchanged", GLYPHS_FILE)


if __name__ == "__main__":
    main()
