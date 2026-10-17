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

## Branches

All changes are made on the `main` branch. Never create a branch unless the
owner specifically asks for one.

## Workspace

This folder is one family in the Nunuiko Family repo (`nunuiko-family`):
Nunuiko in `../nunuiko/`, Nunuiko Display in `../nunuiko-display/`. Rules that
hold for every family are in the repo's top-level `AGENTS.md`; read it first.
The workspace map, with every project and how they depend on each other, is in
`../../CLAUDE.md`.

- **Upstream:** `../nunuiko/` (Nunuïko), vendored as a snapshot — nothing reads
  that folder at build time except the proof, which embeds its built fonts for
  the side-by-side.
- **Consumers:** none yet. Like the other families, consumers would copy the
  built font files; say so when a release changes file names, family names or
  metrics.
