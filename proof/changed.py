"""Which characters each family draws differently from its stock font, for
the proof's "non-stock" marks.

Nunuïko and Display: compared source to source. A glyph is changed when
any master's outline (nodes, components) or advance differs from the stock
.glyphs file (read from git history), or when one of its components is
changed; a character is changed when its glyph is.

Nunuïkode: Nunuïko's changed characters, plus those its code edits changed,
which its build lists in nunuikode/sources/edited-characters.txt. Moving
glyphs into the cell and condensing wide ones doesn't count.
"""
import subprocess

from glyphsLib import GSFont


def _shape(glyph, font):
    out = []
    for m in font.masters:
        lay = glyph.layers[m.id]
        if lay is None:
            out.append(None)
            continue
        paths = tuple(tuple((round(n.position.x), round(n.position.y), n.type) for n in p.nodes)
                      for p in lay.paths)
        comps = tuple((c.name, tuple(round(v, 3) for v in c.transform)) for c in lay.components)
        out.append((round(lay.width), paths, comps))
    return out


def source_changes(stock_path, ours_path):
    """Characters whose glyph differs between two .glyphs files."""
    a, b = GSFont(stock_path), GSFont(ours_path)
    ga = {g.name: g for g in a.glyphs}
    gb = {g.name: g for g in b.glyphs}
    own = {n for n, g in gb.items() if n not in ga or _shape(g, b) != _shape(ga[n], a)}
    memo = {}

    def changed(name):
        if name not in memo:
            memo[name] = False
            g = gb.get(name)
            comps = {c.name for m in b.masters if g and g.layers[m.id] for c in g.layers[m.id].components}
            memo[name] = name in own or any(changed(c) for c in comps)
        return memo[name]

    return {chr(int(g.unicode, 16)) for n, g in gb.items() if g.unicode and changed(n)}


def from_history(root, commit, path, dest):
    dest.write_bytes(subprocess.run(["git", "-C", root, "show", f"{commit}:{path}"],
                                    check=True, capture_output=True).stdout)
    return dest
