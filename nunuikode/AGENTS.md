# Nunuïkode

Nunuïkode (ASCII name Nunuikode) is Nunuïko made monospaced for code. Read
the repo's top-level `AGENTS.md` first: its rules, layout, build and proof
commands hold here.

It is **derived**: the glyphs come from Nunuïko and a build pipeline turns
them into a monospaced font. Change the pipeline or add a code edit; don't
hand-edit generated files.

- **The l stays disambiguated.** It keeps Nunuïko's tail and gets the i's
  top-left flag (edit 3). The default l must never be a bare stem, which
  reads as I or |; the plain l stays opt-in through ss02.
- **Proof:** the family proof (`../proof/`) has Nunuïkode-only sections:
  texture healing (on and off) and a column grid.

## How the build works

- `sources/upstream/Nunuiko.glyphs` is a snapshot of `../nunuiko/sources/Nunuiko.glyphs`; the
  commit it came from is in `sources/upstream/NUNUIKO_COMMIT`. To pick up later
  Nunuïko changes, copy the new file in, update the commit, rebuild.
- `sources/build.py` derives the UFO masters + designspace in `sources/build/`
  (generated, gitignored): rename the family → code edits → decompose →
  monospace (600-unit cell) → drop kerning and f-ligatures → fixed-pitch flags.
  Its docstring has the full rule set and knobs (`CELL`, `SB_MIN`, `COMP`).
- **Code edits** (character changes for code, e.g. the dotted zero) live in
  `sources/edits/NN_name.py`, each with an `apply(ufo, stem, tan)` function,
  run in name order on every master **before** decomposition so composites
  built from the edited glyph follow. Log each one in `GLYPHLOG.md`.
- Build, from `sources/`: `PATH=../.venv/bin:$PATH sh build.sh` (runs
  `build.py`, then `gftools builder config.yaml`, then `display_name.py`).
  Output: `fonts/variable/Nunuikode[wght].ttf` and `Nunuikode-Italic[wght].ttf`.
