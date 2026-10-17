"""Glyph edit 21: ¢ with one stroke right through it (shared by Nunuiko
and Display), like the $ (edit 19).

Stock Nunito / Nunito Sans draw the ¢ as one outline: a c with two stubs
of the bar sticking out above and below it. A straight stroke is added as
its own contour, overlapping the c: exactly the stubs' thickness and
reach, so the outline looks the same outside the c and the stroke now runs
on through the c's counter between them. Round ends in Nunuiko, flat in
Display (bar_nodes from edit 19). Follows the slant in the italic; runs in
the same direction as the outer contour so the overlap fills. The c and
the advance are unchanged.

The stubs are the on-curve nodes above the x-height + 30; the reach is the
glyph's full height.

Run once per source from sources/:
  python3 edits/21_cent_full_stroke.py [file.glyphs]
"""
import glob
import importlib.util
import math
import os
import re
import sys

from glyphsLib import GSFont

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("*.glyphs"))[0]
_spec = importlib.util.spec_from_file_location(
    "edit19", os.path.join(os.path.dirname(__file__), "19_dollar_full_s.py"))
e19 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e19)


def main():
    text = open(GLYPHS_FILE).read()
    g3 = ".formatVersion = 3;" in text
    font = GSFont(GLYPHS_FILE)
    bs = text.index("glyphname = cent;")
    be = text.index("\nglyphname = ", bs + 1)
    block = text[bs:be]
    for m in font.masters:
        tan = math.tan(math.radians(m.italicAngle))
        lay = font.glyphs["cent"].layers[m.id]
        assert len(lay.paths) == 1 and not lay.components, m.name
        nodes = lay.paths[0].nodes
        un = [(n.position.x - n.position.y * tan, n.position.y, n.type) for n in nodes]
        stub = [u for u, y, t in un if t != "offcurve" and y > m.xHeight + 30]
        assert len(stub) >= 2, m.name
        hw = (max(stub) - min(stub)) / 2
        cx = (max(stub) + min(stub)) / 2
        bot, top = min(y for _, y, _ in un), max(y for _, y, _ in un)
        ccw = e19.signed_area(lay.paths[0]) > 0
        bar = e19.bar_nodes(cx, hw, bot, top, tan, ccw)
        print(f"  {m.name:32s} stroke {2 * hw:.0f} thick at {cx:.0f}, {bot:.0f}..{top:.0f}")
        ls = block.index(f'layerId = "{m.id}";')
        we = re.compile(r"\nwidth = [^;]*;").search(block, ls).start()
        end = block.rindex("\n);", ls, we)
        path = ",\n{\nclosed = 1;\nnodes = (\n" + ",\n".join(e19.fmt(*n, g3) for n in bar) + "\n);\n}"
        block = block[:end] + path + block[end:]
    text = text[:bs] + block + text[be:]
    open(GLYPHS_FILE, "w").write(text)
    print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
