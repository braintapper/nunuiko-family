"""Glyph edit 9: K and k — the leg grows out of the arm (Proxima Nova style).

Port of Nunuïko Display's edit 9 to Nunito's rounded construction. Stock
Nunito draws K/k as a chevron: arm and leg both meet the stem. Here the
leg is detached from the stem: both of its edges end on the underside of
the arm, so the open space below the arm runs up to it.

Landmarks (34-node path, same structure in every master, upright and
italic; K, k and kgreenlandic):
  2 -> 3    stem right edge (3: where the outline leaves the stem)
  4 -> 5    leg lower/left edge        5..11  rounded foot cap
  11 -> 12  leg upper/right edge       12 -> 13  notch face
  13 -> 14  arm bottom edge            14..20 rounded arm tip
  21 .. 1   arm top, stem (untouched)

Rule, per master (worked unslanted: x - y*tan(italic angle)):
  S  = stem right edge (2-3) ∩ arm bottom line (13-14)
  Cf = foot-cap centre (midpoint of 5 and 11)
  The leg pivots RIGIDLY: the cap (5..11) rotates about Cf by the angle
  that points the leg axis at a point C on the arm, then shifts
  vertically so its lowest node keeps its original height (overshoot).
  The leg edges continue the rotated cap's ends in the rotated
  directions, so 5 and 11 stay smooth.
  C is solved by bisection so the leg's lower edge meets the arm at
  GAP_FRAC of the way from S to the tip (same knob as Display), unless
  that swings the leg more than MAX_TURN (12 deg): then, of the positions
  within 12 deg, the one whose gap is closest to GAP_FRAC (only Heavy
  Italic K and the Heavy k/ĸ masters, all above 700).
  3 = S; 4 / 12 = lower / upper edge ∩ arm; 13 = midpoint of 12 and 14
  (on the arm, keeps the 34-node structure).

Kcommaaccent / kcommaaccent are composites; Cyrillic Ka-cy / ka-cy stay
stock. Run once:  python3 edits/09_K_leg_from_arm.py   (--dry-run prints)
"""
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
DRY = "--dry-run" in sys.argv
GAP_FRAC = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--gap=")), 0.15))
MAX_TURN = 12  # degrees: the rounded foot can't swing far (heavy k would
               # need 33-44 deg for the full gap); past this, the gap gives
CAP = range(5, 12)
STRUCT = "oocslllsoocsoocslllsoocsoocslllsoocsoocslsoocs"

_font = GSFont(GLYPHS_FILE)
_angle = {m.name: m.italicAngle for m in _font.masters}


def intersect(p1, d1, q1, q2):
    """Line through p1 with direction d1, intersected with line q1-q2."""
    d2 = (q2[0] - q1[0], q2[1] - q1[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    assert abs(den) > 1e-9, "parallel"
    t = ((q1[0] - p1[0]) * d2[1] - (q1[1] - p1[1]) * d2[0]) / den
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def struct(nodes):
    return "".join(n.type[0] + ("s" if n.smooth else "") for n in nodes)


def edit(mname, layer, nodes):
    assert len(nodes) == 34 and struct(nodes) == STRUCT, (mname, struct(nodes))
    tan = math.tan(math.radians(_angle[mname]))
    un = lambda p: (p[0] - p[1] * tan, p[1])
    re_ = lambda p: (p[0] + p[1] * tan, p[1])
    P = [un((n.position.x, n.position.y)) for n in nodes]

    S = intersect(P[2], (P[3][0] - P[2][0], P[3][1] - P[2][1]), P[13], P[14])
    arm = (P[14][0] - S[0], P[14][1] - S[1])
    along = lambda p: ((p[0] - S[0]) * arm[0] + (p[1] - S[1]) * arm[1]) / (
        arm[0] ** 2 + arm[1] ** 2)
    Cf = ((P[5][0] + P[11][0]) / 2, (P[5][1] + P[11][1]) / 2)
    lo_dir = (P[4][0] - P[5][0], P[4][1] - P[5][1])     # up the lower edge
    hi_dir = (P[12][0] - P[11][0], P[12][1] - P[11][1])  # up the upper edge
    axis0 = math.atan2(lo_dir[1], lo_dir[0])  # leg edges are parallel
    ymin0 = min(P[i][1] for i in CAP)

    def build(c):
        C = (S[0] + c * arm[0], S[1] + c * arm[1])
        dy, da = 0.0, 0.0
        for _ in range(6):  # rotation and baseline shift settle together
            da = math.atan2(C[1] - (Cf[1] + dy), C[0] - Cf[0]) - axis0
            cap = {i: rot((P[i][0] - Cf[0], P[i][1] - Cf[1]), da) for i in CAP}
            dy = ymin0 - min(Cf[1] + v[1] for v in cap.values())
        cap = {i: (Cf[0] + v[0], Cf[1] + v[1] + dy) for i, v in cap.items()}
        n4 = intersect(cap[5], rot(lo_dir, da), P[13], P[14])
        n12 = intersect(cap[11], rot(hi_dir, da), P[13], P[14])
        return cap, n4, n12, da

    a, b = 0.0, 1.0  # lower edge's arm fraction rises with c
    for _ in range(60):
        c = (a + b) / 2
        _, n4, _, _ = build(c)
        a, b = (c, b) if along(n4) < GAP_FRAC else (a, c)
    cap, n4, n12, da = build(c)
    if abs(math.degrees(da)) > MAX_TURN:
        # swing capped: of the leg positions along the arm that swing no
        # more than MAX_TURN (the swing isn't monotonic along the arm),
        # take the one whose gap comes closest to GAP_FRAC
        best = None
        for k in range(1, 1000):
            ck = k / 1000
            cap_k, n4_k, n12_k, da_k = build(ck)
            if abs(math.degrees(da_k)) > MAX_TURN or not 0 < along(n4_k) < along(n12_k) < 1:
                continue
            score = abs(along(n4_k) - GAP_FRAC)
            if best is None or score < best[0]:
                best = (score, ck)
        assert best, (mname, "no leg position within MAX_TURN")
        c = best[1]
        cap, n4, n12, da = build(c)
    n13 = ((n12[0] + P[14][0]) / 2, (n12[1] + P[14][1]) / 2)
    tA, tB = along(n4), along(n12)
    assert 0 < tA < tB < along(n13) < 1, (mname, tA, tB)
    gap = math.hypot(n4[0] - S[0], n4[1] - S[1])
    print(f"{mname:20s} leg on arm {tA:.2f}-{tB:.2f}  gap {gap:5.1f}"
          f"  leg turns {math.degrees(da):+5.1f} deg  foot {P[8][0]:g} -> {cap[8][0]:.0f}"
          f"  width {layer.width:g}")
    if DRY:
        return {}
    new = {3: S, 4: n4, 12: n12, 13: n13, **cap}
    return {"nodes": {i: re_(p) for i, p in new.items()}}


if __name__ == "__main__":
    for glyph in ("K", "k", "kgreenlandic"):
        print(f"--- {glyph}")
        changed = apply_edit(GLYPHS_FILE, glyph, edit)
        assert DRY or changed
    print("dry run" if DRY else "done")
