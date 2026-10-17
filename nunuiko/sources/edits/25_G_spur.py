"""Glyph edit 25: the G gets a straight drop under the bar; edit 18's round
G becomes the alternate G.ss03 (shared by Nunuiko and Display).
Reference: Bryant (user screenshot, 2026-10-17): before the bar turns
left, the right side drops straight down about half the way to the
baseline.

Both were drawn and compared side by side; the user picked this one as the
default and kept the round one (edit 18) as the alternate, as with the l.

The round G as edit 18 leaves it is first copied to G.ss03 (no Unicode),
with copies of the composites built on G (Gbreve.ss03 ...) pointing at it,
and a new stylistic set ss03 ("Alternate G") that swaps them in. Kerning
groups come with the copies. Then G itself is reshaped: starting from edit
18's G (as wide as the O, the upstroke evened out), only where the bottom
curve turns up changes: the right side is now straight from the bar down
to J = DROP (0.5) of the bar's top height, outside and inside, and the
bottom curves join it there, vertical, with the O's tensions. The stroke
keeps the side thickness edit 18 gave it.

Operation, per master, unslanted (x - y tan) in the italic:
  Outer: the two handles after the outer bottom point B and the node they
    lead to are replaced by handles to a new curve node E at (xo, J),
    vertical there; the stem then runs straight up to L (the bar's corner).
    Nunuiko (edit 18's "cut": L ends the curve) gains E and L becomes a
    line node; Display ("vertical": E is already there) moves E.
  Inner: a line node Ei at (xi, J) is inserted after the bar's underside U,
    and the curve from it to the inner bottom point IB gets new handles.
  xo, xi: the outer and inner x of the side at the bar, as edit 18 left them.

Run once per source from sources/, after edit 18:
  python3 edits/25_G_spur.py [file.glyphs]
"""
import glob
import importlib.util
import math
import os
import re
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("*.glyphs"))[0]
DROP = 0.5   # the straight side ends this share of the way from the bar's top to the baseline
ALT = ".ss03"
_spec = importlib.util.spec_from_file_location(
    "edit18", os.path.join(os.path.dirname(__file__), "18_G_rounder_bottom.py"))
e18 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e18)


def glyph_span(text, name):
    """From the glyph's opening brace to the next glyph's (keys such as
    color = ...; can come before glyphname)."""
    for marker in (f"\nglyphname = {name};\n", f'\nglyphname = "{name}";\n'):
        if marker in text:
            k = text.index(marker)
            s = text.rindex("\n{\n", 0, k + 1) + 1
            nxt = text.index("\nglyphname = ", k + 1)
            e = text.rindex("\n{\n", 0, nxt + 1) + 1
            return s, e
    raise KeyError(name)


def copy_glyphs(text, g3, font):
    """Add G.ss03 and the composites built on G, as copies."""
    names = ["G"] + [g.name for g in font.glyphs
                     if g.name != "G" and g.layers[font.masters[0].id].components
                     and g.layers[font.masters[0].id].components[0].name == "G"
                     and not g.layers[font.masters[0].id].paths and "." not in g.name]
    ref = "ref = G;" if g3 else "name = G;"
    for name in names:
        assert f"glyphname = {name}{ALT};" not in text, f"{name}{ALT} exists already"
        s, e = glyph_span(text, name)
        block = text[s:e]
        block = block.replace(f"glyphname = {name};", f"glyphname = {name}{ALT};", 1)
        block = re.sub(r"\nunicode = [^;]*;", "", block)
        block = block.replace(f"\n{ref}\n", f"\n{ref[:-1]}{ALT};\n")
        text = text[:e] + block + text[e:]
    return text, names


def add_feature(text, g3, names):
    code = "\n".join(f"sub {n} by {n}{ALT};" for n in names)
    if g3:
        feat = (f'{{\ncode = "{code}\n";\nlabels = (\n{{\nlanguage = dflt;\n'
                f'value = "Alternate G";\n}}\n);\ntag = ss03;\n}},\n')
        anchor = "tag = ss02;\n},\n"
    else:
        feat = f'{{\ncode = "{code}\n";\nname = ss03;\n}},\n'
        anchor = "name = ss02;\n},\n"
    assert text.count(anchor) == 1 and "ss03;" not in text.split("features = (")[1][:200000]
    i = text.index(anchor) + len(anchor)
    return text[:i] + feat + text[i:]


def plan(nodes, tan, o_layer):
    m = len(nodes)
    P = [(n.position.x - n.position.y * tan, n.position.y) for n in nodes]
    T = [n.type for n in nodes]
    nx = lambda i: (i + 1) % m
    b = min((i for i in range(m) if T[i] != "offcurve"), key=lambda i: P[i][1])
    h1, h2, x = nx(b), nx(nx(b)), nx(nx(nx(b)))
    assert T[h1] == T[h2] == "offcurve" and T[x] == "curve", "outer"
    display = T[nx(x)] == "line"
    li = nx(x) if display else x
    # inner: U (line) -> 2 handles -> IB (curve), U the rightmost such line node
    u = max((i for i in range(m) if T[i] == "line" and T[nx(i)] == T[nx(nx(i))] == "offcurve"
             and T[nx(nx(nx(i)))] == "curve" and P[nx(nx(nx(i)))][1] < P[i][1] - 50),
            key=lambda i: P[i][0])
    ib = nx(nx(nx(u)))
    i, bar = li, P[li][1]
    while i != u:
        bar = max(bar, P[i][1])
        i = nx(i)
    xo, xi = P[li][0], P[u][0]
    J = DROP * bar
    (ro, kxo, kyo), (ri, kxi, kyi) = e18.o_quarter(o_layer, tan, 0), e18.o_quarter(o_layer, tan, 1)
    if ro[0] < ri[0]:
        kxo, kyo, kxi, kyi = kxi, kyi, kxo, kyo
    bx, by = P[b]
    ibx, iby = P[ib]
    assert by < J < P[li][1] and iby < J < P[u][1], "geometry"
    sl = lambda x_, y: (x_ + y * tan, y)
    out = []
    for k in range(m):
        n = nodes[k]
        if k == h1:
            out.append((*sl(bx + kxo * (xo - bx), by), "offcurve", False))
        elif k == h2:
            out.append((*sl(xo, J - kyo * (J - by)), "offcurve", False))
        elif k == x and display:
            out.append((*sl(xo, J), "curve", True))
        elif k == x:
            out.append((*sl(xo, J), "curve", True))
            out.append((*sl(*P[li]), "line", True))
        elif k == u:
            out.append((n.position.x, n.position.y, n.type, n.smooth))
            out.append((*sl(xi, J), "line", True))
        elif k == nx(u):
            out.append((*sl(xi, J - kyi * (J - iby)), "offcurve", False))
        elif k == nx(nx(u)):
            out.append((*sl(ibx + kxi * (xi - ibx), iby), "offcurve", False))
        else:
            out.append((n.position.x, n.position.y, n.type, n.smooth))
    return out, f"straight side from {bar:.0f} down to {J:.0f} at {xo:.0f} / {xi:.0f}; {m} -> {len(out)} nodes"


def main():
    text = open(GLYPHS_FILE).read()
    g3 = ".formatVersion = 3;" in text
    font = GSFont(GLYPHS_FILE)
    text, names = copy_glyphs(text, g3, font)
    text = add_feature(text, g3, names)
    open(GLYPHS_FILE, "w").write(text)
    print("  copies:", ", ".join(n + ALT for n in names))

    font = GSFont(GLYPHS_FILE)
    ids = {m.name: m for m in font.masters}

    def edit(mname, layer, nodes):
        m = ids[mname]
        out, info = plan(nodes, math.tan(math.radians(m.italicAngle)), font.glyphs["O"].layers[m.id])
        print(f"  {mname:32s} {info}")
        return {"replace_nodes": out}

    apply_edit(GLYPHS_FILE, "G", edit)
    print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
