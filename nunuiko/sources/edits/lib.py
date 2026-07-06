"""Shared machinery for glyph edits on the raw .glyphs file.

glyphsLib is used READ-ONLY to parse geometry; edits are applied as
targeted text surgery (GSFont.save drops kerning groups / feature code —
see PLAYBOOK.md). Node lines are replaced positionally, never by content
matching (a new coordinate can collide with a later node's line).
"""
import re

from glyphsLib import GSFont

NUM = r"-?\d+(?:\.\d+)?"
NODE_RE = re.compile(rf'"{NUM} {NUM} (?:OFFCURVE|CURVE|LINE|QCURVE)(?: SMOOTH)?"')
WIDTH_RE = re.compile(r"width = (\d+);")


def fmt_node(x, y, ntype, smooth):
    s = f'"{x:.10g} {y:.10g} {ntype.upper()}'
    if smooth:
        s += " SMOOTH"
    return s + '"'


def apply_edit(glyphs_path, glyph_name, edit_fn):
    """Apply edit_fn to every master layer of glyph_name.

    edit_fn(master_name, layer, nodes) -> dict with optional keys:
      'nodes':   {global_node_index: (new_x, new_y)}  (index across all
                 paths, concatenated in order)
      'width':   new advance width (int)
      'anchors': {anchor_name: (new_x, new_y)}
    Coordinates are rounded to int. Returns True if the file changed.
    """
    text = open(glyphs_path).read()
    font = GSFont(glyphs_path)
    masters = {m.id: m.name for m in font.masters}

    block_start = text.index(f"glyphname = {glyph_name};")
    block_end = text.index("glyphname = ", block_start + 1)
    block = text[block_start:block_end]

    for layer in font.glyphs[glyph_name].layers:
        if layer.layerId not in masters:
            continue
        mname = masters[layer.layerId]
        nodes = [n for p in layer.paths for n in p.nodes]
        result = edit_fn(mname, layer, nodes) or {}

        lstart = block.index(f'layerId = "{layer.layerId}";')
        wmatch = WIDTH_RE.search(block, lstart)
        region = block[lstart : wmatch.end()]

        new_coords = result.get("nodes", {})
        if new_coords:
            spans = [m.span() for m in NODE_RE.finditer(region)]
            assert len(spans) == len(nodes), (mname, len(spans), len(nodes))
            pieces, prev = [], 0
            for i, (s, e) in enumerate(spans):
                n = nodes[i]
                old = fmt_node(n.position.x, n.position.y, n.type, n.smooth)
                assert region[s:e] == old, (mname, i, region[s:e], old)
                x, y = new_coords.get(i, (n.position.x, n.position.y))
                pieces.append(region[prev:s])
                pieces.append(fmt_node(round(x), round(y), n.type, n.smooth))
                prev = e
            pieces.append(region[prev:])
            new_region = "".join(pieces)
        else:
            new_region = region

        if result.get("width") is not None:
            old_width = int(wmatch.group(1))
            assert old_width == layer.width, (mname, old_width, layer.width)
            new_region = new_region.replace(
                f"width = {old_width};", f"width = {result['width']};"
            )
        block = block.replace(region, new_region)

        # anchors mirror in the background copy: expect exactly 2 occurrences
        for a in layer.anchors:
            if a.name not in result.get("anchors", {}):
                continue
            nx, ny = result["anchors"][a.name]
            old = f'position = "{{{a.position.x:g}, {a.position.y:g}}}";'
            new = f'position = "{{{round(nx):g}, {round(ny):g}}}";'
            count = block.count(old)
            assert count in (1, 2), (mname, a.name, count)
            block = block.replace(old, new)

    new_text = text[:block_start] + block + text[block_end:]
    if new_text == text:
        return False
    open(glyphs_path, "w").write(new_text)
    return True
