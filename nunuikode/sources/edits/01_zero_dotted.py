"""Code edit 1: dotted zero, so 0 can't be read as O.

In a monospaced font O is condensed to the same cell as 0, so the two
ovals end up close in shape. A dot in the counter disambiguates them;
a dot (rather than a slash) suits Nunito's rounded style and can't be
mistaken for Ø.

Rule, per master: an upright oval centred in the zero's counter (the
second contour), drawn unslanted and slanted with the italic.
  width  = min(DOT_STEM x stem, DOT_MAX_W x counter width)
  height = min(DOT_ASPECT x width, DOT_MAX_H x counter height)
Applied to zero, zero.tosf and zero.dnom; zero.numr, zerosuperior and
zeroinferior are composites of zero.dnom and follow.
"""
KAPPA = 0.5522847498
DOT_STEM = 1.6     # dot width relative to the stem weight
DOT_MAX_W = 0.40   # ... but at most this share of the counter width
DOT_ASPECT = 1.35  # height / width (upright oval like the zero)
DOT_MAX_H = 0.35   # ... at most this share of the counter height
GLYPHS = ("zero", "zero.tosf", "zero.dnom")


def apply(ufo, stem, tan):
    for name in GLYPHS:
        g = ufo[name]
        assert len(g) == 2, (name, len(g))  # outer oval + counter
        counter = g[1]
        xs = [p.x - p.y * tan for p in counter]
        ys = [p.y for p in counter]
        cw, ch = max(xs) - min(xs), max(ys) - min(ys)
        cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
        w = min(DOT_STEM * stem, DOT_MAX_W * cw)
        h = min(DOT_ASPECT * w, DOT_MAX_H * ch)
        rx, ry = w / 2, h / 2
        kx, ky = rx * KAPPA, ry * KAPPA
        sl = lambda x, y: (round(x + y * tan), round(y))
        pen = g.getPen()
        # counter-clockwise (ink), starting at the bottom
        pen.moveTo(sl(cx, cy - ry))
        pen.curveTo(sl(cx + kx, cy - ry), sl(cx + rx, cy - ky), sl(cx + rx, cy))
        pen.curveTo(sl(cx + rx, cy + ky), sl(cx + kx, cy + ry), sl(cx, cy + ry))
        pen.curveTo(sl(cx - kx, cy + ry), sl(cx - rx, cy + ky), sl(cx - rx, cy))
        pen.curveTo(sl(cx - rx, cy - ky), sl(cx - kx, cy - ry), sl(cx, cy - ry))
        pen.closePath()
