"""Code edit 11: a longer tail on the t.

The t's tail (every point right of the stem's right edge, below the
crossbar) reaches TAIL (1.3) x as far right of the stem as it did, the
same factor as its crossbar (edit 7). The round end moves out rigidly,
so it keeps its shape: points past the tail's lowest point move by the
full amount, points between the stem and that point are stretched away
from the stem in proportion, so the curve from the stem keeps its shape.
If the t would then be wider than the cell allows, the tail is cut back.
Accented t's (ţ ť ț ŧ) follow. Worked unslanted.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "edit07", os.path.join(os.path.dirname(__file__), "07_t_and_f.py"))
e07 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e07)

CELL = 600
SB_MIN = 30
TAIL = 1.3


def apply(ufo, stem, tan):
    g = ufo["t"]
    assert len(g) == 1, g.name
    pts = list(g[0])
    ux = lambda p: p.x - p.y * tan
    left = min(ux(q) for q in pts)
    bar = min(p.y for p in pts if ux(p) < left + 40)  # the crossbar's underside, at its left end
    # the stem's right edge, just under the crossbar
    xr = e07.stem_edges(pts, tan, bar - 30)[1]
    tail = [p for p in pts if p.y < bar - 1 and ux(p) > xr + 0.5]
    b = min((p for p in tail if p.segmentType), key=lambda p: p.y)
    xb = ux(b)
    reach = max(ux(p) for p in tail) - xr
    dx = (TAIL - 1) * reach
    others = [ux(p) for p in pts if p not in tail]
    room = CELL - 2 * SB_MIN
    dx = max(0, min(dx, min(others) + room - (xr + reach)))
    s = (xb + dx - xr) / (xb - xr)
    for p in tail:
        u = ux(p)
        u = u + dx if u >= xb else xr + (u - xr) * s
        p.x = u + p.y * tan
    print(f"  t tail reach {reach:.0f} -> {reach + dx:.0f}")
