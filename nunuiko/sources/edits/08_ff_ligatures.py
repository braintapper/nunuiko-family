"""Glyph edit 8: ff / ffi / ffl ligatures with a joined crossbar.

Stock Nunito has no ff ligature: "ff" is two f's pulled together by the
f-f kern (-10 / -23 / -35). Each crossbar ends in a round cap, so the
bars meet as two rounded ends (a gap at ExtraLight, a pinched waist from
Regular up). The ligatures join them into one flat bar.

Rule, per master:
  offset = width(f) + kern(@MMK_L_f, @MMK_R_f)   (where the kerned 2nd f sits)
  glyph  = component f at 0 + component <second> at offset + a bridge
  bridge = quad from the first f's flat-bar right ends (nodes 4 bottom,
           10 top) to the second f's flat-bar left ends (nodes 33 bottom,
           27 top, + offset). Both round caps lie inside it, so the union
           is one flat bar. Works on the italic masters unchanged: the
           bar is horizontal there too, the quad simply follows the
           slanted cap starts.
  width  = offset + width(<second>)

Glyphs (second component): f_f (f), f_f_i (fi), f_f_l (fl),
f_f_l.ss02 (fl.ss02). fi is drawn rather than built from f, so its bar
ends are asserted to match f's. Carets: caret_1 at offset, caret_2 at
offset + the second glyph's caret_1. Kerning groups: left f, right taken
from the second glyph. liga/ss02 feature code gets the matching subs.

Text-surgery on the .glyphs file (see lib.py). Run once from sources/:
python3 edits/08_ff_ligatures.py
"""
import sys

from glyphsLib import GSFont

GLYPHS_FILE = "Nunuiko.glyphs"
# name -> (second component, unicode or None)
LIGATURES = {
    "f_f": ("f", "FB00"),
    "f_f_i": ("fi", "FB03"),
    "f_f_l": ("fl", "FB04"),
    "f_f_l.ss02": ("fl.ss02", None),
}
INSERT_BEFORE = "{\ncolor = 6;\nglyphname = ordfeminine;\n"
BAR_BOTTOM_RIGHT, BAR_TOP_RIGHT = 4, 10  # first f: flat bar ends
BAR_TOP_LEFT, BAR_BOTTOM_LEFT = 27, 33  # second f: flat bar ends

LIGA_OLD = "code = \"lookupflag IgnoreMarks;\nsub f i by fi;\nsub f l by fl;\n\";\nname = liga;"
LIGA_NEW = ("code = \"lookupflag IgnoreMarks;\nsub f f i by f_f_i;\n"
            "sub f f l by f_f_l;\nsub f f by f_f;\nsub f i by fi;\n"
            "sub f l by fl;\n\";\nname = liga;")
SS02_OLD = "sub fl by fl.ss02;\n\";\nname = ss02;"
SS02_NEW = "sub fl by fl.ss02;\nsub f_f_l by f_f_l.ss02;\n\";\nname = ss02;"


def num(v):
    return f"{v:g}"


def layer_text(master_id, offset, second, width, bridge, carets):
    anchors = ",\n".join(
        f"{{\nname = caret_{i};\nposition = \"{{{num(x)}, 0}}\";\n}}"
        for i, x in enumerate(carets, 1)
    )
    nodes = ",\n".join(f'"{x} {y} LINE"' for x, y in bridge)
    comps = (f"{{\nname = f;\n}},\n{{\nname = {second};\n"
             f"transform = \"{{1, 0, 0, 1, {offset}, 0}}\";\n}}")
    return (f"{{\nanchors = (\n{anchors}\n);\ncomponents = (\n{comps}\n);\n"
            f"layerId = \"{master_id}\";\npaths = (\n{{\nclosed = 1;\n"
            f"nodes = (\n{nodes}\n);\n}}\n);\nwidth = {width};\n}}")


def main():
    text = open(GLYPHS_FILE).read()
    font = GSFont(GLYPHS_FILE)
    for name in LIGATURES:
        if font.glyphs[name] is not None:
            sys.exit(f"{name} already exists — already applied?")
    masters = [m.id for m in font.masters]
    mnames = {m.id: m.name for m in font.masters}

    def master_layer(glyph, mid):
        return next(l for l in font.glyphs[glyph].layers if l.layerId == mid)

    blocks = []
    for name, (second, uni) in LIGATURES.items():
        layers = []
        for mid in masters:
            f = master_layer("f", mid)
            n = f.paths[0].nodes
            assert len(n) == 39, (mnames[mid], len(n))
            pos = lambda i: (n[i].position.x, n[i].position.y)
            br, tr = pos(BAR_BOTTOM_RIGHT), pos(BAR_TOP_RIGHT)
            tl, bl = pos(BAR_TOP_LEFT), pos(BAR_BOTTOM_LEFT)
            assert br[1] == bl[1] and tr[1] == tl[1], mnames[mid]
            kern = font.kerning[mid]["@MMK_L_f"]["@MMK_R_f"]
            offset = int(f.width + kern)
            if second == "fi":  # drawn, not a component of f: check its bar
                fi = {(q.position.x, q.position.y)
                      for q in master_layer("fi", mid).paths[0].nodes}
                assert tl in fi and bl in fi, (mnames[mid], "fi bar differs")
            bridge = [br, (bl[0] + offset, bl[1]),
                      (tl[0] + offset, tl[1]), tr]
            assert br[0] < bridge[1][0] and tr[0] < bridge[2][0], mnames[mid]
            sec = master_layer(second, mid)
            carets = [offset] + [offset + a.position.x for a in sec.anchors
                                 if a.name == "caret_1"]
            width = int(offset + sec.width)
            layers.append(layer_text(mid, offset, second, width, bridge, carets))
            print(f"{name:11s} {mnames[mid]:18s} offset {offset} width {width}"
                  f" bridge x {br[0]:g}->{bl[0] + offset:g}")
        right = font.glyphs[second].rightKerningGroup
        block = (f"{{\nglyphname = {name};\nlayers = (\n" + ",\n".join(layers)
                 + f"\n);\nleftKerningGroup = f;\nrightKerningGroup = {right};\n"
                 + (f"unicode = {uni};\n" if uni else "") + "},\n")
        blocks.append(block)

    assert text.count(INSERT_BEFORE) == 1
    text = text.replace(INSERT_BEFORE, "".join(blocks) + INSERT_BEFORE)
    for old, new in ((LIGA_OLD, LIGA_NEW), (SS02_OLD, SS02_NEW)):
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    open(GLYPHS_FILE, "w").write(text)
    print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
