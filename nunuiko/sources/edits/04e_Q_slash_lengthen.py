"""Glyph edit 4e: Q slash — lengthen the capsule at every weight/slant.

Originally 4e lengthened the slash only at ExtraLight upright, using literal
cap deltas copied from the user's ExtraLight SFD (+ (11,-7) / (-9,10)). That
left Bold/Heavy upright and all three italics at the shorter 4d length, so the
extra length faded out with weight and the italic Q didn't match the roman.

Reformulated as a geometric rule so it applies in every master, upright and
slanted: the slash is a rigid capsule with two rounded caps (nodes 0-6 =
bottom-right end, nodes 7-13 = top-left end) joined by two straight edges.
Its axis is the line through the two cap "shoulder" midpoints; extending it =
sliding each cap group rigidly OUTWARD along that axis by EXTEND_FRAC of the
slash length. Computing the axis from each master's own node positions makes
it work for the italics automatically (their axis is already slanted).

ExtraLight upright is LEFT UNTOUCHED — it keeps the exact SFD values the user
accepted; EXTEND_FRAC (0.05) is calibrated to reproduce that same ~13u/end,
so the other masters come out visually consistent with it. Rigid cap
translation preserves the caps and stroke width exactly; node count unchanged
-> interpolation-safe.

Run once from sources/: python3 edits/04e_Q_slash_lengthen.py
"""
import math

from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
BR_CAP = range(0, 7)     # bottom-right rounded end
TL_CAP = range(7, 14)    # top-left rounded end
EXTEND_FRAC = 0.05       # extra length each end, as fraction of slash length
SKIP = {"ExtraLight"}    # already carries the exact SFD 4e values


def edit(mname, layer, nodes):
    if mname in SKIP:
        return {}
    assert len(nodes) == 14, (mname, len(nodes))
    xy = lambda i: (nodes[i].position.x, nodes[i].position.y)
    # cap shoulder midpoints (where each cap meets the straight edges)
    br_mid = tuple((xy(0)[k] + xy(6)[k]) / 2 for k in (0, 1))
    tl_mid = tuple((xy(7)[k] + xy(13)[k]) / 2 for k in (0, 1))
    axis = (br_mid[0] - tl_mid[0], br_mid[1] - tl_mid[1])
    length = math.hypot(*axis)
    unit = (axis[0] / length, axis[1] / length)
    d = EXTEND_FRAC * length

    new = {}
    for i in BR_CAP:       # slide toward bottom-right (+axis)
        new[i] = (xy(i)[0] + d * unit[0], xy(i)[1] + d * unit[1])
    for i in TL_CAP:       # slide toward top-left (-axis)
        new[i] = (xy(i)[0] - d * unit[0], xy(i)[1] - d * unit[1])
    print(f"{mname:16s} slash len {length:.0f}  extend {d:.0f}/end "
          f"along ({unit[0]:.2f},{unit[1]:.2f})")
    return {"nodes": new}


if __name__ == "__main__":
    changed = apply_edit(GLYPHS_FILE, "_part.Qtail", edit)
    print("done" if changed else "nothing changed — already applied?")
