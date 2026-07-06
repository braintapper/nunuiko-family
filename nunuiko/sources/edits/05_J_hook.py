"""Glyph edit 5: capital J — upturned bottom terminal (hooked foot).

Reference: Google Sans Flex J. Nunito's J sweeps left and dies at the
baseline; the new foot is a U-hook: down the stem, around the bowl, up
the left side, ending in a rounded cap built exactly like the stem's own
top cap — so every corner stays in Nunito's rounded vocabulary.

Everything derives from the J's own landmarks per master:
  - stem right/left x and curve-start y  (old nodes 3 / 11)
  - leftmost extent xO                    (old node 18 — LSB preserved)
  - inner bottom y (taper: Bold/Heavy J bottoms are already thinner
    than the stem)                        (old node 14)
  - outer bottom overshoot                (old node 0)
  - hook weight = min(stem weight, HOOK_MAX_FRAC * (stem_left - xO)) —
    Heavy can't fit a full-weight U (215 * 2 > 370 span), same cap idea
    as the Q slash
  - terminal height H = H_FRAC * stem curve-start y
Italic masters: landmarks deslanted by tan(9 deg), constructed upright,
reslanted. Stem + top cap nodes (old 3..11) are kept verbatim.

22 -> 26 nodes. Run once from sources/: python3 edits/05_J_hook.py
"""
import math

from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
H_FRAC = 0.9            # terminal height, fraction of stem curve-start y
HOOK_MAX_FRAC = 0.55    # hook weight cap, fraction of the left span
KAPPA = 0.5523          # quarter-arc control tension
SLANT = math.tan(math.radians(9))


def edit(mname, layer, nodes):
    assert len(nodes) == 22, (mname, len(nodes))
    for i, t, sm in ((0, "line", True), (3, "curve", True), (4, "line", True),
                     (11, "line", True), (14, "curve", True), (18, "curve", True)):
        assert nodes[i].type == t and nodes[i].smooth == sm, (mname, i)

    s = SLANT if "Italic" in mname else 0.0
    de = lambda n: (n.position.x - s * n.position.y, n.position.y)
    re_ = lambda x, y: (x + s * y, y)

    sr_x, y3 = de(nodes[3])          # stem right (deslanted), curve start
    sl_x, y11 = de(nodes[11])        # stem left
    xO = de(nodes[18])[0]            # hook outer left (preserves extent)
    apexI_y = nodes[14].position.y   # inner bottom (keeps original taper)
    apexO_y = nodes[0].position.y    # outer bottom overshoot

    w_stem = sr_x - sl_x
    w_hook = min(w_stem, HOOK_MAX_FRAC * (sl_x - xO))
    xI = xO + w_hook
    H = H_FRAC * y3
    rise = w_hook / 2
    midx = (xO + xI) / 2
    apexI_x = (sl_x + xI) / 2
    apexO_x = (sr_x + xO) / 2
    k = KAPPA

    def orig(i):
        n = nodes[i]
        return (n.position.x, n.position.y, n.type, n.smooth)

    out = [
        (*re_(sr_x, y3), "curve", True),                              # stem R base
        orig(4), orig(5), orig(6), orig(7), orig(8), orig(9), orig(10),
        orig(11),                                                     # stem L base
        (*re_(sl_x, y11 - k * (y11 - apexI_y)), "offcurve", False),
        (*re_(apexI_x + k * (sl_x - apexI_x), apexI_y), "offcurve", False),
        (*re_(apexI_x, apexI_y), "curve", True),                      # inner apex
        (*re_(apexI_x - k * (apexI_x - xI), apexI_y), "offcurve", False),
        (*re_(xI, apexI_y + k * (H - apexI_y)), "offcurve", False),
        (*re_(xI, H), "curve", True),                                 # inner terminal base
        (*re_(xI, H + k * rise), "offcurve", False),
        (*re_(midx + k * (xI - midx), H + rise), "offcurve", False),
        (*re_(midx, H + rise), "curve", True),                        # cap top
        (*re_(midx - k * (midx - xO), H + rise), "offcurve", False),
        (*re_(xO, H + k * rise), "offcurve", False),
        (*re_(xO, H), "curve", True),                                 # outer terminal base
        (*re_(xO, H - k * (H - apexO_y)), "offcurve", False),
        (*re_(apexO_x - k * (apexO_x - xO), apexO_y), "offcurve", False),
        (*re_(apexO_x, apexO_y), "curve", True),                      # outer apex
        (*re_(apexO_x + k * (sr_x - apexO_x), apexO_y), "offcurve", False),
        (*re_(sr_x, y3 - k * (y3 - apexO_y)), "offcurve", False),
    ]
    assert len(out) == 26
    print(f"{mname:20s} w_stem={w_stem:.0f} w_hook={w_hook:.0f} "
          f"xO={xO:.0f} H={H:.0f} cap_top={H + rise:.0f}")
    return {"replace_nodes": out}


if __name__ == "__main__":
    assert apply_edit(GLYPHS_FILE, "J", edit)
    print("done")
