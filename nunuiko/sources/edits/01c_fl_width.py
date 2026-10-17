"""Glyph edit 1c: fl ligature — fix stale advance width after the l tail edit.

`fl` is a composite: f + l (l placed at f's advance). Edit 1 shortened the l
and reduced its advance (EL 275->218 etc.), but the fl composite kept its OLD
advance, leaving ~44-57 units of dead space after the l — visible as "too much
space before the next character" in fl (and in typed 'ffl', which has no glyph
of its own and renders as f + the fl ligature).

Fix: set fl's advance to (l-component offset + l's advance) per master, so the
space after fl matches the space after a standalone l:
    ExtraLight 581 -> 524   Bold 683 -> 632   Heavy 787 -> 743

fl.ss02 references l.ss02 (untouched by edit 1) and is already correct — left
alone. fi is outlines, unaffected. Applied to all masters (upright + italic;
italic added 2026-07-07 when building italics).

Run once from sources/: python3 edits/01c_fl_width.py
"""
from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
# corrected advance per master = l offset + l advance
WIDTH = {
    "ExtraLight": 524, "Bold": 632, "Heavy": 743,
    "ExtraLight Italic": 532, "Bold Italic": 640, "Heavy Italic": 750,
}


def edit(mname, layer, nodes):
    if mname not in WIDTH:
        return {}
    print(f"{mname:12s} fl width {layer.width:g} -> {WIDTH[mname]}")
    return {"width": WIDTH[mname]}


if __name__ == "__main__":
    changed = apply_edit(GLYPHS_FILE, "fl", edit)
    print("done" if changed else "nothing changed — already applied?")
