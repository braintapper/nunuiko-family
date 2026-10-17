"""Code edit 4: brackets and bars centred on the capitals.

Nunuiko's ( ) [ ] { } | ¦ hang from the cap height: their tops sit at or
just above it and their bottoms 180-220 below the baseline, the usual
choice for prose. Code fonts centre them on the capitals instead, so a
bracket reaches as far above the cap height as below the baseline and
(x), [0], {} sit level with the letters (Cascadia: -98..791 on a 693 cap).

Rule, per master: each glyph moves up until the middle of its height is
at half the cap height (worked along the slant on the italics). The
angle brackets ⟨ ⟩ are already centred and stay put.
"""
GLYPHS = ("parenleft", "parenright", "bracketleft", "bracketright",
          "braceleft", "braceright", "bar", "brokenbar")


def apply(ufo, stem, tan):
    half = ufo.info.capHeight / 2
    for name in GLYPHS:
        g = ufo[name]
        assert not g.components, name
        ys = [p.y for c in g for p in c]
        dy = half - (min(ys) + max(ys)) / 2
        g.move((dy * tan, dy))
    print(f"  brackets raised to centre on {half:g}")
