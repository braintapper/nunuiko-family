"""Glyph edit 12: 1 without the foot (bottom horizontal stroke).

Port of Nunuïko Display's edit 12. Nunito draws a footless 1 as a
stylistic alternate (one.ss01, one.tosf.ss01: stem with a round bottom
end + flag). Make it the default by SWAPPING outlines: one <-> one.ss01
and one.tosf <-> one.tosf.ss01; ss01 now gives the footed 1.

one.dnom (fractions; one.numr, onesuperior, oneinferior, onehalf,
onequarter are built from it) has no footless alternate, so its foot is
removed by rule. Its 29 nodes follow one's structure: 8..20 are the stem
right edge, the rounded top, the flag and the stem left edge (they map to
one.ss01's 3..15). Keep those; replace the foot with a round stem end
copied from the footless 1 of the same master, scaled by the stem-width
ratio: right side end R, two handles, bottom B, two handles, left side
end L, in one.ss01's order and fractions. Built unslanted, so it follows
the slant in the italic.

Centring: one, one.tosf (after the swap) and the footless one.dnom are
shifted so their left and right sidebearings are equal, measured
unslanted. (Edit 13 then makes one/one.tosf proportional; the centring
still holds for one.dnom.)

Only master layers are written. Run once:  python3 edits/12_one_footless.py
"""
import math

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
SWAPS = (("one", "one.ss01"), ("one.tosf", "one.tosf.ss01"))

font = GSFont(GLYPHS_FILE)
masters = {m.name: m for m in font.masters}


def outline(glyph, mid):
    lay = font.glyphs[glyph].layers[mid]
    assert len(lay.paths) == 1 and not lay.components, glyph
    return [(n.position.x, n.position.y, n.type, n.smooth) for n in lay.paths[0].nodes]


def swap(a, b):
    stock = {g: {m.id: outline(g, m.id) for m in font.masters} for g in (a, b)}
    for g, other in ((a, b), (b, a)):
        assert apply_edit(GLYPHS_FILE, g,
                          lambda mname, layer, nodes, other=other:
                          {"replace_nodes": stock[other][layer.layerId]})
        print(f"{g} <- {other}'s outline")


def centre_shift(xs_ys, width, tan):
    """x shift that makes the unslanted sidebearings equal"""
    ux = [x - y * tan for x, y in xs_ys]
    return width / 2 - (min(ux) + max(ux)) / 2


def centre_edit(mname, layer, nodes):
    tan = math.tan(math.radians(masters[mname].italicAngle))
    pts = [(n.position.x, n.position.y) for n in nodes]
    shift = centre_shift(pts, layer.width, tan)
    print(f"{mname:20s} {layer.parent.name} centred, shifted {shift:+.0f}")
    return {"nodes": {i: (x + shift, y) for i, (x, y) in enumerate(pts)}}


def dnom_edit(mname, layer, nodes):
    m = masters[mname]
    tan = math.tan(math.radians(m.italicAngle))
    un = lambda p: (p[0] - p[1] * tan, p[1])
    re_ = lambda p: (p[0] + p[1] * tan, p[1])
    assert len(nodes) == 29, (mname, len(nodes))
    D = [un((n.position.x, n.position.y)) for n in nodes]
    T = [(n.type, n.smooth) for n in nodes]
    # footless reference (one, since the swap): 20 nodes
    ref = font.glyphs["one"].layers[m.id].paths[0].nodes
    assert len(ref) == 20, (mname, len(ref))
    F = [un((n.position.x, n.position.y)) for n in ref]
    xr_f, xl_f = F[2][0], F[16][0]
    yR_f, B_f = F[2][1], F[19]
    hB = (F[0][0] - B_f[0]) / (xr_f - B_f[0])       # bottom handle, horizontal
    vR = (yR_f - F[1][1]) / (yR_f - B_f[1])         # side handle, vertical
    xr, xl = D[7][0], D[21][0]                      # dnom stem edges at the foot
    s = (xr - xl) / (xr_f - xl_f)
    yB = B_f[1] * s
    yR = yB + (yR_f - B_f[1]) * s
    bx = (xr + xl) / 2
    cap_in = [(bx + hB * (xr - bx), yB, "offcurve", False),
              (xr, yR - vR * (yR - yB), "offcurve", False),
              (xr, yR, "curve", True)]
    cap_out = [(xl, yR, "line", True),
               (xl, yR - vR * (yR - yB), "offcurve", False),
               (bx - hB * (bx - xl), yB, "offcurve", False),
               (bx, yB, "curve", True)]
    body = [(D[i][0], D[i][1], *T[i]) for i in range(8, 21)]
    pts = cap_in + body + cap_out
    shift = centre_shift([re_((x, y)) for x, y, _, _ in pts], layer.width, tan)
    print(f"{mname:20s} one.dnom foot removed, centred, shifted {shift:+.0f}")
    return {"replace_nodes": [(*re_((x, y)), t, sm) for x, y, t, sm in
                              [(x + shift, y, t, sm) for x, y, t, sm in pts]]}


if __name__ == "__main__":
    for a, b in SWAPS:
        swap(a, b)
    font = GSFont(GLYPHS_FILE)  # reload after writing
    masters = {m.name: m for m in font.masters}
    for g in ("one", "one.tosf"):
        assert apply_edit(GLYPHS_FILE, g, centre_edit)
    assert apply_edit(GLYPHS_FILE, "one.dnom", dnom_edit)
    print("done")
