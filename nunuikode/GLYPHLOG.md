# Nunuïkode change log

Record of the monospace pipeline and every code edit, precise enough to replay.
Upstream glyph changes are logged in Nunuïko's `GLYPHLOG.md`.

## 0. Monospace pipeline ◐ (2026-10-16)

`sources/build.py`, from the Nunuïko snapshot at `9f0828a3` (6 masters:
ExtraLight / Bold / Heavy, upright + italic, stems 42 / 125 / 208).

- **Cell:** `CELL` = 600, the width Nunuïko's figures already have. Zero-width
  glyphs stay zero-width: 103 of them, combining marks and ZWSP. This is decided
  once from the first master, because upstream `caron.alt` is 500 wide in one
  italic master only.
- **Glyphs that fit** in 600 − 2·`SB_MIN` (30) are moved but not reshaped, and
  centred optically. The cell centre goes halfway between the outline's box
  centre and its centre of mass, so l r j L [ ( lean toward their heavy side.
  (The first build kept the old left:right sidebearing ratio instead. That
  pushed the tailed l and the brackets to the right, since the l has almost no
  right sidebearing, and put j on different sides in Light and Bold.)
- **Wider glyphs** are condensed by
  s = (inner − COMP·stem) / (width − COMP·stem). A horizontal stroke offset then
  moves every point d = COMP·(1−s)·stem/2 along the x direction of its outward
  normal (ramped near horizontal), so vertical stems keep `COMP` (75%) of the
  weight condensing would remove. Off-curve points move with their on-curve.
  Everything is done unslanted, so the italic keeps its 9°. Anchors are moved
  and scaled the same way.
- **Composites** are decomposed first. Accent composites (base at the origin +
  zero-width marks) reuse their base's exact transform, so á, í, ĺ … sit exactly
  on a, i, l. i and j follow idotless and jdotless. All placements are resolved
  before any width changes.
- **Removed:** non-exported helper glyphs, kerning, `liga` (f-ligatures), and
  glyphsLib's `eraseOpenCorners` filter. After condensing, Nunito's overlap loops
  no longer line up across masters; they render fine as overlaps.
- **Added:** a `.notdef` box at 600 (Nunuïko has none). post.isFixedPitch = 1 and
  OS/2 panose proportion = 9.
- **Names:** "Nunuïkode" in the display name records; ASCII "Nunuikode" in
  PostScript names and file names.

Condensing per master (s = horizontal scale):

| Master | glyphs condensed | m | w | M | W | tightest |
|---|---|---|---|---|---|---|
| ExtraLight | 279 | 0.80 | 0.71 | 0.82 | 0.52 | ‰ 0.44 |
| Bold | 422 | 0.68 | 0.62 | 0.72 | 0.47 | Ǆ 0.38 |
| Heavy | 597 | 0.57 | 0.53 | 0.62 | 0.41 | Ǆ 0.32 |

W (and to a lesser degree w, m, M) is a candidate for a proper monospace
redesign.

## 1. Dotted zero ◐ (2026-10-16)

`sources/edits/01_zero_dotted.py`. Once condensed into the same cell, O and 0
are close in shape. The zero gets an upright oval dot centred in its counter
(rather than a slash, which would clash with Ø):

- width = min(1.6 × stem, 0.40 × counter width)
- height = min(1.35 × width, 0.35 × counter height)

It is built unslanted and slanted with the italic. It applies to zero,
zero.tosf and zero.dnom; zero.numr, zerosuperior and zeroinferior are built from
zero.dnom and follow.

## 2. Dieresis clears a single stem ◐ (2026-10-16)

`sources/edits/02_dieresis_clears_stem.py`. On ï Ï ї Ї and the ï/Ï with acute,
Nunuïko's ordinary dieresis sits closer as the weight rises. At Bold the gap
between the dots (66) is narrower than the stem (125), so the dots sit over the
stem's edges. Alone in a cell this reads as a misplaced accent. Each dot moves
outward until it clears the stem by 0.3 × stem + 13 (ExtraLight 26, unchanged;
Bold 51). It goes no further than 15 units from the cell edge, so Heavy only
just clears.

## 3. Footed 1 and i ◐ (2026-10-16)

`sources/edits/03_footed_one_and_i.py`. The narrow 1 and i get a horizontal foot
to fill their cell.

- **1:** the stock footed 1 becomes the default. one/one.tosf swap contents
  with one.ss01/one.tosf.ss01, so ss01 now gives the footless 1. `tnum` is
  dropped in build.py: every figure is 600 already. Fraction, super and
  subscript 1s stay footless.
- **i:** i and idotless (so ı í ì ï … too) stand on a foot copied from the
  footed 1 of the same master: same thickness and length (at most 540, so the
  i is never condensed), centred on the stem, with round ends. The stem's
  rounded bottom is replaced by the foot; the top is kept. Each is one contour
  with the same structure in every master. į (drawn with the ogonek merged into
  the stem) and j keep their plain form.

## 4. Texture healing ◐ (2026-10-16)

`sources/build.py` (`heal_sets`, `add_healing`, `healing_features`), as in
Monaspace. Cells stay 600; only the outlines move.

- **Wide letters:** letters that monospace condenses below 0.9 at ExtraLight
  (`WIDE_S`): A M O Q V W m w, plus their accented and look-alike forms,
  163 glyphs. Each gets .texl / .texr / .texb alternates, condensed less and
  extending `HEAL` (60) units past the cell on the left, right or both sides.
- **Narrow letters:** letters whose proportional advance is at most 0.6 × n's
  (`NARROW`): I f i j l r t and their forms, 73 glyphs (ss01/ss02 alternates
  count by base name). Each gets .texl / .texr, shifted up to 60 units into its
  own spare space. At Bold the footed i only has room for 44.
- **calt rules** pick the alternates by neighbour. A narrow letter lends to one
  neighbour only, so in "mim" the second m stays plain. The rules run after
  every other substitution.
