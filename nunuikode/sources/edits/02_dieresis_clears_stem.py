"""Code edit 2: the dieresis on a single stem (ï Ï ї Ї ḯ Ḯ) clears the stem.

Nunuiko uses its ordinary dieresis on these. The dots sit closer as the
weight rises: the gap between them is 94 at ExtraLight but only 66 at
Bold, narrower than the 125 stem, so the dots sit over the stem's edges.
In proportional text the neighbours hide it; alone in a monospace cell
it reads as a misplaced accent.

Rule, per master (unslanted): each dot moves outward until its inner edge
is CLEAR from the stem edge,
  CLEAR = CLEAR_STEM x stem + CLEAR_MIN   (ExtraLight 26, Bold 51, Heavy 76)
but no further than leaves EDGE between the outer dot edges and the cell
(Heavy can't fit the full clearance). Dots already clear enough don't
move. The mark component is decomposed into the glyph first; contours
centred over the stem (the acute of ḯ) stay put.
"""
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen

CLEAR_STEM = 0.3
CLEAR_MIN = 13
EDGE = 15          # min space between a dot and the 600 cell edge
CELL = 600
GLYPHS = ("idieresis", "idieresisacute", "Idieresis", "Idieresisacute",
          "yi-cy", "Yi-cy")


def apply(ufo, stem, tan):
    clear = CLEAR_STEM * stem + CLEAR_MIN
    for name in GLYPHS:
        if name not in ufo:
            continue
        g = ufo[name]
        base, marks = g.components[0], g.components[1:]
        assert not len(g) and marks, name
        bx = [p.x - p.y * tan for c in ufo[base.baseGlyph] for p in c]
        s0 = min(bx) + base.transformation[4]
        s1 = max(bx) + base.transformation[4]
        mid = (s0 + s1) / 2
        rec = DecomposingRecordingPen(ufo)
        for m in marks:
            m.draw(rec)
        # split the recording into contours, tagged left / right / centre
        groups, cur = [], []
        for op, args in rec.value:
            cur.append((op, args))
            if op in ("closePath", "endPath"):
                groups.append(cur)
                cur = []

        def ux(grp):
            return [x - y * tan for _, a in grp for x, y in a]

        left = [k for k, grp in enumerate(groups) if max(ux(grp)) < mid]
        right = [k for k, grp in enumerate(groups) if min(ux(grp)) > mid]
        assert left and right, name
        lin = max(max(ux(groups[k])) for k in left)
        rin = min(min(ux(groups[k])) for k in right)
        dot_w = max(max(ux(groups[k])) - min(ux(groups[k])) for k in left + right)
        room = (CELL - 2 * EDGE - (s1 - s0) - 2 * dot_w) / 2  # max clearance
        want = min(clear, room)
        # the glyph is still at its proportional width; monospace centres
        # it later, so the cell limit is applied to the clearance, not x
        dl = max(0.0, want - (s0 - lin))
        dr = max(0.0, want - (rin - s1))
        for m in marks:
            g.removeComponent(m)
        pen = g.getPen()
        for k, grp in enumerate(groups):
            dx = -dl if k in left else dr if k in right else 0.0
            out = TransformPen(pen, (1, 0, 0, 1, dx, 0))
            for op, args in grp:
                getattr(out, op)(*args)
        print(f"  {name:15s} clearance {s0 - lin:5.1f}/{rin - s1:5.1f} -> {want:5.1f}")
