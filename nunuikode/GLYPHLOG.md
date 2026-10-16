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
- **Glyphs that fit** in 600 − 2·`SB_MIN` (30) are moved but not reshaped. They
  keep their old left:right sidebearing ratio, clamped to 0.25–0.75.
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
