"""Glyph edit 19: $ is a full-size S with one stroke right through it
(shared by Nunuiko and Display; supersedes edit 16).

Stock Nunito / Nunito Sans draw the $ as one outline: a smaller S with
two stubs of the bar sticking out above and below it. Edit 16 shrank all
of it to the S's height. Now the $ is:
  - the S itself, as a component (so later S changes reach the $), at full
    size, with the S's advance;
  - one straight vertical stroke through it, as its own contour,
    overlapping the S: as thick as the stock bar, reaching as far above and
    below as the stock bar did (Nunito -121..826 at ExtraLight; Nunito Sans
    -115..820), centred across on the S's outline. Its ends are round in
    Nunuiko (half-circles, like the stock stub ends) and flat in Display.
    In the italic it follows the slant.

The bar's thickness and reach are read per master from the stock $ in git
history (STOCK below): the on-curve nodes above the S's top give the
stub's left and right edges. The stroke runs in the same direction as the
S's outer contour so the overlap fills.

Run once per source from sources/:
  python3 edits/19_dollar_full_s.py [file.glyphs]
"""
import glob
import math
import os
import re
import subprocess
import sys
import tempfile

from glyphsLib import GSFont

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("*.glyphs"))[0]
KAPPA = 0.5522847498
STOCK = {  # source -> (commit, stock file in the repo)
    "Nunuiko.glyphs": ("7539f1e9", "nunuiko/sources/Nunito.glyphs"),
    "NunuikoDisplay.glyphs": ("0bac6f5d", "nunuiko-display/sources/NunitoSans.glyphs"),
    "NunuikoDisplay-Italic.glyphs": ("0bac6f5d", "nunuiko-display/sources/NunitoSans-Italic.glyphs"),
}
ROUND = os.path.basename(GLYPHS_FILE) == "Nunuiko.glyphs"


def stock_font():
    commit, path = STOCK[os.path.basename(GLYPHS_FILE)]
    data = subprocess.run(["git", "show", f"{commit}:{path}"], check=True,
                          capture_output=True).stdout
    with tempfile.NamedTemporaryFile(suffix=".glyphs", delete=False) as t:
        t.write(data)
    try:
        return GSFont(t.name)
    finally:
        os.unlink(t.name)


def bar_nodes(cx, hw, bot, top, tan, ccw):
    """(x, y, type, smooth) for the stroke, unslanted cx, slanted out."""
    R, L = cx + hw, cx - hw
    if ROUND:
        k = hw * KAPPA
        pts = [(R, top - hw, "line", True),
               (R, top - hw + k, "offcurve", False), (cx + k, top, "offcurve", False),
               (cx, top, "curve", True),
               (cx - k, top, "offcurve", False), (L, top - hw + k, "offcurve", False),
               (L, top - hw, "curve", True),
               (L, bot + hw, "line", True),
               (L, bot + hw - k, "offcurve", False), (cx - k, bot, "offcurve", False),
               (cx, bot, "curve", True),
               (cx + k, bot, "offcurve", False), (R, bot + hw - k, "offcurve", False),
               (R, bot + hw, "curve", True)]
    else:
        pts = [(R, bot, "line", False), (R, top, "line", False),
               (L, top, "line", False), (L, bot, "line", False)]
    if not ccw:
        # reverse, keeping each curve's handles before its on-curve node
        on = [i for i, p in enumerate(pts) if p[2] != "offcurve"]
        segs = []
        for j, i in enumerate(on):
            prev = on[j - 1]
            segs.append((pts[prev], pts[prev + 1:i] if i > prev else pts[prev + 1:] + pts[:i], pts[i]))
        out = []
        for start, handles, end in reversed(segs):
            kind = end[2]
            out += list(reversed(handles))
            out.append((start[0], start[1], kind, start[3]))
        pts = out
    return [(x + y * tan, y, t, sm) for x, y, t, sm in pts]


def signed_area(path):
    # over the control polygon (handles included): close enough to the
    # outline's own area for its sign, where on-curve points alone can miss
    P = [(n.position.x, n.position.y) for n in path.nodes]
    return sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1]
               for i in range(len(P)))


def fmt(x, y, t, sm, g3):
    x, y = round(x), round(y)
    if g3:
        code = {"offcurve": "o", "curve": "c", "line": "l"}[t] + ("s" if sm and t != "offcurve" else "")
        return f"({x},{y},{code})"
    return f'"{x} {y} {t.upper()}{" SMOOTH" if sm and t != "offcurve" else ""}"'


def main():
    text = open(GLYPHS_FILE).read()
    g3 = ".formatVersion = 3;" in text
    font, stock = GSFont(GLYPHS_FILE), stock_font()
    smasters = {m.id for m in stock.masters}
    for g in font.glyphs:
        for l in g.layers:
            assert not any(c.name == "dollar" for c in l.components), g.name

    bs = text.index("glyphname = dollar;")
    be = text.index("\nglyphname = ", bs + 1)
    block = text[bs:be]
    for m in font.masters:
        assert m.id in smasters, m.name
        tan = math.tan(math.radians(m.italicAngle))
        S = font.glyphs["S"].layers[m.id]
        un = [(n.position.x - n.position.y * tan, n.position.y)
              for p in S.paths for n in p.nodes if n.type != "offcurve"]
        s_lo, s_hi = min(y for _, y in un), max(y for _, y in un)
        cx = (min(u for u, _ in un) + max(u for u, _ in un)) / 2
        ccw = signed_area(max(S.paths, key=lambda p: abs(signed_area(p)))) > 0
        st = [(n.position.x - n.position.y * tan, n.position.y)
              for p in stock.glyphs["dollar"].layers[m.id].paths for n in p.nodes]
        stub = [u for (u, y), n in zip(st, [n for p in stock.glyphs["dollar"].layers[m.id].paths
                                            for n in p.nodes])
                if y > s_hi + 20 and n.type != "offcurve"]
        hw = (max(stub) - min(stub)) / 2
        bot, top = min(y for _, y in st), max(y for _, y in st)
        nodes = bar_nodes(cx, hw, bot, top, tan, ccw)
        print(f"  {m.name:32s} S {S.width:g} wide; stroke {2 * hw:.0f} thick, {bot:.0f}..{top:.0f}, centre {cx:.0f}")

        ls = block.index(f'layerId = "{m.id}";')
        le = re.compile(r"\nwidth = [^;]*;").search(block, ls)
        node_text = ",\n".join(fmt(*n, g3) for n in nodes)
        path = "{\nclosed = 1;\nnodes = (\n" + node_text + "\n);\n}"
        if g3:
            region = block[ls:le.end()]
            new = (f'layerId = "{m.id}";\nshapes = (\n{{\nref = S;\n}},\n{path}\n);\n'
                   f"width = {S.width:g};")
            block = block[:ls] + new + block[le.end():]
        else:
            # Glyphs 2: components come before layerId, paths after it
            region = block[ls:le.end()]
            new = (f'layerId = "{m.id}";\npaths = (\n{path}\n);\nwidth = {S.width:g};')
            block = block[:ls] + "components = (\n{\nname = S;\n}\n);\n" + new + block[le.end():]
    text = text[:bs] + block + text[be:]
    open(GLYPHS_FILE, "w").write(text)
    print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
