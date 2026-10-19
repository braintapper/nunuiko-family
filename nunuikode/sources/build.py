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
       - fits in CELL - 2*SB_MIN (SB_CAP for capitals): moved, not reshaped, and centred
         optically: the cell centre goes halfway between the outline's
         box centre and its centre of mass (ink area). Asymmetric glyphs
         (l r j L [ ...) lean toward their heavy side without hugging an
         edge; the proportional sidebearings mean nothing in a cell
         (Nunuiko's tailed l had almost none on the right).
       - lowercase letters (not i j l t f, shaped for the cell by edits) are
         judged by their side white: the mean white per scanline across
         the x-height, each side counted at most half a cell deep. If the
         tighter side has more than OPEN (1.45) x the n's, the letter
         widens (by at most OPEN_MAX, 1.3; stems thinned back by COMP) so
         v y x k s z c don't sit in holes. Then it moves BALANCE (75%) of
         the way to equal white each side, so open-sided letters (r c k e)
         sit toward their open side. (r is placed like the n, see ALIGN.)
         c, e and a widen to at least the o's ink width (WIDE_AS), as
         far as the cell allows: they set narrower than the o beside it.
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
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.statisticsPen import StatisticsPen
from fontTools.pens.transformPen import TransformPen
from ufo2ft.filters.decomposeComponents import DecomposeComponentsFilter

SOURCE = "upstream/Nunuiko.glyphs"
OUT = "build"
FAMILY = "Nunuikode"
VERSION = (0, 100)  # font version 0.100 = release 0.1.0
CELL = 600       # every advance
SB_MIN = 30      # sidebearing for glyphs condensed to fit
SB_CAP = 60      # ... for capital letters: at 30, runs of capitals (FROM,
                 # WHERE) set far tighter than lowercase (n has 70-110)
COMP = 0.75      # share of lost stem weight given back when condensing
ALIGN = {"i": "idotless", "j": "jdotless",  # placed exactly like these
         "r": "n"}  # r is drawn from the n (edit 3): its stem goes where the n's left stem goes
HEAL = 60        # texture healing: units a wide letter borrows per side
WIDE_S = 0.9     # ... wide = condensed below this (first master)
NARROW = 0.6     # ... narrow = proportional advance <= this x n's
OPEN = 1.45      # lowercase with more side white than this x n's widen,
OPEN_MAX = 1.3   # ... by at most this
OPEN_SKIP = {"i", "j", "l", "idotless", "jdotless", "t", "f"}  # shaped for the cell (edits 3, 7)
BALANCE = 0.75   # lowercase: share of the left/right white difference evened out
WIDE_AS = {"c": "o", "e": "o", "a": "o"}  # lowercase widened to at least this letter's ink width


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


def ink_width(ufo, glyph, tan):
    bp = BoundsPen(ufo)
    glyph.draw(TransformPen(bp, (1, 0, -tan, 1, 0, 0)))
    return bp.bounds[2] - bp.bounds[0]


class FlattenPen(BasePen):
    """Outline as polygons (curves sampled), for scanline profiles."""
    def __init__(self, glyphset=None):
        super().__init__(glyphset)
        self.polys = []

    def _moveTo(self, p):
        self.polys.append([p])

    def _lineTo(self, p):
        self.polys[-1].append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._getCurrentPoint()
        for k in range(1, 13):
            t = k / 12
            a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
            self.polys[-1].append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                                   a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))

    def _closePath(self):
        pass


def side_profile(ufo, glyph, tan, top):
    """Ink extent (xmin, xmax), unslanted, on scanlines across 0..top;
    None where a line has no ink."""
    pen = FlattenPen(ufo)
    glyph.draw(TransformPen(pen, (1, 0, -tan, 1, 0, 0)))
    out = []
    for y in range(10, int(top) - 5, 20):
        xs = []
        for poly in pen.polys:
            for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
                if (ay <= y < by) or (by <= y < ay):
                    xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
        out.append((min(xs), max(xs)) if xs else None)
    return out


def side_white(prof, x0, bw, s, left=None):
    """Mean white per scanline (left, right), with the glyph scaled by s and
    its box's left edge at `left` (default: centred in the cell); each
    side counted at most half a cell deep."""
    cap = CELL / 2
    if left is None:
        left = (CELL - s * bw) / 2
    right = CELL - left - s * bw
    tl = tr = 0.0
    for e in prof:
        if e is None:
            tl += cap
            tr += cap
        else:
            tl += min(cap, left + s * (e[0] - x0))
            tr += min(cap, right + s * (x0 + bw - e[1]))
    return tl / len(prof), tr / len(prof)


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

    xh = ufo.info.xHeight
    n_white = []

    def opening(name, g, x0, bw, inner):
        """Lowercase letters with far more side white than n (r t v z ...)
        widen until they have OPEN x n's, by at most OPEN_MAX, so they
        don't sit in a hole between their neighbours."""
        if name not in heal["letters"] or name in heal["upper"] \
                or name.split(".")[0] in OPEN_SKIP:
            return 1.0, None
        if not n_white:
            nb = unslanted_bounds(ufo, ufo["n"], tan)
            n_white.append(sum(side_white(side_profile(ufo, ufo["n"], tan, xh),
                                          nb[0], nb[1] - nb[0], 1.0)))
        prof = side_profile(ufo, g, tan, xh)
        # judged by the tighter side: the hole under r's arm or in c's
        # mouth doesn't close by widening, it is evened out by BALANCE
        tight = lambda s: 2 * min(side_white(prof, x0, bw, s))
        target = OPEN * n_white[0]
        hi = min(OPEN_MAX, inner / bw)
        if tight(1.0) <= target or hi <= 1:
            return 1.0, prof
        lo = 1.0
        for _ in range(20):
            mid = (lo + hi) / 2
            if tight(mid) > target:
                lo = mid
            else:
                hi = mid
        return hi, prof

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
        sb = SB_CAP if name in heal["upper"] else SB_MIN
        inner = CELL - 2 * sb
        s, prof = opening(name, g, x0, bw, inner)
        if prof is not None and name in WIDE_AS:
            # true ink widths (curves, not their handles); the widened stems
            # are thinned back by COMP, which takes 2|d| off the ink width:
            # solve for the width after that
            ow, cw = ink_width(ufo, ufo[WIDE_AS[name]], tan), ink_width(ufo, g, tan)
            k = COMP * stem
            s = max(s, min(inner / bw, (ow - k) / (cw - k)))
        if prof is not None and bw * s <= inner:
            # lowercase: optical centre as below, then moved BALANCE of the
            # way to equal white each side (r's open right, c's, k's ...)
            mid = (x0 + x1) / 2
            centre = (mid + unslanted_centroid_x(ufo, g, tan)) / 2
            d = COMP * (1 - s) * stem / 2 if s > 1 else 0.0  # < 0: thinned back
            nx = CELL / 2 - s * (centre - x0)
            wl, wr = side_white(prof, x0, bw, s, nx)
            nx += BALANCE * (wr - wl) / 2
            nx = min(CELL - sb - bw * s - d, max(sb + d, nx))
            params[name] = (s, d, x0, nx)
        elif bw <= inner:
            mid = (x0 + x1) / 2
            centre = (mid + unslanted_centroid_x(ufo, g, tan)) / 2
            lsb = CELL / 2 - (centre - x0)
            lsb = min(CELL - sb - bw, max(sb, lsb))
            params[name] = (1.0, 0.0, x0, lsb)
        else:
            s = (inner - COMP * stem) / (bw - COMP * stem)
            d = COMP * (1 - s) * stem / 2
            params[name] = (s, d, x0, sb + d)
        return params[name]

    # resolve everything first: an accent composite reuses its base's
    # transform only while the base still has its original advance
    for name in list(ufo.keys()):
        resolve(name)
    opened = sorted((p[0], n) for n, p in params.items() if p and p[0] > 1 and len(n) == 1)
    print("  opened " + " ".join(f"{n} {s:.2f}" for s, n in opened))
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


def signature(glyph):
    """A glyph's outline and components, to tell whether an edit touched it."""
    return (tuple(tuple((round(p.x, 2), round(p.y, 2), p.segmentType) for p in c) for c in glyph),
            tuple((c.baseGlyph, tuple(round(v, 4) for v in c.transformation)) for c in glyph.components),
            round(glyph.width, 2))


def edited_characters(ufo, edited):
    """Characters whose glyph an edit changed, directly or through a
    component, for the proof's non-stock marks."""
    memo = {}

    def hit(name):
        if name not in memo:
            memo[name] = False
            g = ufo[name]
            memo[name] = name in edited or any(hit(c.baseGlyph) for c in g.components if c.baseGlyph in ufo)
        return memo[name]

    return {chr(u) for g in ufo for u in g.unicodes if hit(g.name)}


def heal_sets(font, mid):
    """Letter glyphs that may heal: narrow ones by their proportional
    advance (first master); wide ones are picked later, by how much the
    monospace transform condenses them. Alternates (l.ss02, a.ss01 ...)
    count as letters by their base name, since ss01/ss02 run before calt.
    Also returns the capital letters, which get SB_CAP."""
    by_name = {g.name: g for g in font.glyphs}
    n_width = by_name["n"].layers[mid].width
    letters, narrow, upper = set(), set(), set()
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
        if unicodedata.category(ch) in ("Lu", "Lt"):
            upper.add(g.name)
        if g.layers[mid].width <= NARROW * n_width:
            narrow.add(g.name)
    return letters, narrow, upper


def add_healing(ufo, stem, tan, params, root_of, heal):
    """Texture healing alternates (as in Monaspace), all CELL wide:
      wide.texl / .texr / .texb  condensed less, extending HEAL units past
                                 the cell on the left / right / both sides
      narrow.texl / .texr        shifted up to HEAL units left / right,
                                 out of the way of the wide neighbour
    Accent composites share their base's alternate transforms, like the
    main transform. Adds the glyphs and their params; outlines are
    transformed with everything else."""
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
        sb = SB_CAP if root in heal["upper"] else SB_MIN
        inner = CELL - 2 * sb
        x0, x1 = unslanted_bounds(ufo, ufo[root], tan)
        bw = x1 - x0
        if suf in ("texl", "texr", "texb") and name in wide:
            left = HEAL if suf in ("texl", "texb") else 0
            room = inner + (HEAL if suf != "texb" else 2 * HEAL)
            if bw <= room:
                p = (1.0, 0.0, x0, sb - left + (room - bw) / 2)
            else:
                s2 = (room - COMP * stem) / (bw - COMP * stem)
                d2 = COMP * (1 - s2) * stem / 2
                p = (s2, d2, x0, sb - left + d2)
        else:  # narrow: same shape, shifted into its own spare space
            w = bw * s + 2 * d
            if suf == "texl":
                p = (s, d, ox, nx - max(0.0, min(HEAL, nx - sb)))
            else:
                p = (s, d, ox, nx + max(0.0, min(HEAL, CELL - nx - w - sb)))
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
    """calt lookups. A narrow letter lends its space to one neighbour only,
    and only when its other neighbour isn't narrow too: stepping aside
    would pinch it against that letter (the i in "will" against the l).
    Both-sided extensions claim their narrows first, then right, then
    left; each later lookup skips a narrow an earlier one has taken.
    Runs after every other substitution."""
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

lookup tex_both {{
    ignore sub @TEX_W_B @TEX_N @TEX_W';
    ignore sub @TEX_N @TEX_N @TEX_W';
    ignore sub @TEX_W' @TEX_N @TEX_N;
    sub @TEX_N @TEX_W' @TEX_N by @TEX_W_B;
}} tex_both;

lookup tex_right {{
    ignore sub @TEX_W' @TEX_N @TEX_N;
    ignore sub @TEX_W' @TEX_N @TEX_W_B;
    sub @TEX_W' @TEX_N by @TEX_W_R;
}} tex_right;

lookup tex_left {{
    ignore sub [@TEX_W_R @TEX_W_B] @TEX_N @TEX_W';
    ignore sub @TEX_N @TEX_N @TEX_W';
    sub @TEX_N @TEX_W' by @TEX_W_L;
}} tex_left;

lookup tex_narrow {{
    sub @TEX_N' [@TEX_W_L @TEX_W_B] by @TEX_N_L;
    sub [@TEX_W_R @TEX_W_B] @TEX_N' by @TEX_N_R;
}} tex_narrow;

feature calt {{
    lookup tex_both;
    lookup tex_right;
    lookup tex_left;
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
    # Nunuikode has its own version, separate from the Nunuiko snapshot's
    # (the snapshot carries Nunuiko's version, which means nothing here).
    font.versionMajor, font.versionMinor = VERSION
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
    letters, narrow, upper = heal_sets(font, mid)
    chars = set()
    heal = {"letters": letters, "narrow": narrow, "upper": upper}

    ds = glyphsLib.to_designspace(font, minimize_glyphs_diffs=False)
    edits = load_edits()
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    for src in ds.sources:
        ufo = src.font
        stem = src.location["Weight"]
        angle = -(ufo.info.italicAngle or 0)  # UFO: negative = slanted right
        tan = math.tan(math.radians(angle))
        before = {g.name: signature(g) for g in ufo}
        for e in edits:
            e.apply(ufo, stem=stem, tan=tan)
        edited = {g.name for g in ufo if before.get(g.name) != signature(g)}
        chars |= edited_characters(ufo, edited)
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
    # characters the code edits changed (any master): read by the family proof
    with open("edited-characters.txt", "w") as f:
        f.write("".join(sorted(chars)) + "\n")
    print(f"edited characters: {len(chars)}")
    print("written", os.path.join(OUT, f"{FAMILY}.designspace"))


if __name__ == "__main__":
    main()
