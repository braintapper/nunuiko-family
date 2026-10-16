"""Generate Nunuikode's UFO masters + designspace from the Nunuiko source.

Nunuikode is Nunuiko made monospaced for code. The source of truth stays
upstream: sources/upstream/Nunuiko.glyphs is a snapshot of the Nunuiko
repo (commit in sources/upstream/NUNUIKO_COMMIT), and this script derives
everything else, so re-syncing is: copy the new Nunuiko.glyphs in, rebuild.

Steps, per master (6 masters: ExtraLight / Bold / Heavy, upright + italic):
  1. glyphsLib: Nunuiko.glyphs -> designspace + UFO masters, family
     renamed to Nunuikode.
  2. Character edits for code (sources/edits/*.py, in name order), applied
     while composites are still composites so derived glyphs follow.
  3. Decompose every composite, then drop non-exported helper glyphs.
     Accent composites (base at the origin + zero-width marks) remember
     their base glyph so they get the base's exact transform and stay
     aligned with it; i and j likewise follow idotless / jdotless.
  4. Monospace: every glyph with an advance gets CELL (600, the width the
     figures already have). Zero-width glyphs (combining marks, ZWSP)
     stay zero-width.
       - fits in CELL - 2*SB_MIN: moved, not reshaped. Its old left/right
         sidebearing ratio is kept (clamped to 0.25..0.75) so asymmetric
         letters (f r j L ...) keep their optical placement.
       - wider (m w M W, ligatures...): condensed horizontally by s and
         its vertical strokes thickened back by a horizontal stroke offset
         (each point moves d * its outward normal's x direction), so
         stems keep COMP (75%) of their weight instead of shrinking by s.
       All of it is done unslanted (x - y*tan(italic angle)) so italic
       slant survives condensing. Anchors take the same move/scale.
  5. No kerning (monospace) and no f-ligatures (liga removed); other
     features unchanged. OS/2 + post flag the font as fixed pitch.

Run from sources/:  python3 build.py   (build.sh runs it, then gftools)
"""
import glob
import importlib.util
import math
import os
import re
import shutil

import glyphsLib
from glyphsLib import GSFont
from fontTools.pens.boundsPen import BoundsPen
from ufo2ft.filters.decomposeComponents import DecomposeComponentsFilter

SOURCE = "upstream/Nunuiko.glyphs"
OUT = "build"
FAMILY = "Nunuikode"
CELL = 600       # every advance
SB_MIN = 30      # sidebearing for glyphs condensed to fit
COMP = 0.75      # share of lost stem weight given back when condensing
ALIGN = {"i": "idotless", "j": "jdotless"}  # placed exactly like these


def load_edits():
    edits = []
    for path in sorted(glob.glob("edits/[0-9]*.py")):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        edits.append(mod)
    return edits


def unslanted_bounds(ufo, glyph, tan):
    xs, ys = [], []
    for c in glyph:
        for p in c:
            xs.append(p.x - p.y * tan)
            ys.append(p.y)
    if not xs:
        return None
    return min(xs), max(xs)


def outward_x(contour, i, n):
    """x component of the outward (away from ink) unit normal at point i.
    Outer contours run counter-clockwise, counters clockwise, so the
    outward normal of travel direction t is (t.y, -t.x) for both."""
    prev = contour[(i - 1) % n]
    nxt = contour[(i + 1) % n]
    tx, ty = nxt.x - prev.x, nxt.y - prev.y
    ln = math.hypot(tx, ty)
    return ty / ln if ln else 0.0


def monospace(ufo, stem, tan, base_of, zero_width):
    params = {}

    def resolve(name):
        if name in params:
            return params[name]
        g = ufo[name]
        if name in zero_width:  # decided once, from the first master
            g.width = 0  # (upstream caron.alt is 500 in one italic master)
            params[name] = None
            return None
        base = base_of.get(name)
        if base and base in ufo:
            params[name] = resolve(base)
            return params[name]
        b = unslanted_bounds(ufo, g, tan)
        if b is None:
            params[name] = (1.0, 0.0, 0.0, 0.0)  # empty: only the width changes
            return params[name]
        x0, x1 = b
        bw = x1 - x0
        inner = CELL - 2 * SB_MIN
        if bw <= inner:
            lsb, rsb = x0, g.width - x1
            r = lsb / (lsb + rsb) if lsb + rsb > 0 else 0.5
            r = min(0.75, max(0.25, r))
            params[name] = (1.0, 0.0, x0, (CELL - bw) * r)
        else:
            s = (inner - COMP * stem) / (bw - COMP * stem)
            d = COMP * (1 - s) * stem / 2
            params[name] = (s, d, x0, SB_MIN + d)
        return params[name]

    # resolve everything first: an accent composite reuses its base's
    # transform only while the base still has its original advance
    for name in list(ufo.keys()):
        resolve(name)
    squeezed = sorted((p[0], n) for n, p in params.items() if p and p[0] < 1)
    print(f"  condensed {len(squeezed)} glyphs; tightest "
          + ", ".join(f"{n} {s:.2f}" for s, n in squeezed[:4])
          + "; " + " ".join(f"{n} {params[n][0]:.2f}" for n in ("m", "w", "M", "W") if n in params))
    for name in ufo.keys():
        p = params[name]
        g = ufo[name]
        if p is None:
            continue
        s, d, ox, nx = p
        for c in g:
            n = len(c)
            pts = list(c)
            un = [(q.x - q.y * tan, q.y) for q in pts]
            # stroke offset follows the on-curve point a handle belongs to
            dx = [0.0] * n
            if d:
                on = [k for k in range(n) if pts[k].segmentType is not None]
                for k in on:
                    nxv = outward_x(c, k, n)
                    dx[k] = d * max(-1.0, min(1.0, nxv / 0.3))
                for k in range(n):
                    if pts[k].segmentType is None:
                        # off-curve: owner is the on-curve on the same side
                        before = pts[(k - 1) % n].segmentType is not None
                        dx[k] = dx[(k - 1) % n] if before else dx[(k + 1) % n]
            for k, q in enumerate(pts):
                xu = nx + (un[k][0] - ox) * s + dx[k]
                q.x = xu + q.y * tan
        for a in g.anchors:
            xu = nx + ((a.x - a.y * tan) - ox) * s
            a.x = xu + a.y * tan
        g.width = CELL


def add_notdef(ufo, stem):
    """Nunuiko has no .notdef (the compiler would make a 500-wide one):
    draw the usual box, CELL wide, stroke = stem."""
    if ".notdef" in ufo:
        return
    g = ufo.newGlyph(".notdef")
    g.width = CELL
    x0, x1, y0, y1 = 2 * SB_MIN, CELL - 2 * SB_MIN, 0, 700
    t = max(20, stem * 0.6)
    pen = g.getPen()
    for (a, b, c, d), ccw in (((x0, y0, x1, y1), True), ((x0 + t, y0 + t, x1 - t, y1 - t), False)):
        pts = [(a, b), (c, b), (c, d), (a, d)]
        if not ccw:
            pts.reverse()
        pen.moveTo(pts[0])
        for q in pts[1:]:
            pen.lineTo(q)
        pen.closePath()
    order = ufo.lib.get("public.glyphOrder")
    if order is not None and ".notdef" not in order:
        ufo.lib["public.glyphOrder"] = [".notdef"] + order


def strip_features(text):
    # f-ligatures would put two letters in one cell
    return re.sub(r"\nfeature liga \{.*?\} liga;\n", "\n", text, flags=re.S)


def main():
    font = GSFont(SOURCE)
    font.familyName = FAMILY
    # composites whose first component is the base at the origin, with the
    # same advance (accented letters): remember the base before decomposing
    # (Accent composites: first component is the base at the origin and
    # every other component is a zero-width mark. Advance widths aren't
    # compared: some, like lacute's, are stale upstream.)
    mid = font.masters[0].id
    zero_width = {g.name for g in font.glyphs if g.layers[mid].width == 0}
    base_of = {}
    for g in font.glyphs:
        lay = g.layers[mid]
        comps = list(lay.components)
        if comps and not lay.paths and tuple(comps[0].position) == (0, 0) \
                and all(c.name in zero_width for c in comps[1:]):
            base_of[g.name] = comps[0].name
    # i and j are drawn on their own, but must sit exactly where their
    # dotless forms (the base of í ì ĵ ...) sit
    base_of.update(ALIGN)

    # non-exported helpers (_part.* components, scratch glyphs like
    # 'apple' whose masters don't match): dropped after decomposing, so
    # the glyphs built from them keep their shapes
    skip = {g.name for g in font.glyphs if not g.export}

    ds = glyphsLib.to_designspace(font, minimize_glyphs_diffs=False)
    edits = load_edits()
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    for src in ds.sources:
        ufo = src.font
        stem = src.location["Weight"]
        angle = -(ufo.info.italicAngle or 0)  # UFO: negative = slanted right
        tan = math.tan(math.radians(angle))
        for e in edits:
            e.apply(ufo, stem=stem, tan=tan)
        DecomposeComponentsFilter()(ufo)
        for name in skip & set(ufo.keys()):
            del ufo[name]
        ufo.lib.pop("public.skipExportGlyphs", None)
        order = ufo.lib.get("public.glyphOrder")
        if order:
            ufo.lib["public.glyphOrder"] = [n for n in order if n not in skip]
        monospace(ufo, stem, tan, base_of, zero_width)
        add_notdef(ufo, stem)
        # glyphsLib's eraseOpenCorners would cut Nunito's small overlap
        # loops; after condensing they don't line up across masters, so it
        # would make masters incompatible. The loops are plain overlaps and
        # render fine in a variable font: keep them.
        ufo.lib["com.github.googlei18n.ufo2ft.filters"] = [
            f for f in ufo.lib.get("com.github.googlei18n.ufo2ft.filters", [])
            if f.get("name") != "eraseOpenCorners"]
        ufo.kerning.clear()
        ufo.features.text = strip_features(ufo.features.text)
        ufo.info.familyName = FAMILY
        ufo.info.postscriptIsFixedPitch = True
        panose = list(ufo.info.openTypeOS2Panose or [2, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        panose[3] = 9  # proportion: monospaced
        ufo.info.openTypeOS2Panose = panose
        src.path = os.path.join(OUT, src.filename)  # already Nunuikode-*
        ufo.save(src.path, overwrite=True)
        print(f"{src.filename:32s} stem {stem:3g}  angle {angle:g}")
    for inst in ds.instances:
        inst.familyName = FAMILY
    ds.write(os.path.join(OUT, f"{FAMILY}.designspace"))
    print("written", os.path.join(OUT, f"{FAMILY}.designspace"))


if __name__ == "__main__":
    main()
