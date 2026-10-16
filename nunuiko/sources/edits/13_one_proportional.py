"""Glyph edit 13: proportional 1 by default, footed tabular 1 under tnum.

Port of Nunuïko Display's edit 13. Every figure is tabular (600); the
footless 1 (edit 12) leaves too much space around it in typed numbers.

  one, one.tosf   outline shifted, advance narrowed (unslanted):
                    RSB = I's sidebearing (straight stem, same master)
                    LSB = LSB_FRAC x that (the flag leaves open space)
  one.tf,         NEW: component of the STOCK footed 1 (one.ss01 /
  one.tosf.tf     one.tosf.ss01 since edit 12's swap), 600 wide: the
                  foot gives the tabular 1 better optical balance
  tnum            NEW feature right after onum: one -> one.tf,
                  one.tosf -> one.tosf.tf
  ss01            + one.tf -> one.ss01, one.tosf.tf -> one.tosf.ss01

Fraction / super / subscript figures stay tabular. Only master layers
are written. Run once, after edit 12:  python3 edits/13_one_proportional.py
"""
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
LSB_FRAC = 0.75
PAIRS = (("one", "one.tf"), ("one.tosf", "one.tosf.tf"))
TABULAR = {"one.tf": "one.ss01", "one.tosf.tf": "one.tosf.ss01"}  # footed
ONUM_END = "sub nine by nine.tosf;\n\";\nname = onum;\n},\n"
TNUM = ("{\ncode = \"sub one by one.tf;\nsub one.tosf by one.tosf.tf;\n\";\n"
        "name = tnum;\n},\n")
SS01_OLD = "sub one.tosf by one.tosf.ss01;\n\";\nname = ss01;"
SS01_NEW = ("sub one.tosf by one.tosf.ss01;\nsub one.tf by one.ss01;\n"
            "sub one.tosf.tf by one.tosf.ss01;\n\";\nname = ss01;")

font = GSFont(GLYPHS_FILE)
masters = {m.name: m for m in font.masters}
for _, tf in PAIRS:
    if font.glyphs[tf] is not None:
        sys.exit(f"{tf} already exists — already applied?")


def unslanted_x(layer, tan):
    return [n.position.x - n.position.y * tan for n in layer.paths[0].nodes]


def proportional(mname, layer, nodes):
    m = masters[mname]
    tan = math.tan(math.radians(m.italicAngle))
    ux = unslanted_x(layer, tan)
    i_lay = font.glyphs["I"].layers[m.id]
    ix = unslanted_x(i_lay, tan)
    sb = (min(ix) + (i_lay.width - max(ix))) / 2
    lsb, rsb = LSB_FRAC * sb, sb
    shift = lsb - min(ux)
    width = round(lsb + (max(ux) - min(ux)) + rsb)
    print(f"{mname:20s} {layer.parent.name:9s} sidebearings {lsb:.0f}/{rsb:.0f}"
          f"  width {layer.width:g} -> {width}")
    return {"nodes": {i: (n.position.x + shift, n.position.y)
                      for i, n in enumerate(nodes)},
            "width": width}


def tabular_block(tf):
    """Glyphs 2 glyph block: one component of the footed 1, 600 wide."""
    layers = []
    for m in font.masters:
        w = font.glyphs[TABULAR[tf]].layers[m.id].width
        layers.append(f"{{\ncomponents = (\n{{\nname = {TABULAR[tf]};\n}}\n);\n"
                      f"layerId = \"{m.id}\";\nwidth = {w:g};\n}}")
    return f"{{\nglyphname = {tf};\nlayers = (\n" + ",\n".join(layers) + "\n);\n},\n"


if __name__ == "__main__":
    for base, _ in PAIRS:
        assert apply_edit(GLYPHS_FILE, base, proportional)
    blocks = "".join(tabular_block(tf) for _, tf in PAIRS)
    text = open(GLYPHS_FILE).read()
    # insert the new glyphs right before one.dnom's block
    s = text.index("glyphname = one.dnom;")
    s = text.rindex("\n{\n", 0, s) + 1
    text = text[:s] + blocks + text[s:]
    for old, new in ((ONUM_END, ONUM_END + TNUM), (SS01_OLD, SS01_NEW)):
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    open(GLYPHS_FILE, "w").write(text)
    print("written", GLYPHS_FILE)
