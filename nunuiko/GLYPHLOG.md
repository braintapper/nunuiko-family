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

**Follow-up 1c (2026-07-07):** shortening l reduced its advance, but the `fl`
composite (f + l) kept its old advance — ~44-57u of dead space after the l
(seen in `fl` and typed `ffl`, which has no glyph and renders as f + fl liga).
Fixed fl advance to (l offset + l advance) per upright master: EL 581→524,
Bold 683→632, Heavy 787→743. Script `sources/edits/01c_fl_width.py`. fl.ss02
(uses l.ss02, untouched) and fi (outlines) were already fine.
Italic fl got the same fix once italics were unfrozen: EL-I 581→532,
Bold-I 683→640, Heavy-I 787→750.

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

**Refinement 1b (user feedback):** the compression squashed the tip's
top-right corner arc (nodes 5→6,7→8) to 0.6 of its x-extent — visibly
sharp. After compressing, restore that arc's x-extent to
**min(original, 0.65 × the new cap-top span 5→11)** — the cap keeps the
top edge from degenerating in the heavy masters, whose corner is too big
to fit whole (Heavy 40→29, Heavy It 33→23; EL/EL It get their full
original 17/11 back; superseded by 1d's 0.8 cap). Control 7 keeps its original x-offset from node 8
scaled by the same ratio, control 6 stays on node 5's vertical, and
top-edge controls 9,10 sit at their original fractions of the 8→11 span.
In 1b, y never changed (1d now lifts 10–12 by 1–3 units); the 4-5-6
vertical and 10-11-12 horizontal collinearities survive exactly. Folded into the main script — a single
run of 01 produces the final tail.

**Refinement 1d (2026-10-15, user feedback: the corner was still a little
sharp next to Nunito's):** two causes, both fixed in the same script.
(1) The 1b cap (0.65) still clipped Bold's corner (24→21, tightest radius
11.2 vs Nunito's 12.8). The cap is now **0.8**, so every master gets
Nunito's full corner except Heavy (40→35) and Heavy Italic (33→28), both
above 700. (2) Nunito's top edge dips 2–4 units from the corner end (node 8)
to node 11 over ~30 units. Squeezed into the shortened 8–12-unit span, the
dip left node 8 standing proud as a small nub. Rule: **scale the drop by
the span ratio** `(x8'−x11')/(x8−x11)` and lift node 11 and its horizontal
handle 12 (and control 10, level with 11) to `y8 − round(drop × ratio)`.
Drops are now EL 2→1, Bold 2→1, Heavy 4→1, EL It 4→2, Bold It 3→1,
Heavy It 2→1. Control 9 sits on the 7→8 tangent so node 8 stays smooth.
In Bold, integer rounding still leaves a ~6° tangent break across a
2-unit handle there, as before. Tightest corner radius now matches Nunito
in EL, Bold, EL It and Bold It.

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

## 3. J (capital) — upturned hooked foot ✅ (2026-07-07, done 5th)

**Intent:** U-hook foot per **Google Sans Flex** reference — stem down,
around the bowl, back **up** the left side, ending in a rounded cap.
**Lowercase `j` is CANCELLED** (user decision: stock j is fine — do not
touch it, here or in the Nunito Sans replay).

**Composites (inherit automatically):** IJ, I_J.loclNLD,
Iacute_J.loclNLD, Jcircumflex, Je-cy, LJ, NJ.

**Script:** `sources/edits/05_J_hook.py` (22 → 26 nodes).

### Operation / rule

Full reconstruction of the foot; stem + top cap (old nodes 3–11) kept
verbatim but **shifted right by δ** — because the J is also **widened**:

- **Advance width = 0.66 × U's width** (user spec — the original bowl
  was far too narrow for the font's proportions): 297→475 (δ=178) /
  354→487 (δ=133) / 411→498 (δ=87); italics identical. All growth is
  bowl-side: hook outer-left keeps the old leftmost extent
  (−11/−14/−16; italics ≈−51 deslanted) → LSB and RSB both preserved.
- Inner bottom y = old inner-bottom y (36/100/164) → keeps Nunito's
  existing bottom taper. Outer bottom = old overshoot (−2/−5/−7).
- **Hook weight = min(stem weight, 0.55 × left span)** — with the wider
  bowl, EL and Bold now fit the full stem weight (42/128); Heavy is
  capped 215→133.
- **Terminal height H = 0.9 × stem curve-start y** (EL 159 / Bold 179 /
  Heavy 199); rounded terminal cap = same construction as the stem's own
  top cap (rise = hook weight / 2, kappa 0.5523 quarter arcs) — corners
  stay in Nunito's rounded vocabulary (user requirement).
- Italics: landmarks deslanted by tan 9°, built upright, reslanted.
- Anchors: top follows the stem (+δ); bottom recentered on the bowl.

### Composites (widening propagation — replay this too!)

IJ, I_J.loclNLD, Iacute_J.loclNLD, Je-cy, LJ, NJ: **width += δ** (their
J component offsets stay — growth is inside J's box, left of the stem).
Jcircumflex: width += δ **and** its circumflexcomb.case transform
tx += δ (the accent must track the shifted stem; some layers carry the
transform once, some twice incl. background).

### Compatibility & size-ramp check
- [x] 26 nodes, same order/types, all 6 masters; fontmake clean
- [x] JU proportion pairs at 200/400/1000; Ĵ accent centered; context
      Jump/Justice/IJssel/JOJO/NJ verified upright + italic
- [ ] Nunito Sans replay notes: same landmark-based construction should
      port directly; re-judge H_FRAC / HOOK_MAX_FRAC / WIDTH_FRAC_OF_U
      by eye; hyphenated glyph names are quoted in the .glyphs file
      (lib.py handles both).

---

## 4. Q — Jost-style slash ✅ (2026-07-06, done 4th)

**Refinement 4e (user feedback, 2026-07-07, accepted):** lengthened the slash
a further ~13u each end. First applied at ExtraLight only from the user's SFD
(cap deltas (11,-7)/(-9,10)); then **reformulated as a geometric rule**
(2026-07-07, when building italics) so it applies in every master, upright and
slanted: slide each rounded cap (nodes 0-6 / 7-13) rigidly outward along the
slash's own axis by EXTEND_FRAC (0.05) of its length. ExtraLight upright is
skipped (keeps the exact accepted SFD values); the fraction is calibrated to
reproduce that same ~13u, so Bold/Heavy upright + all 3 italics come out
consistent (slash bbox diag now 367/453/518 upright, 394/470/517 italic).
Script `sources/edits/04e_Q_slash_lengthen.py`. Rigid cap translation, no node
count change -> interpolation-safe. The
Q **bowl** is the shared `O` component — the user's SFD also fattened it ~14u
but that was NOT applied (same untractable bowl reshape reverted on G; would
change O everywhere).

**Intent (refined by user):** straight slash crossing the bowl at the
bottom right, reference **Jost**. Originally baseline-aligned (slash
bottom at y = 0, no descender); **refinement 4d lengthened it so it now
dips slightly below the baseline** — see 4d. Still far short of the old
swash's −276 (Heavy Italic), so line fitting stays tight.

**Structure discovery:** Q = `O` component + `_part.Qtail` component
(used only by Q) — the entire edit lives in `_part.Qtail`
(12 curved nodes → capsule, 14 nodes).

**Refinement 4b (user feedback):** flat Jost corners looked out of place —
corners filleted with r = 0.18 × slash weight. **Superseded by 4c.**

**Refinement 4c (user feedback):** slash ends made **fully round** —
semicircular caps like the font's other terminals, so the slash is a
capsule/stadium (two quarter-arc cubics per cap, tension 0.5523; 14
nodes). Ink extents preserved from 4a/4b: the outer cap's *center* is
solved so the circle is tangent to y = 0 exactly (no post-shift needed),
and the inner cap center is pulled back by w/2 so the round tip's ink
ends where the flat end used to. Folded into the main script — a single
run of 04 produces the round-cap slash.

**Refinement 4d (user feedback):** slash lengthened **10% at each end** —
after the 4c caps are placed, both cap centers are pushed outward along
±d by `EXTEND_FRAC (0.10) × tip-to-tip length`. The outer tip now dips
below the baseline (EL ~13 units, more at heavier weights) and the inner
tip reaches deeper into the counter. Guard asserts the inner tip stays on
the ring side of the counter center so the counter never closes. Folded
into the script (single run of 04 produces the final slash).

**Script:** `sources/edits/04_Q_slash.py`. All geometry derived from O's
outlines per master:

- **M** = midpoint of the outer & inner bottom-right arc midpoints
  (ring midline at ~4:30); **w_ring** = distance between them.
- **Direction** 45° down-right; sheared by tan 9° for italic masters.
- **Slash weight** = min(w_ring, 0.6 × counter radius) — the cap is the
  key Heavy fix: at full ring weight the slash swallowed the counter and
  barely poked out. EL/Bold use ring weight (42/123); Heavy capped
  204→104, Heavy Italic 204→96. NB slash weight is non-monotonic
  Bold→Heavy — visually fine, interpolation clean.
- **Outer cap** center starts on the slash midline at y = w/2 (tangent
  to the baseline), then pushed out by 4d.
- **Inner ink tip** = inner-arc midpoint + 0.35 × counter radius along
  −d (cap center w/2 short of that), then pushed in by 4d.
- **4d extension** = 0.10 × tip-to-tip length added at each end.
- Winding matched to O's outer ring (else nonzero fill cancels the
  overlap); rect corners converted to part-local space via Q's
  per-master component offset. Same node order in all masters
  (interpolation-safe — verify the orientation flip decides identically
  everywhere when replaying).

### Compatibility & size-ramp check
- [x] Same 14-node capsule structure, same order, all masters
- [x] Counter stays open at all weights incl. Heavy/Heavy Italic (incl.
      the deeper 4d inner tip; guard assert in the script)
- [x] 4d slash length/dip verified against baseline guide at 200/700/1000
      upright + italic (outer tip dips below, inner reaches deeper)
- [ ] Nunito Sans replay notes: check whether its Q is also
      O + _part composite; re-judge MAX_COUNTER_FRAC by eye (its
      counters differ).

---

## 5. G — rebuilt on O's bowl ❌ REVERTED to stock (2026-07-07)

**Reverted to stock Nunito.** Edits 3 + 3b (O-bowl rebuild, bar fillet) and a
later attempt 3c (fuller right bowl from the SFD) were all dropped — the SFD's
bowl reshape is drawn with more nodes than the source topology holds, so it
couldn't be reproduced without junction kinks or a large residual, and the
user judged it not worth it. G restored by splicing its glyph block from
pre-edit-3 commit `104bb3b0`; scripts `03_G_bowl.py`, `03b_G_corner.py`,
`03c_G_bowl_right.py` deleted (recoverable from git). Original intent below,
kept for the record.

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

**Refinement 3b (user feedback: corner A too sharp):**
`sources/edits/03b_G_corner.py` replaces corner A with a fillet whose
radius = the bar left-end's own corner rounding (r = barTopY − leftU
cornerY, read per master: EL 19 · Bold 47 · Heavy 74 · italics 22/54/86),
so it matches the font's corner vocabulary and scales with weight
automatically. Fillet controls at 55% tension toward the old corner.
35 → 38 nodes. Corner B (inside the counter, underside) left sharp —
it reads as the bar tucking into the bowl. **Replay order: 03 then 03b.**

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

## 6. K / k — notched joint, not a chevron ❌ REVERTED (2026-07-07)

**Reverted to stock Nunito.** The notch (edit 6) plus a later crotch-collapse
attempt (edit 7) proved fiddly across the weight axis and not worth it. K, k,
and kgreenlandic were restored to their original Nunito outlines by splicing
those three glyph blocks from commit `8772e0d6` (pre-edit-6); edits 1–5
(l/f/G/J/Q) were untouched. Scripts `06_K_notch.py` and `07_K_crotch.py`
deleted (recoverable from git history). Original design intent below, kept
for the record.

**Intent:** Nunito's K is single-junction (arm and leg meet the stem at one
point — a chevron). Change to a **notched joint**: arm meets the stem, leg
branches off the **arm** a short distance out from the stem, opening the
crotch. Apply identically to `k`.

**Related glyphs:** Kcommaaccent/kcommaaccent are composites of K/k —
inherit automatically. **kgreenlandic** shares k's exact 34-node topology —
edited by the same script (added to its glyph loop). **Ka-cy/ka-cy have a
different construction** (35/34 nodes, different type sequence — curled
leg) — left stock; would need their own rule if desired.

**Script:** `sources/edits/06_K_notch.py` (K, k, kgreenlandic in one run).

### Operation / rule

Key discovery: the **heavy masters are already notched** (fat strokes can't
converge at one point) — Bold sits at frac 0.25–0.39, Heavy at 0.45–0.67.
So the rule is a *floor*, not an offset: move the crotch vertex out along
the arm-bottom line to **max(current, 0.25) of the arm's horizontal run**
(measured from the stem-right ∩ arm-bottom intersection S to the arm tip).
Masters already at/past the floor are untouched — the light masters simply
catch up to the design logic the heavy ones already had.

Per glyph, per master (34-node topology, K and k and kgreenlandic
identical): crotch vertex = node 13; leg foot cap = nodes 5–11; notch face
= edge 12→13 (Nunito's little perpendicular cut, preserved verbatim but
rotated with the leg).
1. node 13 → floor position on the arm-bottom line.
2. Leg pivots **rigidly about its foot-cap center**; rotation angle solved
   by fixed-point iteration so the leg's top edge passes through the new
   node 12 — stroke width and cap shape preserved exactly.
3. node 12 = new 13 + rotated original face vector.
4. node 4 = rotated leg bottom edge ∩ arm-bottom line.
5. node 3 = stem right edge ∩ arm-bottom line (S).
Pure line/intersection/rotation geometry — works unchanged in slanted
(italic) space.

### Changed masters (others already ≥ 0.25)

| Glyph | Master | frac | crotch (13) | leg rotation |
|---|---|---|---|---|
| K | ExtraLight | 0.05→0.25 | (158,342)→(239,414) | −12.5° |
| K | ExtraLight Italic | 0.06→0.25 | (178,339)→(266,408) | −13.9° |
| k | ExtraLight | 0.10→0.25 | (154,231)→(198,270) | −10.1° |
| k | ExtraLight Italic | 0.09→0.25 | (149,225)→(200,266) | −12.2° |
| ĸ | ExtraLight | 0.10→0.25 | (154,231)→(198,270) | −10.1° |
| ĸ | ExtraLight Italic | 0.09→0.25 | (149,225)→(200,266) | −12.2° |

Unchanged fracs — K: Bold 0.25, Heavy 0.45, Bold It 0.27, Heavy It 0.48;
k/ĸ: Bold 0.37, Heavy 0.63, Bold It 0.39, Heavy It 0.67.

### Compatibility & size-ramp check
- [x] Same 34-node count/order in all masters; fontmake clean
- [x] K, k, ĸ joints visually matched at 200/1000, upright + italic
- [x] 10px legibility strip (Kick KLERK kayak) at 200/400/1000
- [ ] Nunito Sans replay notes: run the script as-is (asserts will catch
      topology drift); re-check whether its heavy masters are also
      pre-notched — if not, the max() floor still just works. Check its
      Cyrillic К construction separately.

---

## 8. ff / ffi / ffl — ligatures with a joined crossbar ✅ (2026-10-15)

**Intent (user feedback):** in "ff" the crossbars should join, but their
round caps met as two rounded ends. Stock Nunito has no ff ligature. Typed
"ff" is two f's pulled together by the f–f kern (−10 / −23 / −35), which
leaves a 3-unit gap at ExtraLight and an overlap with a pinched waist from
Regular up.

**Script:** `sources/edits/08_ff_ligatures.py` (run once; adds glyphs,
refuses to run if they already exist).

### Rule (per master, upright and italic alike)

- `offset = width(f) + kern(@MMK_L_f, @MMK_R_f)` (where the kerned second f
  sits: 296 / 341 / 388).
- Each glyph is a component `f` at 0, plus the second glyph as a component
  at `offset`, plus a **bridge** path: a quad from the first f's flat-bar
  right ends (f nodes 4 bottom, 10 top) to the second f's flat-bar left
  ends (f nodes 33 bottom, 27 top, + offset). Both round caps sit inside
  it, so the union is one flat bar. On italic masters the quad follows
  the slanted cap starts.
- `width = offset + width(second)`. Carets go at `offset` and at
  `offset + the second glyph's caret_1`. The left kerning group is `f`;
  the right group comes from the second glyph.

| Glyph | Second | Unicode | Right group |
|---|---|---|---|
| f_f | f | FB00 | f |
| f_f_i | fi | FB03 | i |
| f_f_l | fl | FB04 | ltail |
| f_f_l.ss02 | fl.ss02 | — | l |

Bridge x (first → second bar end): EL 275→322, Bold 308→393, Heavy
341→465, EL It 306→359, Bold It 333→422, Heavy It 359→486.

**Features:** liga gains `sub f f i by f_f_i; sub f f l by f_f_l; sub f f
by f_f;` (ahead of fi/fl), and ss02 gains `sub f_f_l by f_f_l.ss02;`. Both
features are flagged `automatic` in the source, so Glyphs.app would
regenerate the same lines from the glyph names.

`fi` is drawn, not built from `f`, so the script asserts that its bar's
left ends match f's nodes 27/33. Because `f` stays a component in all four
glyphs, later f edits carry over.

### Checks
- [x] Shaping (Regular, upright + italic): ff→f_f, office→f_f_i,
      waffle→f_f_l, waffle+ss02→f_f_l.ss02, U+FB00→f_f; liga off → f f
- [x] Build clean; proof f row now shows `ff ffi ffl`
- [ ] Visual check of the joined bar (user)

---

## 9–13. Ported from Nunuïko Display: K/k, dots, a, 1 ◐ (2026-10-16)

**Intent (user):** repeat Display's K/k, dots, a and 1 changes here. The
l stays disambiguated in Nunuïko (the UI family); only Display swapped to
the plain l (its edit 14). Rules and rationale are in
`../nunuiko-display/GLYPHLOG.md` §9–13; this entry records where
Nunito's rounded construction differs. Edit numbers match Display's.

### 9. K / k / ĸ — leg grows out of the arm (`sources/edits/09_K_leg_from_arm.py`)

The glyphs are 34-node paths: 2→3 stem right, 4→5 leg lower edge, 5–11
rounded foot cap, 11→12 leg upper edge, 12→13 notch face, 13→14 arm bottom,
14–20 rounded arm tip.

- **The leg pivots rigidly.** The foot cap rotates about its centre
  (midpoint of 5 and 11) toward a point on the arm, then shifts vertically
  so its lowest node keeps its height (overshoot). The leg edges continue
  the rotated cap ends, so 5 and 11 stay smooth.
- **Gap:** as in Display, GAP_FRAC is 0.15 (the lower edge meets the arm
  15% of the way from the stem to the tip).
- **New knob, `MAX_TURN` 12°.** A round foot can't swing far. If the full
  gap would swing the leg more than 12°, the script takes the position
  within 12° whose gap comes closest. This affects only Heavy Italic K and
  Heavy / Heavy Italic k and ĸ (they would need 33–44°), where the leg
  lands further out (gap 0.24–0.29).
- **Result, 12pt ExtraLight–Bold:** gaps of 81–84 on K and 57–61 on k; the
  leg turns 1–8°; feet move 3 units or less.

### 10. Dots — nothing to do

Nunito's dots are already circles (12-node round contours). The only
square 4-node contours in the font are edit 8's ff bridges.

### 11. a — rounder, 10% taller bowl (`sources/edits/11_a_round_bowl.py`)

Nunito's a is Nunito Sans's construction plus 7 nodes (rounded stem foot
4–10, rounded terminal 17–20), so every bowl index is Display's + 7. The
same knobs apply: BOWL_RISE 0.10, INNER_DROP 0.40, OUTER_DROP 0.22, TILT 15°.
The italic masters borrow the matching upright master's o from this file.
The numbers come out identical to Display's (the same base metrics):

| | ExtraLight | Bold | Heavy |
|---|---|---|---|
| bowl top | 303 | 320 | — |
| opening under the arch | 150 | 85 | 28 |

### 12. 1 — footless (`sources/edits/12_one_footless.py`)

- The default and ss01 outlines swap, as in Display: `one` ↔ `one.ss01`,
  `one.tosf` ↔ `one.tosf.ss01`.
- **`one.dnom`** (29 nodes, one's structure): nodes 8–20 are kept (stem
  edges, top, flag). The foot is replaced by a round stem end copied from
  the footless 1 of the same master, scaled by the stem-width ratio and
  built unslanted, giving 20 nodes like one.ss01. It is then centred with
  equal sidebearings.

### 13. 1 — proportional, footed tabular 1 (`sources/edits/13_one_proportional.py`)

Same as Display:
- RSB = I's sidebearing, LSB = 0.75 × that. Widths 600 → 392 (ExtraLight)
  and 481 (Bold).
- `one.tf` and `one.tosf.tf` are components of the footed `one.ss01` /
  `one.tosf.ss01`, 600 wide.
- A new `tnum` feature goes after onum, and ss01 maps the .tf forms to the
  footed 1.
- The Glyphs 2 format gets its own feature anchors (`name = ...`).

### Checks
- [x] All 6 masters; build clean
- [x] Shaping ("2011½"): default one 392; tnum → one.tf 600; onum+tnum →
      one.tosf.tf; ss01+tnum → one.ss01
- [x] Proof gains K, a and 1 rows (the 1 row with a tnum line)
- [ ] Visual check (user)

---

## 16. $ — no taller than the S ❌ SUPERSEDED by edit 19 (2026-10-17)

*Replaced the same day: the $ is now a full-size S with a stroke through it
(edit 19). Kept for the record.*

**Intent (user):** the $ gets the same treatment as in Nunuïkode: shrunk to
fit between the baseline and the cap height.

**Script:** `sources/edits/16_dollar_cap_height.py` (the same file in
Nunuïko and Display), run once per source.

**Operation:** the $ (an S with the bar sticking out above and below) is
scaled down uniformly until its full height, bar ends included, is the S's
own, overshoots included. Stroke weight is kept: each on-curve point also
moves out along its outward normal by (1 − s) × stem / 2, stem = the I's in
that master, handles following their on-curve point. It stays centred where it
was across, and its advance (600, tabular like the figures) doesn't change.
Done unslanted in the italic. No composite uses the $.

**Result:** −121..826 → −8..713 at ExtraLight (scale 0.750), 0.725 at Bold, 0.695 at
Heavy; italics 0.755 / 0.728 / 0.695.

### Checks
- [x] All masters compatible; build clean
- [ ] Visual check (user)

---

## 18. G — the bottom-right follows the O's bowl up to the bar ◐ (2026-10-17)

**Intent (user):** the bottom curve comes up the right side before the
straight stroke starts, keeping the shape of Nunito's G. References: Bryant
(the user's screenshot) and Proxima Nova.

**Script:** `sources/edits/18_G_rounder_bottom.py`, run once. Nunuïko first;
Display's G is back to stock until this one is right.

**How it got here (all 2026-10-17):** four versions kept the stock stem's x
and only reshaped the curve into it: the stem starting halfway up with the
O's tension; then at ~0.7 of the bar height (the top arc's proportions);
then 0.08 fuller; then the stem 20 units right of the terminal with the arc
rising to the bar. The user found each still off, and sent Bryant's G next to
ours. Measured, the difference is width: Bryant's G is an O with a gap at the
upper right, while Nunito's stem stands 55 units (ExtraLight) inside the O's
right side, so any curve into it is squeezed.

**Operation, per master** (unslanted in the italic): the G's bottom-right is
redrawn on the O's. Nunito's G already shares the O's skeleton on the left,
top and bottom (see edit 5's log).
- **Outer:** a curve from the G's outer bottom point to the O's rightmost
  point (its x and height, vertical there), with the tensions of the O's own
  bottom-right quarter, cut where it reaches the stem's top node L (where the
  bar's top-right corner starts; the O's widest point is just above, at the
  bar's top). L moves to the cut; the bar's corner moves across with it.
- **Inner:** the same on the O's inner contour, from the G's inner bottom
  point, cut at the bar's underside. The stock inner stem and its notch (a
  hidden overlap) go.
- **Even upstroke** (user: "the thickness needs to be a little more
  consistent on the upstroke", subtly): the O's sides are heavier than its
  bottom, so the stroke thickened toward the bar (Bold: 110 at the bottom, 132
  just under the bar, 144 at the corner). The inner rightmost point moves out
  so the side keeps only `SIDE` (0.5) of the O's extra side weight: Bold now
  110 → 121, 133 at the corner; ExtraLight 41 → 43 (was 45).
- **Advance** := the O's, as for Ğ Ǧ Ĝ Ģ Ġ Ḡ; top and bottom anchors := the O's.
- 44 → 38 nodes, the same in every master.

**Result:** right side 628 → 684 / 665 → 731 / 701 → 778 (ExtraLight / Bold /
Heavy), italic 590 → 636 / 628 → 682 / 666 → 729 (unslanted); advance 718 →
751 / 736 → 785 / 754 → 820. The bar, the arm and terminal, the left side and
the bottom point are unchanged. This is close to edit 5's July construction
(also on the O's bowl), which was reverted for unrelated reasons (an SFD
reshape that couldn't be reproduced), not for the shape.

### Checks
- [x] All masters compatible; build clean
- [ ] Visual check (user), then derive Nunuïkode from Nunuïko

---

## 19. $ — a full-size S with a stroke right through it ◐ (2026-10-17)

**Intent (user):** the $ is a full-size S with a full vertical stroke going
through it (replaces edit 16).

**Script:** `sources/edits/19_dollar_full_s.py`, the same file in Nunuïko and
Display, run once per source.

**Operation, per master:** the $ is rebuilt as
- the **S as a component**, at full size and with the S's advance (600 / 631 /
  663 at ExtraLight / Bold / Heavy; the stock $ was 600 in every master), so
  later changes to the S reach the $;
- **one straight stroke** as its own contour, overlapping the S: as thick as
  the stock bar (40 / 100 / 160) and reaching as far as it did (−121..826 at ExtraLight),
  centred across on the S's outline. Its ends are round, half-circles like the stock stub ends. It follows the slant
  in the italic and runs in the same direction as the S's outer contour, so
  the overlap fills.

The thickness and reach are read per master from the stock $ in git history.

### Checks
- [x] All masters compatible; build clean
- [ ] Visual check (user)

---

## 20. % — round rings ◐ (2026-10-17)

**Intent (user):** the % rings become symmetric circles instead of o-like
ovals.

**Script:** `sources/edits/20_percent_round_rings.py`, the same file in Nunuïko
and Display, run once per source.

**Operation, per master:** each ring (326 × 431 at ExtraLight) becomes a
circle as wide as it was, with an even stroke all round (the old ring's side
thickness), so the counter is a circle too. The upper ring keeps its top, the
lower ring its bottom, both keep their centre across. Each ring keeps its 12
nodes in the same order and direction, each redrawn on the circle by its role
(right, top, left, bottom). The stroke is capped so the counter is at least
0.35 × the radius (Heavy: 126 instead of the stock side thickness). The slash,
the advance and ‰ are unchanged. In the italic the circles are drawn unslanted
and then slanted.

**Result:** rings 326 / 356 / 388 across (ExtraLight / Bold / Heavy), stroke
42 / 102 / 126; italic 322 / 346 / 369.

### Checks
- [x] All masters compatible; build clean
- [ ] Visual check (user)

---

## 21. ¢ — one stroke right through it ◐ (2026-10-17)

**Intent (user):** the cent sign gets a full vertical stroke, like the $.

**Script:** `sources/edits/21_cent_full_stroke.py` (shared), run once per
source.

**Operation, per master:** a straight stroke is added as its own contour,
overlapping the c: exactly the stock stubs' thickness and reach (40 / 100 /
160 thick; −121..610 at ExtraLight), so the outline is unchanged outside the
c and the stroke now runs on through the counter. Round ends (half-circles), as the stubs have. It follows
the slant in the italic and runs in the outer contour's direction so the
overlap fills. The stubs are the on-curve nodes above x-height + 30.
(`signed_area` in edit 19, used for the direction, now uses the control
polygon: on-curve points alone can get the sign wrong.)

---

## 22. & — the arm stops a little past the diagonal ◐ (2026-10-17)

**Intent (user):** shorten the &'s right arm (the one rising from the bowl to
near the x-height) so it ends only a little past where it crosses the diagonal.

**Script:** `sources/edits/22_ampersand_short_arm.py` (shared), run once per
source.

**Operation, per master:** the arm's outer edge is cut at
y = junction + `TAIL` (0.3) × (old end − junction), the junction being the node
where the arm's inner edge meets the diagonal; the inner edge is cut where the
perpendicular to the stroke through that point crosses it. The round end is rebuilt as a half-circle across the stroke.
Nodes and types unchanged.

**Result:** outer end 387 → 229 / 375 → 261 / 362 → 293 (ExtraLight / Bold / Heavy);
junction 161 / 212 / 263.

---

## 23. R — straight leg, no transition into the bowl ◐ (2026-10-17)

**Intent (user):** no curved transition into the R's slanted leg; reference
Proxima Nova's R.

**Script:** `sources/edits/23_R_straight_leg.py` (shared), run once per source.

**Operation, per master:** both edges of the leg run straight until they meet:
the inner edge's straight part is extended up to the crotch line under the
bowl (the line's end node moves there, a sharp corner; the curve between goes),
and the outer edge's straight part is extended until it crosses the bowl's
outer curve (a sharp corner there; the bowl curve is split and its upper part
kept; the curve into the bowl and the hidden notch go). 35 → 27 nodes.
Composites follow. `lib.apply_edit` gained a `path` option so `replace_nodes`
can rewrite one path of a multi-path glyph.

**Result:** crotch at x 404 / 374 / 344 (was 295 / 300 / 305), leg meets the
bowl at (442, 326) / (502, 305) / (561, 285) (upright ExtraLight / Bold / Heavy).

---

## 24. 6 — a shorter tail ◐ (2026-10-17)

**Intent (user):** shorten the tail on the 6.

**Script:** `sources/edits/24_six_short_tail.py` (shared), run once per source,
on six, six.tosf and six.dnom (numerators, superiors and inferiors follow).

**Operation, per master:** the hook's outer edge is cut so it reaches `KEEP`
(0.7, after a first try at 0.6) as far right of the top point as before; the inner edge is cut on the
perpendicular through that point. The round end is redrawn as a half-circle (handles 4/3 × the radius).
Nodes and types unchanged.

**Result:** outer end at ExtraLight (529, 630) → (473, 676). The 9 is unchanged.

### Checks (21–24)
- [x] All masters compatible; build clean
- [ ] Visual check (user)

---

## Replay procedure (Nunito Sans → Nunuïko Display)

1. For each glyph above, read the **Operation / rule** — apply the rule to
   Nunito Sans's outlines (its coordinates differ; the rules shouldn't).
2. Nunito Sans has straight terminals — some operations may need
   re-interpretation (e.g. the `f` downturn on a cut terminal); note any
   divergence in the glyph's "Nunito Sans replay notes" line and mirror the
   final decision back here.
3. Run the same compatibility + size-ramp checks.
