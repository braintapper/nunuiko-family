"""Glyph edit 17: capital J — the hook rises as high as Nunuiko's.

Edit 05 ends Display's hook in a flat cut at H (0.9 x the stem's
curve-start height), where Nunuiko's rounded cap rises half the hook
weight above H. Here the hook's left upright is extended straight up by
half the hook weight, so the flat cut sits where the top of Nunuiko's cap
does: 180 / 243 at ExtraLight / Bold, as in Nunuiko (Heavy: Display's
ExtraBlack hook is 129 thick, so 263 against Nunuiko's 265).

On edit 05's 16-node J: node 9 (curve, inner end of the hook at H) and
node 10 (line, outer end at H) are the two ends of the cut. Two line nodes
are inserted between them at H + w/2 (w = hook weight, node 9 x - node 10
x): up the inner side, across the cut, and back down the outer side to
node 10, which becomes smooth (a straight run into its curve). In the
italic the rise follows the 9° slant. Output: 18 nodes in every master.

Composites (Jcircumflex, IJ, NJ ...) follow; no width changes.
Run once per source from sources/:
  python3 edits/17_J_tail_height.py
  python3 edits/17_J_tail_height.py NunuikoDisplay-Italic.glyphs
"""
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else "NunuikoDisplay.glyphs"


def main():
    font = GSFont(GLYPHS_FILE)
    angles = {m.name: m.italicAngle for m in font.masters}

    def edit(mname, layer, nodes):
        assert len(nodes) == 16, (mname, len(nodes))
        n9, n10 = nodes[9], nodes[10]
        assert n9.type == "curve" and n10.type == "line", mname
        assert abs(n9.position.y - n10.position.y) < 0.5, mname
        tan = math.tan(math.radians(angles[mname]))
        w = n9.position.x - n10.position.x
        d = w / 2
        out = [(n.position.x, n.position.y, n.type, n.smooth) for n in nodes]
        a = (n9.position.x + d * tan, n9.position.y + d, "line", False)
        b = (n10.position.x + d * tan, n10.position.y + d, "line", False)
        out[10] = (n10.position.x, n10.position.y, "line", True)
        out[10:10] = [a, b]
        print(f"  {mname:32s} hook {w:.0f}, cut {n9.position.y:.0f} -> {a[1]:.0f}")
        return {"replace_nodes": out}

    changed = apply_edit(GLYPHS_FILE, "J", edit)
    print("written" if changed else "unchanged", GLYPHS_FILE)


if __name__ == "__main__":
    main()
