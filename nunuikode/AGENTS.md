# Working ground rules

Nunuikode (public name Nunuïkode) is Nunuïko made monospaced for code. It is
**derived**: the glyphs come from the Nunuïko repo and a build pipeline turns
them into a monospaced font. Change the pipeline or add a code edit; don't
hand-edit generated files.

1. **Don't visual-test the fonts.** After a change, build and regenerate the
   proof — the user does the visual testing. Do not render glyphs to images or
   judge their appearance yourself.

   **Always regenerate the proof whenever you generate a TTF:**
   `.venv/bin/python sources/proof/make_proof.py` (from the repo root), so
   `sources/proof/nunuikode-proof.html` reflects the new build.

2. **Weights over 700 are unlikely to ever be used.** The user works in the
   ExtraLight–Bold range (200–700). Prioritise ≤700 when judging trade-offs.

3. **Italics are in scope.** Express every change as a geometric rule that runs
   on all six masters, worked in unslanted space (x − y·tan(angle)) so it holds
   on the italic masters, the way the existing pipeline and edits do.

4. **The l stays disambiguated.** It keeps Nunuïko's tail and gets the i's
   top-left flag (edit 3). The default l must never be a bare stem, which
   reads as I or |; the plain l stays opt-in through ss02.

## How the build works

- `sources/upstream/Nunuiko.glyphs` is a snapshot of `../nunuiko`'s source; the
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

## Branches

All changes are made on the `main` branch. Never create a branch unless the
owner specifically asks for one.

## Workspace

This repo is one of several sibling projects in the owner's development
workspace (one folder per repo, side by side). The workspace map, with every
project and how they depend on each other, is in `../CLAUDE.md`. Read it when a
task reaches outside this repo.

- **Upstream:** `../nunuiko` (Nunuïko), vendored as a snapshot — nothing reads
  that folder at build time. Do not edit a sibling repo from a session in this
  project without asking the owner first.
- **Consumers:** none yet. Like the other font repos, consumers would copy the
  built font files; say so when a release changes file names, family names or
  metrics.
