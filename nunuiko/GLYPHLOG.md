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

## 1. l (lowercase L) — shorter tail ☐

**Intent:** reduce the foot/tail. ⚠️ The tail is Nunito's main
`l` / `I` / `1` disambiguator — shorten, don't remove; test `Il1` adjacent
at ~10px before committing.

**Related glyphs to check:** lacute, lcaron, lcommaaccent, ldot, lslash,
and any composites using `l` as a component; also `iota`-like Cyrillic/
Greek forms if they share the tail.

### Before (per master)
- Master 1 (Light):
- Master 2 (Regular):
- Master 3 (Heavy):
- Masters 4–6 (Italics):

### Operation / rule


### After (per master)


### Compatibility & size-ramp check
- [ ] Same point count/order in all masters (fontmake interpolation clean)
- [ ] `Il1` distinct at ~10px
- [ ] Nunito Sans replay notes:

---

## 2. f — downturned top terminal ☐

**Intent:** top curves back **down**, but slightly.

**Related glyphs to check:** f_f/fi/fl/ffi/ffl ligatures, florin,
f-composites; `longs` if present.

### Before (per master)


### Operation / rule


### After (per master)


### Compatibility & size-ramp check
- [ ] Same point count/order in all masters
- [ ] Ligatures updated to match
- [ ] Nunito Sans replay notes:

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

## 5. G — wider, more curve before the horizontal stroke ☐

**Intent:** widen G with more of a curve before the horizontal bar.

**Related glyphs to check:** Gbreve, Gcircumflex, Gcommaaccent, Gdotaccent;
spacing/kerning against O/C classes (widening may change sidebearings —
record kerning class changes too).

### Before (per master)


### Operation / rule


### After (per master)


### Compatibility & size-ramp check
- [ ] Same point count/order in all masters
- [ ] Kerning classes still correct after width change
- [ ] Nunito Sans replay notes:

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
