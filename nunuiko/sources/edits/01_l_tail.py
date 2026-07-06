"""Glyph edit 1: shorten the tail of lowercase l.

Rule (see GLYPHLOG.md): compress the tail region horizontally toward the
stem's bottom-right edge (pivot = node 14 x, per master) by FACTOR.
Tail region = node indices 0-13 (terminal cap + inner sweep) and 23-25
(outer bottom curve); stem/top nodes 14-22 untouched. Advance width
shrinks by the tail tip's retreat. Anchors `bottom` and `dot` follow the
same compression; `top`, `topright`, `center` stay.

Compression is affine in x, so collinear points stay collinear and all
SMOOTH joints survive exactly. Same 26-node structure required in every
master (asserted).

Text-surgery on the .glyphs file — glyphsLib is used read-only for
parsing (its save drops kerning groups / feature code; see PLAYBOOK.md).
Run once from sources/: python3 edits/01_l_tail.py
Backgrounds are left untouched (they don't ship), EXCEPT anchors, which
are mirrored in backgrounds and kept in sync.
"""
import re
import sys

from glyphsLib import GSFont

GLYPHS_FILE = "Nunuiko.glyphs"
GLYPH = "l"
FACTOR = 0.6
PIVOT_NODE = 14  # stem bottom-right junction; also first untouched node
TAIL_NODES = list(range(0, 14)) + [23, 24, 25]
EXPECTED_NODE_COUNT = 26
MOVE_ANCHORS = {"bottom", "dot"}


def fmt_node(x, y, ntype, smooth):
    s = f'"{x:g} {y:g} {ntype.upper()}'
    if smooth:
        s += " SMOOTH"
    return s + '"'


def compress(x, pivot):
    return round(pivot + FACTOR * (x - pivot))


def main():
    text = open(GLYPHS_FILE).read()
    font = GSFont(GLYPHS_FILE)
    masters = {m.id: m.name for m in font.masters}
    glyph = font.glyphs[GLYPH]

    # scope all replacements to this glyph's block
    block_start = text.index(f"glyphname = {GLYPH};")
    block_end = text.index("glyphname = ", block_start + 1)
    block = text[block_start:block_end]

    for layer in glyph.layers:
        if layer.layerId not in masters:
            continue
        mname = masters[layer.layerId]
        (path,) = layer.paths
        nodes = path.nodes
        assert len(nodes) == EXPECTED_NODE_COUNT, (mname, len(nodes))
        pivot = nodes[PIVOT_NODE].position.x
        old_tip = max(n.position.x for n in nodes)

        # active outline region: from this layerId line to its width line
        lstart = block.index(f'layerId = "{layer.layerId}";')
        wmatch = re.compile(r"width = (\d+);").search(block, lstart)
        region = block[lstart : wmatch.end()]

        # positional replacement: node lines appear in file in node order;
        # matching by content is unsafe (a compressed line can collide with
        # a later original line)
        node_re = re.compile(r'"-?\d+ -?\d+ (?:OFFCURVE|CURVE|LINE|QCURVE)(?: SMOOTH)?"')
        spans = [m.span() for m in node_re.finditer(region)]
        assert len(spans) == EXPECTED_NODE_COUNT, (mname, len(spans))
        pieces, prev = [], 0
        for i, (s, e) in enumerate(spans):
            n = nodes[i]
            x, y = n.position.x, n.position.y
            old = fmt_node(x, y, n.type, n.smooth)
            assert region[s:e] == old, (mname, i, region[s:e], old)
            if i in TAIL_NODES and x > pivot:
                x = compress(x, pivot)
            pieces.append(region[prev:s])
            pieces.append(fmt_node(x, y, n.type, n.smooth))
            prev = e
        pieces.append(region[prev:])
        new_region = "".join(pieces)

        new_tip = compress(old_tip, pivot)
        old_width = int(wmatch.group(1))
        assert old_width == layer.width
        new_width = old_width - (old_tip - new_tip)
        new_region = new_region.replace(
            f"width = {old_width};", f"width = {new_width};"
        )
        block = block.replace(region, new_region)
        print(
            f"{mname:20s} pivot={pivot:g} tip {old_tip:g}->{new_tip}"
            f" width {old_width}->{new_width}"
        )

        # anchors: appear twice per layer (active + background), same values
        for a in layer.anchors:
            if a.name not in MOVE_ANCHORS or a.position.x <= pivot:
                continue
            old = f'position = "{{{a.position.x:g}, {a.position.y:g}}}";'
            new = (
                f'position = "{{{compress(a.position.x, pivot):g},'
                f" {a.position.y:g}}}\";"
            )
            assert block.count(old) == 2, (mname, a.name, old)
            block = block.replace(old, new)
            print(f"{'':20s} anchor {a.name}: x {a.position.x:g}"
                  f" -> {compress(a.position.x, pivot)}")

    new_text = text[:block_start] + block + text[block_end:]
    if new_text == text:
        sys.exit("nothing changed — already applied?")
    open(GLYPHS_FILE, "w").write(new_text)
    print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
