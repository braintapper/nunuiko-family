"""Code edit 8: ©, ® and @ keep their shape, centred on the capitals.

All three are wider than the cell, so the monospace step condensed them
horizontally alone: © and ® into tall ovals, the @ (which edit 6 used to
squash onto the O's height instead) into a narrow one. Instead they are
scaled down uniformly here until they fit the cell (WIDTH, the cell less
SB_MIN each side), so the monospace step only moves them, and centred
vertically on half the cap height, between the baseline and the cap
height. If one were still taller than the O after that, it would be
scaled down further to the O's height. Stroke weight is kept as on the $
(edit 6, scale_kept). Nunuiko's @ hangs below the baseline; this lifts it
onto the capitals.
"""
import importlib.util
import os

from fontTools.pens.recordingPen import DecomposingRecordingPen

WIDTH = 538   # the cell less 30 each side, with 2 units to spare for rounding

_spec = importlib.util.spec_from_file_location(
    "edit06", os.path.join(os.path.dirname(__file__), "06_at_percent_dollar.py"))
_e6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_e6)


def flatten(ufo, g):
    if not g.components:
        return
    rec = DecomposingRecordingPen(ufo)
    g.draw(rec)
    g.clearContours()
    g.clearComponents()
    rec.replay(g.getPen())


def round_and_centre(ufo, g, stem, tan):
    flatten(ufo, g)
    x0, y0, x1, y1 = _e6.bounds(g, tan)
    lo, hi = _e6.o_bounds(ufo)
    s = min(1.0, (WIDTH - stem) / (x1 - x0 - stem),  # the offset adds (1-s)stem
            (hi - lo - stem) / (y1 - y0 - stem))
    h = s * (y1 - y0 - stem) + stem
    lo = ufo.info.capHeight / 2 - h / 2
    cx = (x0 + x1) / 2
    _e6.scale_kept(g, s, s, cx, y0, cx, lo + (1 - s) * stem / 2, stem, tan)
    return s, lo, lo + h


def apply(ufo, stem, tan):
    for name in ufo.keys():
        assert not any(c.baseGlyph in ("copyright", "registered", "at")
                       for c in ufo[name].components), name
    out = []
    for name in ("copyright", "registered", "at"):
        s, lo, hi = round_and_centre(ufo, ufo[name], stem, tan)
        out.append(f"{name} {s:.2f} ({lo:.0f}..{hi:.0f})")
    print("  " + "; ".join(out))
