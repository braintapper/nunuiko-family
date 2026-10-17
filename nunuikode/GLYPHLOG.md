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
  rounded bottom is replaced by the foot.
- **i flag:** a horizontal arm runs left from the stem top. It has the foot's
  thickness and round end, its top is flush with the old cap's top, and it
  reaches 0.7 × the foot's reach from the stem centre (`FLAG`), so it stops
  short of the foot. The top right corner keeps the old round cap. At Heavy
  only the round end sticks out.
- **l:** Nunuïko's tailed l keeps its curved bottom and gets the i's flag (same
  thickness and round end) in place of the left half of its top cap. ĺ ľ ļ ŀ ḷ
  ḻ ł lj follow. The ﬂ/ﬄ ligature characters are frozen first and keep the
  unflagged l, since the flag would hit the f's hook. Like the i's foot, the l
  spans the foot's length centred on its stem: the flag reaches the foot's full
  reach to the left (`FLAG_L` = 1.0, against the i's 0.7), and the tail is
  stretched horizontally out to the foot's reach on the right, so the curve
  keeps its shape. With Nunuïko's short tail and flag the l was a bare stem in
  its cell: "ll", "cl" and "el" set far looser than "il". Now the l's stem
  sits where the i's does, and ll, il, li and ii are within 10 units of each
  other (232 / 227 / 237 / 232 at ExtraLight; ll was 366). (Tried first: the
  tail alone at 1.3 × and 1.6 ×, which left ll 40–55 looser.) ss02 is
  unchanged: Nunuïko's plain l. (Briefly the plain l with the i's foot and
  flag became the default, with the tailed l in ss02; reverted the same day.)
- **r:** rebuilt from the n of the same master: the n's stem and arch, the
  arch cut 0.55 of the way down its descent (`ARCH`; both edges split at the
  same curve parameter) and ended with a round terminal, so the arm arches
  down like the n's shoulder. The cut ends around 410–440 at ExtraLight and
  330–440 at Bold (x-height 486). The top anchor goes over the arch (the n's);
  the bottom one stays under the stem. Nunuïko's r is the narrowest lowercase
  letter and set loose alone in its cell (mirror, array, error); it now spans
  143–535 at Regular (was 193–469). ŕ ř ŗ follow. In the cell it is placed exactly
  like the n (`ALIGN` in build.py), so its stem lines up with the n's left stem
  and "mirror" keeps the rhythm of "minnow": optical centring had put it 72
  units right of the n at Regular, crowding its arm into the next letter.
  (Tried first the same day: the i's foot, too heavy; then the old arm
  stretched 1.4 ×.) (2026-10-17)
- **I:** the stem gets equal bars at the baseline and at the cap height, each
  exactly the i's foot (thickness, length, round ends) and centred on the stem.
  Accented I's, І, Ї and Ӏ follow. Ĳ and its Dutch forms are frozen first and
  keep the plain I, since two letters already share the cell. Į keeps its
  plain stem, as į does. Each is one contour
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
  neighbour only, so in "mim" the second m stays plain. It lends only when its
  other neighbour isn't narrow too; otherwise stepping aside pinches it against
  that letter (the i against the l in "will", and against the t in "limit").
  So will, William, limit and wild don't heal; minimum, mim and Wiki do. The
  rules run after every other substitution.

## 5. Wider spacing for capitals ◐ (2026-10-16)

`SB_CAP` = 60 in `sources/build.py`: capital letters (Lu/Lt and their
alternates) keep at least 60 units each side instead of `SB_MIN`'s 30. At 30,
condensed capitals (H N D O M T U …) sat 60 units apart, so all-caps words like
FROM, WHERE and JOIN set far tighter than lowercase (two n's are 142 apart at
Bold). Now capitals sit at least 120 apart. The widest capitals condense a
little more for it (M 0.82 → 0.73 and W 0.52 → 0.46 at ExtraLight), and their
stems are thickened back as before. More capitals now fall under the 0.9
texture-healing threshold, so the wide set grows to A C D G H M N O Q T U V W X
Y m w (269 glyphs).

## 6. Brackets centred on the capitals ◐ (2026-10-16)

`sources/edits/04_brackets_centred.py`. Nunuïko's ( ) [ ] { } | ¦ hang from
the cap height, with their bottoms 180–220 below the baseline, so in code
(x), [0] and {} sat low next to the letters. Each now moves up until the
middle of its height is at half the cap height (352.5), along the slant on the
italics: parentheses run −97 to 801 at Regular (were −186 to 712), square
brackets and braces −90 to 795. Cascadia Code does the same (−98 to 791 on a
693 cap). The angle brackets ⟨ ⟩ were already centred.

## 7. Lower middle peak on W ◐ (2026-10-17)

`sources/edits/05_w_middle_lower.py`. Nunuïko's W has its middle peak at the
full cap height, level with the outer stems; condensed into the cell, the four
strokes crowd together at the top. The middle peak (its round top and the
notch under it) moves straight down by 0.3 × the cap height (212 units; first tried at 0.06, 42 units), along
the slant on the italics. Ŵ Ẁ Ẃ Ẅ and the healing alternates follow.

## 8. @ on the baseline, round % rings, shorter $ ◐ (2026-10-17)

`sources/edits/06_at_percent_dollar.py`.

- **@:** Nunuïko's @ hung 160 below the baseline (−162 at ExtraLight against
  the O's −9). It was squashed vertically onto the O's height (0.82 at
  ExtraLight, 0.79 at Bold), and each on-curve point moves out along its
  normal by half the thickness lost, so the strokes keep their weight.
  *Superseded by §11: the squash left it to be condensed across into a narrow
  oval; it is now fitted to the cell and centred like © and ®.*
- **%:** the two rings were tall ovals (231 × 431 at ExtraLight). Each is
  redrawn as a circle 0.4 × the cap height across (282), with the old ring's
  side and top/bottom thickness: the upper one in the top-left corner, top on
  the O's top, the lower one in the bottom-right, bottom on the O's bottom. The
  slash is unchanged and the glyph is made 540 wide, so it is no longer
  condensed. At Heavy the thickness is capped so a counter stays. ‰ is
  unchanged.
- **$:** Nunuïko's $ is an S with the bar sticking out 115 above and below it.
  It is scaled down uniformly (0.75 at ExtraLight, 0.73 at Bold), weight kept
  as on the @, until its full height, bar ends included, is the S's. The S in
  it is now smaller than a regular S.

## 9. Lowercase side white: widen and balance ◐ (2026-10-17)

`sources/build.py` (`opening`, `side_profile`, `side_white`). Nunuïko's
mid-width letters are narrower than letters drawn for a cell: measured as the
mean white per scanline across the x-height (each side at most half a cell
deep), r t v k z c s y had 1.5–2.5 × the n's white at Regular, against 1.0–2.0 ×
in Cascadia Code. So mirror, array, remove and remote set with holes.

- **Widen:** a lowercase letter whose tighter side still has more than 1.45 ×
  the n's white (`OPEN`) is widened until it doesn't, by at most 1.3 ×
  (`OPEN_MAX`), its stems thinned back like condensed letters are thickened.
  Judging by the tighter side keeps r and c from widening for the hole under
  the arm or in the mouth, which widening can't close. At Regular: v y x
  1.06–1.10, s 1.19–1.30, z 1.25–1.30 (ExtraLight–Bold).
- **Balance:** each lowercase letter then moves 75 % (`BALANCE`) of the way to
  equal white each side: c went from 111 / 208 (left / right) to 174 / 211 at
  Regular.
- i j l t f are left out: their edits shape them for the cell. r is placed
  like the n instead (balancing pushed its arm into the next letter).

## 10. Wider t and f crossbars; f top arched like the n ◐ (2026-10-17)

`sources/edits/07_t_and_f.py`.

- **Crossbars:** each end of the t's and f's bar reaches 1.3 × as far from the
  stem (`BAR`), stretched so the round ends keep their shape; cut back when the
  letter would overflow the cell (f at Bold: 1.01).
- **f top:** the hook is redrawn as the n's arch, like the r: the stem rises
  into the n's inner curve, the arch is cut 0.55 of the way down its descent
  (`ARCH`) and ends in a round terminal, and the outer edge comes back over on
  the n's outer curve, then down to the stem on a quarter ellipse. The top stays
  at the old f's height. The terminal ends around 640–665 at ExtraLight and
  595–665 at Bold (top 720), where Nunuïko's ended flat.

## 11. Round © and ®, and the @, centred on the capitals ◐ (2026-10-17)

`sources/edits/08_copyright_registered.py`.

- Both were circles wider than the cell, so the monospace step condensed them
  across only, into tall ovals (540 × 725). They are now scaled down
  uniformly to fit the cell, 538 wide (`WIDTH`), so the monospace step only
  moves them. Stroke weight is kept as on the $ (edit 8). The scale is
  0.73 / 0.69 / 0.63 (ExtraLight / Bold / Heavy) upright.
- They are centred on half the cap height: 84..622 upright, a 538 circle.
  The italic keeps Nunuïko's italic proportions, about 538 × 496 unslanted
  (102..603).
- **@** (same day): edit 6's vertical squash is removed and the @ gets the
  same treatment, scaled uniformly to 538 wide (0.65 / 0.58 / 0.49 upright,
  ExtraLight / Bold / Heavy), weight kept, and centred on half the cap height:
  62..643 at ExtraLight, 81..624 at Heavy. It no longer drops below the
  baseline and is no longer condensed. The edit would also cap the height at
  the O's; the @ doesn't need it.

## 12. Snapshot re-synced: Nunuïko's G, $, %, ¢, &, R and 6 ◐ (2026-10-17)

`sources/upstream/Nunuiko.glyphs` re-copied from `../nunuiko/sources/` with
Nunuïko's edits 16–24 (in the same commit as Nunuïko's own source, so
`NUNUIKO_COMMIT` now just says so). Nunuïkode now has, as drawn there:
the G whose bottom-right follows the O's bowl up to the bar (18),
the $ as a full-size S with a stroke through it (19), the ¢ with a full stroke
(21), the shorter & arm (22), the R with a straight leg (23) and the shorter
tail on the 6 (24). The monospace step fits them into the cell as usual.

- **$:** code edit 6 no longer shrinks the $ to the S's height (§8): it takes
  Nunuïko's full-size S with its stroke as it is.
- **%:** code edit 6 still redraws the rings as circles 0.4 × the cap height,
  smaller than Nunuïko's round rings (edit 20), so the % fits the cell; with
  Nunuïko's even stroke the ring thickness is now the same all round
  (42 / 102 at ExtraLight / Bold).

