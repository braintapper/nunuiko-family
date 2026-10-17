"""Glyph edit 24: 6 — a shorter tail (shared by Nunuiko and Display).

The 6's tail is the hook over the top: from the top of the stem it runs
right and down to a terminal (Nunuiko: a round end; Display: a flat cut).
It is cut back so it reaches KEEP (0.7) as far right of the top point as
it did. Applied to six, six.tosf and six.dnom (numerators, superiors and
inferiors are built from six.dnom and follow).

Operation, per master, in place (the cut is perpendicular to the stroke as
drawn, so no unslanting):
  Outer edge: the curve from the top point T to the old outer end Eo is
    split where x = T.x + KEEP x (Eo.x - T.x); the part next to T is kept.
  Inner edge: the curve from the inner top Ti to the old inner end Ei is
    split where the line through the new outer end, perpendicular to the
    stroke there, crosses it.
  End: Nunuiko's round end (one curve from Ei to Eo) is redrawn as a
    half-circle across the stroke, handles 4/3 x the radius along the
    stroke; Display keeps a flat cut.
Node count and types are unchanged.

Run once per source from sources/:
  python3 edits/24_six_short_tail.py [file.glyphs]
"""
import glob
import importlib.util
import math
import os
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("*.glyphs"))[0]
KEEP = 0.7
GLYPHS = ("six", "six.tosf", "six.dnom")
_spec = importlib.util.spec_from_file_location(
    "edit22", os.path.join(os.path.dirname(__file__), "22_ampersand_short_arm.py"))
e22 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e22)


def plan(nodes, rounded):
    m = len(nodes)
    P = [(n.position.x, n.position.y) for n in nodes]
    T = [n.type for n in nodes]
    on = [i for i in range(m) if T[i] != "offcurve"]
    t = max(on, key=lambda i: P[i][1])
    eo = (t - 3) % m
    ei = (eo - (3 if rounded else 1)) % m
    ti = (ei - 3) % m
    assert T[(t - 1) % m] == T[(t - 2) % m] == "offcurve" and T[eo] != "offcurve", "outer"
    assert T[ei] == "curve" and T[(ei - 1) % m] == T[(ei - 2) % m] == "offcurve" \
        and T[ti] != "offcurve", "inner"
    outer = (P[t], P[(t - 1) % m], P[(t - 2) % m], P[eo])  # from the top out
    inner = (P[ti], P[(ti + 1) % m], P[(ti + 2) % m], P[ei])
    xo = P[t][0] + KEEP * (P[eo][0] - P[t][0])
    to = e22.solve(lambda s: e22.bez(outer, s)[0] - xo)
    o1, _ = e22.split(outer, to)
    a = o1[3]
    d = (o1[3][0] - o1[2][0], o1[3][1] - o1[2][1])
    dl = math.hypot(*d)
    d = (d[0] / dl, d[1] / dl)
    ti_ = e22.solve(lambda s: (e22.bez(inner, s)[0] - a[0]) * d[0]
                    + (e22.bez(inner, s)[1] - a[1]) * d[1])
    i1, _ = e22.split(inner, ti_)
    b = i1[3]
    new = {(t - 1) % m: o1[1], (t - 2) % m: o1[2], eo: a,
           (ti + 1) % m: i1[1], (ti + 2) % m: i1[2], ei: b}
    if rounded:
        r = math.hypot(a[0] - b[0], a[1] - b[1]) / 2
        h = 4 / 3 * r
        new[(ei + 1) % m] = (b[0] + h * d[0], b[1] + h * d[1])
        new[(ei + 2) % m] = (a[0] + h * d[0], a[1] + h * d[1])
    return new, f"outer end ({P[eo][0]:.0f}, {P[eo][1]:.0f}) -> ({a[0]:.0f}, {a[1]:.0f})"


def main():
    font = GSFont(GLYPHS_FILE)
    rounded = ".formatVersion = 3;" not in open(GLYPHS_FILE).read()
    for name in GLYPHS:
        def edit(mname, layer, nodes):
            n0 = len(layer.paths[0].nodes)
            new, info = plan(nodes[:n0], rounded)
            print(f"  {name:10s} {mname:32s} {info}")
            return {"nodes": new}
        apply_edit(GLYPHS_FILE, name, edit)
    print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
