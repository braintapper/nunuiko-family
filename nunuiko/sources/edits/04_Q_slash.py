"""Glyph edit 4: Q slashed tail, Jost-style, baseline-aligned.

Design (user spec): replace Nunito's curved below-baseline Qtail swash
with a straight Jost-like slash crossing the bowl's bottom-right ring.
The slash's LOWEST corner sits exactly on the baseline (y = 0) — the new
Q has no descender.

Q = O component + _part.Qtail component, so only _part.Qtail changes
(12 curved nodes -> rotated rectangle with lightly rounded corners:
r = CORNER_R_FRAC * slash weight, matching the font's soft vocabulary).

All geometry is derived from O's own outlines per master:
  - M     = midpoint between the outer and inner bottom-right arc
            midpoints (t=0.5) — the ring midline at ~4:30
  - w     = distance between those arc midpoints — the ring thickness
  - d     = slash direction, 45 deg down-right; sheared by the italic
            angle (9 deg) for italic masters
  - outer tip: solved so the lower corner has y = 0
  - inner tip: from the inner arc midpoint, K_IN_FRAC of the counter
            radius further along -d (scales with the counter, not the
            ring, so Heavy doesn't get speared)
Coordinates are converted from O-space to part-local space via Q's
per-master component offset. Winding matched to O's outer ring so the
overlap unions (not cancels) under nonzero fill.

Run once from sources/: python3 edits/04_Q_slash.py
"""
import math

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
ANGLE_DEG = 45          # slash angle below horizontal, upright masters
ITALIC_SHEAR = math.tan(math.radians(9))
K_IN_FRAC = 0.35        # inner tip: fraction of counter radius past the ring
MAX_COUNTER_FRAC = 0.6  # slash weight cap, as fraction of counter radius
CORNER_R_FRAC = 0.18    # corner fillet radius, as fraction of slash weight
FILLET_TENSION = 0.5523 # circle-approximation control distance


def cubic_point(p0, c1, c2, p3, t):
    u = 1 - t
    return tuple(
        u**3 * p0[i] + 3 * u * u * t * c1[i] + 3 * u * t * t * c2[i] + t**3 * p3[i]
        for i in (0, 1)
    )


def xy(n):
    return (n.position.x, n.position.y)


def signed_area(points):
    s = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        s += x1 * y2 - x2 * y1
    return s / 2


def edit_factory(font):
    masters = {m.id: m.name for m in font.masters}
    o_layers = {l.layerId: l for l in font.glyphs["O"].layers
                if l.layerId in masters}
    q_offsets = {}
    for l in font.glyphs["Q"].layers:
        if l.layerId in masters:
            (tail_comp,) = [c for c in l.components if c.name == "_part.Qtail"]
            q_offsets[l.layerId] = (tail_comp.position.x, tail_comp.position.y)

    def edit(mname, layer, nodes):
        o = o_layers[layer.layerId]
        outer, inner = o.paths[0].nodes, o.paths[1].nodes
        # bottom-right arcs: outer 11 -> (0,1) -> 2 ; inner 8 -> (9,10) -> 11
        om = cubic_point(xy(outer[11]), xy(outer[0]), xy(outer[1]), xy(outer[2]), 0.5)
        im = cubic_point(xy(inner[8]), xy(inner[9]), xy(inner[10]), xy(inner[11]), 0.5)
        M = ((om[0] + im[0]) / 2, (om[1] + im[1]) / 2)
        w_ring = math.dist(om, im)

        a = math.radians(ANGLE_DEG)
        d = (math.cos(a), -math.sin(a))
        if "Italic" in mname:
            d = (d[0] + ITALIC_SHEAR * d[1], d[1])
            norm = math.hypot(*d)
            d = (d[0] / norm, d[1] / norm)
        n = (-d[1], d[0])  # n[1] > 0: +n is the upper side

        c_inner = tuple(sum(xy(inner[i])[j] for i in (2, 5, 8, 11)) / 4
                        for j in (0, 1))
        counter_r = math.dist(im, c_inner)
        # cap the slash weight against the counter so Heavy keeps an open
        # counter and a visible outer stub (full ring weight would swallow it)
        w = min(w_ring, MAX_COUNTER_FRAC * counter_r)

        t_out = ((w / 2) * n[1] - M[1]) / d[1]
        assert t_out > 0, (mname, t_out)
        E_out = (M[0] + t_out * d[0], M[1] + t_out * d[1])
        p_in = K_IN_FRAC * counter_r
        E_in = (im[0] - p_in * d[0], im[1] - p_in * d[1])

        half = (n[0] * w / 2, n[1] * w / 2)
        c_in_lo = (E_in[0] - half[0], E_in[1] - half[1])
        c_in_hi = (E_in[0] + half[0], E_in[1] + half[1])
        c_out_lo = (E_out[0] - half[0], E_out[1] - half[1])
        c_out_hi = (E_out[0] + half[0], E_out[1] + half[1])
        assert abs(c_out_lo[1]) < 0.51, (mname, c_out_lo)

        rect = [c_in_lo, c_out_lo, c_out_hi, c_in_hi]
        if signed_area(rect) * signed_area([xy(p) for p in outer]) < 0:
            rect.reverse()

        # round each corner (r before/after, circle-approx tension) — the
        # font rounds everything; flat Jost cuts looked out of place
        r = CORNER_R_FRAC * w
        lerp = lambda p, q, k: (p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)
        nodes_out = []
        for i, P in enumerate(rect):
            A = lerp(P, rect[i - 1], r / math.dist(P, rect[i - 1]))
            B = lerp(P, rect[(i + 1) % 4], r / math.dist(P, rect[(i + 1) % 4]))
            nodes_out.append((A[0], A[1], "line", True))
            for ctrl in (lerp(A, P, FILLET_TENSION), lerp(B, P, FILLET_TENSION)):
                nodes_out.append((ctrl[0], ctrl[1], "offcurve", False))
            nodes_out.append((B[0], B[1], "curve", True))

        # the fillet lifts the lowest ink ~0.41r above the baseline; shift
        # the whole slash down so the rounded corner touches y=0 exactly
        min_y = min(
            cubic_point(nodes_out[k][:2], nodes_out[k + 1][:2],
                        nodes_out[k + 2][:2], nodes_out[k + 3][:2], t / 20)[1]
            for k in range(0, 16, 4) for t in range(21)
        )
        ox, oy = q_offsets[layer.layerId]
        nodes_out = [(x - ox, y - min_y - oy, t, sm) for x, y, t, sm in nodes_out]
        print(f"{mname:20s} w_slash={w:.0f} r={r:.0f} drop={min_y:.1f} "
              f"tips in=({E_in[0]:.0f},{E_in[1]:.0f}) out=({E_out[0]:.0f},{E_out[1]:.0f})")
        return {"replace_nodes": nodes_out}

    return edit


if __name__ == "__main__":
    font = GSFont(GLYPHS_FILE)
    assert apply_edit(GLYPHS_FILE, "_part.Qtail", edit_factory(font))
    print("done")
