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
       - fits in CELL - 2*SB_MIN: moved, not reshaped, and centred
         optically: the cell centre goes halfway between the outline's
         box centre and its centre of mass (ink area). Asymmetric glyphs
         (l r j L [ ...) lean toward their heavy side without hugging an
         edge; the proportional sidebearings mean nothing in a cell
         (Nunuiko's tailed l has almost none on the right).
       - wider (m w M W, ligatures...): condensed horizontally by s and
         its vertical strokes thickened back by a horizontal stroke offset
         (each point moves d * its outward normal's x direction), so
         stems keep COMP (75%) of their weight instead of shrinking by s.
       All of it is done unslanted (x - y*tan(italic angle)) so italic
       slant survives condensing. Anchors take the same move/scale.
  5. Texture healing (as in Monaspace): wide letters get .texl/.texr/.texb
     alternates that extend HEAL (60) units past the cell, narrow letters
     .texl/.texr alternates shifted out of their way; calt picks them by
     neighbour (healing_features). Advances stay CELL.
  6. No kerning (monospace) and no f-ligatures (liga removed), no tnum; other
     features unchanged. OS/2 + post flag the font as fixed pitch.

Run from sources/:  python3 build.py   (build.sh runs it, then gftools)
"""
import glob
import importlib.util
import math
import os
import re
import shutil
import unicodedata

import glyphsLib
from glyphsLib import GSFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.statisticsPen import StatisticsPen
from fontTools.pens.transformPen import TransformPen
from ufo2ft.filters.decomposeComponents import DecomposeComponentsFilter

SOURCE = "upstream/Nunuiko.glyphs"
OUT = "build"
FAMILY = "Nunuikode"
CELL = 600       # every advance
SB_MIN = 30      # sidebearing for glyphs condensed to fit
COMP = 0.75      # share of lost stem weight given back when condensing
ALIGN = {"i": "idotless", "j": "jdotless"}  # placed exactly like these
HEAL = 60        # texture healing: units a wide letter borrows per side
WIDE_S = 0.9     # ... wide = condensed below this (first master)
NARROW = 0.6     # ... narrow = proportional advance <= this x n's


def load_edits():
    edits = []
    for path in sorted(glob.glob("edits/[0-9]*.py")):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        edits.append(mod)
    return edits


def unslanted_centroid_x(ufo, glyph, tan):
    sp = StatisticsPen(glyphset=ufo)
    glyph.draw(TransformPen(sp, (1, 0, -tan, 1, 0, 0)))
    return sp.meanX


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


def monospace(ufo, stem, tan, base_of, zero_width, heal):
    params = {}

    def root_of(name):
        while base_of.get(name) in ufo:
            name = base_of[name]
        return name

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
            mid = (x0 + x1) / 2
            centre = (mid + unslanted_centroid_x(ufo, g, tan)) / 2
            lsb = CELL / 2 - (centre - x0)
            lsb = min(CELL - SB_MIN - bw, max(SB_MIN, lsb))
            params[name] = (1.0, 0.0, x0, lsb)
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
    add_healing(ufo, stem, tan, params, root_of, heal)
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


def heal_sets(font, mid):
    """Letter glyphs that may heal: narrow ones by their proportional
    advance (first master); wide ones are picked later, by how much the
    monospace transform condenses them. Alternates (l.ss02, a.ss01 ...)
    count as letters by their base name, since ss01/ss02 run before calt."""
    by_name = {g.name: g for g in font.glyphs}
    n_width = by_name["n"].layers[mid].width
    letters, narrow = set(), set()
    for g in font.glyphs:
        if not g.export or "_" in g.name:
            continue
        base = by_name.get(g.name.split(".")[0])
        if base is None or not base.unicode:
            continue
        ch = chr(int(base.unicode, 16))
        if unicodedata.category(ch) not in ("Lu", "Ll", "Lt") \
                or unicodedata.decomposition(ch).startswith("<"):
            continue
        letters.add(g.name)
        if g.layers[mid].width <= NARROW * n_width:
            narrow.add(g.name)
    return letters, narrow


def add_healing(ufo, stem, tan, params, root_of, heal):
    """Texture healing alternates (as in Monaspace), all CELL wide:
      wide.texl / .texr / .texb  condensed less, extending HEAL units past
                                 the cell on the left / right / both sides
      narrow.texl / .texr        shifted up to HEAL units left / right,
                                 out of the way of the wide neighbour
    Accent composites share their base's alternate transforms, like the
    main transform. Adds the glyphs and their params; outlines are
    transformed with everything else."""
    inner = CELL - 2 * SB_MIN
    if "wide" not in heal:  # decided on the first master
        heal["wide"] = sorted(n for n in heal["letters"] - heal["narrow"]
                              if params.get(n) and params[n][0] < WIDE_S)
        heal["narrow"] = sorted(n for n in heal["narrow"] if params.get(n))
    cache = {}

    def alt(name, suf):
        root = root_of(name)
        key = (root, suf, name in wide)
        if key in cache:
            return cache[key]
        s, d, ox, nx = params[root]
        x0, x1 = unslanted_bounds(ufo, ufo[root], tan)
        bw = x1 - x0
        if suf in ("texl", "texr", "texb") and name in wide:
            left = HEAL if suf in ("texl", "texb") else 0
            room = inner + (HEAL if suf != "texb" else 2 * HEAL)
            if bw <= room:
                p = (1.0, 0.0, x0, SB_MIN - left + (room - bw) / 2)
            else:
                s2 = (room - COMP * stem) / (bw - COMP * stem)
                d2 = COMP * (1 - s2) * stem / 2
                p = (s2, d2, x0, SB_MIN - left + d2)
        else:  # narrow: same shape, shifted into its own spare space
            w = bw * s + 2 * d
            if suf == "texl":
                p = (s, d, ox, nx - max(0.0, min(HEAL, nx - SB_MIN)))
            else:
                p = (s, d, ox, nx + max(0.0, min(HEAL, CELL - nx - w - SB_MIN)))
        cache[key] = p
        return p

    wide = set(heal["wide"])
    cats = ufo.lib.get("public.openTypeCategories", {})
    order = ufo.lib.get("public.glyphOrder")
    for names, sufs in ((heal["wide"], ("texl", "texr", "texb")),
                        (heal["narrow"], ("texl", "texr"))):
        for name in names:
            for suf in sufs:
                new = ufo[name].copy(f"{name}.{suf}")
                new.unicodes = []
                ufo.addGlyph(new)
                params[new.name] = alt(name, suf)
                if name in cats:
                    cats[new.name] = cats[name]
                if order is not None:
                    order.append(new.name)


def healing_features(heal):
    """calt lookups. A narrow letter lends its space to one neighbour only:
    once a wide letter on its left has taken it, the wide letter on its
    right doesn't extend into it. Runs after every other substitution."""
    cls = lambda names, suf="": "[" + " ".join(n + suf for n in names) + "]"
    W, N = heal["wide"], heal["narrow"]
    return f"""
@TEX_W = {cls(W)};
@TEX_W_L = {cls(W, ".texl")};
@TEX_W_R = {cls(W, ".texr")};
@TEX_W_B = {cls(W, ".texb")};
@TEX_N = {cls(N)};
@TEX_N_L = {cls(N, ".texl")};
@TEX_N_R = {cls(N, ".texr")};

lookup tex_wide {{
    sub [@TEX_W_R @TEX_W_B] @TEX_N @TEX_W' @TEX_N by @TEX_W_R;
    ignore sub [@TEX_W_R @TEX_W_B] @TEX_N @TEX_W';
    sub @TEX_N @TEX_W' @TEX_N by @TEX_W_B;
    sub @TEX_N @TEX_W' by @TEX_W_L;
    sub @TEX_W' @TEX_N by @TEX_W_R;
}} tex_wide;

lookup tex_narrow {{
    sub @TEX_N' [@TEX_W_L @TEX_W_B] by @TEX_N_L;
    sub [@TEX_W_R @TEX_W_B] @TEX_N' by @TEX_N_R;
}} tex_narrow;

feature calt {{
    lookup tex_wide;
    lookup tex_narrow;
}} calt;
"""


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
    # f-ligatures would put two letters in one cell; tnum is meaningless
    # (every figure is CELL wide) and edit 3 made its one.tf targets footless
    for tag in ("liga", "tnum"):
        text = re.sub(rf"\nfeature {tag} \{{.*?\}} {tag};\n", "\n", text, flags=re.S)
    return text


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
    letters, narrow = heal_sets(font, mid)
    heal = {"letters": letters, "narrow": narrow}

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
        monospace(ufo, stem, tan, base_of, zero_width, heal)
        add_notdef(ufo, stem)
        # glyphsLib's eraseOpenCorners would cut Nunito's small overlap
        # loops; after condensing they don't line up across masters, so it
        # would make masters incompatible. The loops are plain overlaps and
        # render fine in a variable font: keep them.
        ufo.lib["com.github.googlei18n.ufo2ft.filters"] = [
            f for f in ufo.lib.get("com.github.googlei18n.ufo2ft.filters", [])
            if f.get("name") != "eraseOpenCorners"]
        ufo.kerning.clear()
        ufo.features.text = strip_features(ufo.features.text) + healing_features(heal)
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
    print(f"texture healing: {len(heal['wide'])} wide, {len(heal['narrow'])} narrow letters:",
          " ".join(n for n in heal["wide"] if len(n) == 1), "/",
          " ".join(n for n in heal["narrow"] if len(n) == 1))
    ds.write(os.path.join(OUT, f"{FAMILY}.designspace"))
    print("written", os.path.join(OUT, f"{FAMILY}.designspace"))


if __name__ == "__main__":
    main()
