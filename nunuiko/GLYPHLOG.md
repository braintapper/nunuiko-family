# Nunuïko glyph change log

Detailed record of every glyph modification, precise enough to **replay the
same edit on Nunito Sans** (→ Nunuïko Display) without re-deriving it.
Design rationale lives in `fonts.md`; this file is the engineering log.

## Conventions

- Coordinates are in font units (UPM 1000), `(x, y)` from the glyph origin.
- Every edit is recorded **per master**. Masters in `Nunuiko.glyphs`
  (3 weights × upright/italic; stems ≈ 42 / 125 / 208):

  | # | Master | Stem | Italic |
  |---|--------|------|--------|
  | 1 | Light | 42 | no |
  | 2 | Regular | 125 | no |
  | 3 | Heavy | 208 | no |
  | 4 | Light Italic | 42 | 9° |
  | 5 | Regular Italic | 125 | 9° |
  | 6 | Heavy Italic | 208 | 9° |

- For each glyph record: **before** (point structure + key coordinates),
  **operation** (what moved/was added/deleted, and the rule used to derive
  it — e.g. "tail shortened to 60% of original length"), **after**, and
  the **compatibility check** (same point count/order in all masters).
- Prefer *rules* over raw deltas ("terminal cut at y=520, angle follows
  stroke" transfers to Nunito Sans's different outlines; "move point 12 by
  (−18, 40)" does not). Record both when possible.
- Affected composites/related glyphs (accented forms, small caps if any)
  are listed per glyph — the same edit or component update must cover them.
- Status flags: ☐ not started · ◐ in progress · ✅ done (all masters) ·
  🔁 replayed on Nunito Sans.

## Edit order (easiest first)

l → f → J → Q → G → K/k

---

## 1. l (lowercase L) — shorter tail ✅ (2026-07-06)

**Intent:** reduce the foot/tail. ⚠️ The tail is Nunito's main
`l` / `I` / `1` disambiguator — shorten, don't remove; test `Il1` adjacent
at ~10px before committing.

**Composites using `l` (all verified OK, they reference the component so
they picked the edit up automatically):** fl, lacute, lcaron,
lcommaaccent, ldot, ldotbelow, lj, llinebelow, lslash.

**Script:** `sources/edits/01_l_tail.py` (run once; asserts structure).

### Structure (identical in all 6 masters)

One closed path, 26 nodes. Node 14 = stem bottom-right junction
(x = stem right edge at tail height) — the **pivot**. Tail region =
nodes 0–13 (terminal cap + inner sweep) + 23–25 (outer bottom curve).
Nodes 15–22 = stem sides + rounded top cap.

### Operation / rule

**Compress the tail region horizontally toward the pivot by FACTOR = 0.6**
(`x' = pivot + 0.6·(x − pivot)`, applied only to tail nodes with
x > pivot; y untouched). Shrink advance width by the tail tip's retreat
(`width' = width − (tip − tip')`). Move anchors `bottom` and `dot` by the
same rule (they sit in the tail zone / right sidebearing); leave `top`,
`topright`, `center`.

Why this works: the map is affine in x, so collinearity — and therefore
every SMOOTH joint — is preserved exactly. The terminal cap gets ~40%
narrower horizontally but keeps its full stroke height, which reads as
"same terminal, shorter tail".

### Per-master numbers (pivot / tip old→new / width old→new)

| Master | pivot | tip | width |
|---|---|---|---|
| ExtraLight | 127 | 269→212 | 275→218 |
| Bold | 190 | 318→267 | 319→268 |
| Heavy | 252 | 363→319 | 364→320 |
| ExtraLight Italic | 111 | 233→184 | 275→226 |
| Bold Italic | 179 | 287→244 | 319→276 |
| Heavy Italic | 247 | 340→303 | 364→327 |

Tail extent beyond stem: EL 142→85 · Bold 128→77 · Heavy 111→67 units.

### Compatibility & size-ramp check
- [x] Same point count/order in all masters — only coordinates changed;
      fontmake build clean
- [x] `Il1` distinct at 10px (proof sheets: Regular + Bold ramp 10–28px,
      Heavy @72, Italic @84 + 12px)
- [x] lcaron: caron offset is baked (x=177 EL), NOT anchor-driven — checked
      visually, still sits correctly; no edit needed
- [ ] Nunito Sans replay notes: find the same stem-junction pivot node in
      its `l`; if its node structure differs, only the pivot/indices need
      re-deriving — FACTOR 0.6 and the width/anchor rules carry over.
      NB Nunito Sans's l tail may already be shorter/straighter — compare
      before applying blindly.

---

## 2. f — downturned top terminal ✅ (2026-07-06)

**Intent:** top curves back **down**, but slightly.

**Related glyphs — IMPORTANT finding:** `fl` and `fl.ss02` are components
of `f` (inherit automatically), but **`fi` is drawn separately** and
carries its own copy of the hook — it must be edited too. `florin` (ƒ)
has a *different* terminal construction (flat ball cap) and was left
stock. No `longs`/`ffi`/`ffl` in the font.

**Script:** `sources/edits/02_f_terminal.py` (+ shared
`sources/edits/lib.py`). Run once; locates the terminal by pattern.

### Structure / locator (works in both f and fi)

The terminal is a 7-node motif; find every match, keep the one whose cap
control sits highest (abs. y-max is unreliable — fi's i-dot can be the
tallest point in heavy masters):

| offset | type | role |
|---|---|---|
| p | curve smooth | **pivot** — hook-underside neck |
| p+1 | line smooth | underside end of terminal |
| p+2, p+3 | offcurve | cap controls (p+3 ≈ tip) |
| p+4 | curve smooth | topside end of cap |
| p+5 | line smooth | topside neck |
| p+6 | offcurve | first handle of the long top curve |

In `f`: p = node 16 (all 6 masters). In `fi`: p = node 21.

### Operation / rule

**Rotate nodes p+1 … p+6 clockwise by 12° about node p.** Rotation is an
isometry with the pivot on the incoming smooth chain, so every SMOOTH
joint survives exactly; the long top curve reshapes smoothly via the
rotated p+6 handle. No width or anchor changes (the f terminal already
overhangs the advance; the overhang grows a little — checked in
fluff/offer/fjord strings, no collisions).

Pivots / tip-x drift (f): EL (269,670) 324→331 · Bold (332,615) 402→421 ·
Heavy (381,564) 478→509 · same pattern italics. fi within 1–2 units of f.

### Compatibility & size-ramp check
- [x] Same point count/order in all masters — rotation only
- [x] fi edited to match; fl/fl.ss02 inherit via components; florin
      deliberately stock
- [x] No collision in fluff / offer / fjord at Regular, Heavy, Italic
- [ ] Nunito Sans replay notes: check whether its fi is also drawn
      separately; its straight-cut terminal may need the angle re-judged
      by eye (12° chosen against Nunito's round terminal).

---

## 3. J — upturned bottom terminal ☐

**Intent:** bottom curves back **up** (hooked foot), not a plain straight
descender.

**Related glyphs to check:** Jcircumflex, IJ, and lowercase `j` (decide:
matching hook or leave as-is — record the decision here).

### Before (per master)


### Operation / rule


### After (per master)


### Compatibility & size-ramp check
- [ ] Same point count/order in all masters
- [ ] Nunito Sans replay notes:

---

## 4. Q — slashed tail ☐

**Intent:** tail crosses *through* the bowl (slashed/crossing-tail Q)
rather than sitting outside/below it.

**Related glyphs to check:** none expected (Q has few composites); check
`Qsmall`/small-cap forms if present.

### Before (per master)


### Operation / rule


### After (per master)


### Compatibility & size-ramp check
- [ ] Same point count/order in all masters
- [ ] Counter stays open at ~10px (tail must not clog the bowl)
- [ ] Nunito Sans replay notes:

---

## 5. G — rebuilt on O's bowl ✅ (2026-07-06, done 3rd)

**Intent (refined by user):** G is based on **O** — full round bowl — with
the horizontal bar at the same height as the original G and the upper-arm
terminal (top overhang) ending in the same place as the original G.

**Composites (inherit automatically):** Gbreve, Gcaron, Gcircumflex,
Gcommaaccent, Gdotaccent, Gmacron.

**Script:** `sources/edits/03_G_bowl.py`.

### Key insight enabling the graft

Nunito's G and O **share a skeleton**: G's outer top/left is O's outer
top/left within ≤9 units (exact in ExtraLight). So the new G can be
assembled from verbatim pieces with only two computed joins.

### Assembly (44 → 35 nodes, single path, original traversal order)

1. **G bar left-end U** (G nodes 10–16) — verbatim; bar height and left
   end unchanged by construction.
2. Bar underside LINE right to **corner B** = O's *inner* right arc split
   (de Casteljau) at the bar's underside y.
3. Down O's inner right (split remainder) → O inner bottom/left/top
   nodes verbatim.
4. **G arm inner + terminal cap + outer top** (G nodes 29–37) — verbatim;
   terminal ends where it always did. Junction at inner top works because
   both curves are horizontal (y=672) there.
5. Outer left grafted **at O's node** (G's ≤9 units away, tangent shared)
   → O outer bottom verbatim → rising right arc to **corner A** at the
   bar's *top* edge y. Upright quirk: O's right extremum sits ~1 unit
   below the bar top → A is the extremum nudged up, no split. Italics:
   real split (their extremum is higher, y≈416).
6. LINE left along the bar top back to start. A and B are true corners
   (non-smooth); every other joint keeps SMOOTH exactly.

### Metrics & classes

- Width := O's width per master (718→751 / 736→785 / 754→820; italics
  same). LSB unchanged; RSB now O's.
- Anchors top/bottom := O's (bowl recentered) — composites follow.
- **rightKerningGroup G → O** (right side is now O's round bowl; left was
  already O).

### Compatibility & size-ramp check
- [x] Same 35-node structure in all masters; fontmake clean
- [x] Overlay + EL/Regular/Heavy @200px + Google/GIGA/OGRE context +
      italics all verified visually
- [ ] Nunito Sans replay notes: verify its G/O also share the skeleton
      (assert tolerances in the script will tell); bar-node indices may
      differ — the script's semantic asserts locate drift immediately.

---

## 6. K / k — notched joint, not a chevron ☐

**Intent:** Nunito's K is single-junction (arm and leg meet the stem at one
point — a chevron). Change to a **notched joint**: arm meets the stem, leg
branches off the **arm** a short distance out from the stem, opening the
crotch. Tune branch distance to taste. Apply identically to `k`.

**Related glyphs to check:** Kcommaaccent, kcommaaccent, kgreenlandic;
Cyrillic К/к if drawn (they often reuse the same joint construction).

### Before (per master)


### Operation / rule
- Branch distance chosen: ___ units (record as % of arm length too, for
  the Nunito Sans replay)

### After (per master)


### Compatibility & size-ramp check
- [ ] Same point count/order in all masters
- [ ] K and k joints visually matched
- [ ] Nunito Sans replay notes:

---

## Replay procedure (Nunito Sans → Nunuïko Display)

1. For each glyph above, read the **Operation / rule** — apply the rule to
   Nunito Sans's outlines (its coordinates differ; the rules shouldn't).
2. Nunito Sans has straight terminals — some operations may need
   re-interpretation (e.g. the `f` downturn on a cut terminal); note any
   divergence in the glyph's "Nunito Sans replay notes" line and mirror the
   final decision back here.
3. Run the same compatibility + size-ramp checks.
