"""Code edit 5: the capital W's middle peak sits lower.

Nunuiko's W has its middle peak at the full cap height, level with the
outer stems. Condensed into the 600 cell, the four strokes then crowd
together at the top. The middle peak (its round top and the notch under
it) moves straight down by DROP x the cap height, so the inner strokes
end short of the outer ones. Ŵ Ẁ Ẃ Ẅ and the healing alternates follow.

Rule, per master (unslanted): the points in the upper half of the glyph
within MID x its width of its centre move down; the outer stems' tops are
outside that band and stay put.
"""
DROP = 0.3  # x cap height
MID = 0.2    # x glyph width, each side of the centre


def apply(ufo, stem, tan):
    g = ufo["W"]
    assert len(g) == 1 and not g.components
    ux = lambda p: p.x - p.y * tan
    us = [ux(p) for p in g[0]]
    c, w = (min(us) + max(us)) / 2, max(us) - min(us)
    cap = ufo.info.capHeight
    dy = DROP * cap
    pts = [p for p in g[0] if p.y > cap / 2 and abs(ux(p) - c) < MID * w]
    assert len(pts) == 9, len(pts)
    for p in pts:
        p.x -= dy * tan
        p.y -= dy
    print(f"  W middle peak lowered {dy:.0f}")
