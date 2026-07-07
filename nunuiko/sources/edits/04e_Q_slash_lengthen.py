"""Glyph edit 4e: Q slash — lengthen further (ExtraLight), matching the SFD.

The user's fonts/Nunuiko-ExtraLight.sfd extends the slash capsule a further
~13 units at each end (purely along the slash axis; the perpendicular drift
is <3u = rounding). Reproducing it is a rigid translation of each rounded
cap — every corner then matches the SFD to the unit, so the capsule stays a
perfect capsule (caps and stroke width untouched):

  bottom-right cap (nodes 0-6)  += (+11, -7)
  top-left cap     (nodes 7-13) += ( -9, +10)

Applied to the _part.Qtail component at ExtraLight only; node count
unchanged -> interpolation-safe. Bold/Heavy keep their edit-4d length
(the SFD gives no reference for them; per CLAUDE.md the ExtraLight-Bold
range is what matters).

Run once from sources/: python3 edits/04e_Q_slash_lengthen.py
"""
from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
BR_CAP = range(0, 7)    # bottom-right rounded end
TL_CAP = range(7, 14)   # top-left rounded end
BR_DELTA = (11, -7)
TL_DELTA = (-9, 10)


def edit(mname, layer, nodes):
    if mname != "ExtraLight":
        return {}
    assert len(nodes) == 14, (mname, len(nodes))
    new = {}
    for i in BR_CAP:
        new[i] = (nodes[i].position.x + BR_DELTA[0], nodes[i].position.y + BR_DELTA[1])
    for i in TL_CAP:
        new[i] = (nodes[i].position.x + TL_DELTA[0], nodes[i].position.y + TL_DELTA[1])
    print(f"{mname:12s} slash caps: BR += {BR_DELTA}, TL += {TL_DELTA}")
    return {"nodes": new}


if __name__ == "__main__":
    changed = apply_edit(GLYPHS_FILE, "_part.Qtail", edit)
    print("done" if changed else "nothing changed — already applied?")
