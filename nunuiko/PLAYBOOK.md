# Nunuïko build playbook

How this repo (a fork of `googlefonts/nunito`) was brought to a reproducible
build, and the remaining steps to turn it into the Nunuïko derivative. Written
to be repeated verbatim for **Nunito Sans** (`googlefonts/nunito-sans` → the
straight-terminal display cut). Everywhere it says `Nunito`, substitute
`NunitoSans` / `Nunito Sans` for the second run. Background and design
rationale live in `fonts.md`.

## Repo layout (what a Google Fonts upstream gives you)

- `sources/Nunito.glyphs` — the single Glyphs source. **6 masters**:
  3 weights (Light / Regular / Heavy stems ≈ 42 / 125 / 208 units) × upright + italic.
  Every glyph edit must be applied once per master.
- `sources/config.yaml` — gftools builder config (upstream renamed it from
  `builder.yaml`; some scripts may still reference the old name — see fixes).
- `sources/build.sh` — build script: gftools builder → slice combined
  `[ital,wght]` VF into separate roman/italic `[wght]` VFs → STAT/name fixes.
- `sources/fix.py` — post-build italic name/bit fixes (imports `fontbakery`).
- `fonts/variable/` — built variable TTFs (committed binaries).
- `OFL.txt` — license. **Nunito declares NO Reserved Font Name** (the copyright
  line has no "with Reserved Font Name" clause), so the rename is by choice,
  not legal necessity. **Check this again for Nunito Sans** — read the first
  line of its `OFL.txt`.

## Step 1 — reproduce the stock build (DONE for Nunito, 2026-07-05)

Golden rule: prove you can build the *unmodified* font before editing anything.

### 1a. Environment

```bash
cd <repo>
python3 -m venv .venv          # Python 3.14.5 at time of writing
.venv/bin/pip install -r requirements.txt
```

`requirements.txt` was updated to the known-good set (the upstream pin
`gftools==0.8.8` no longer installs cleanly — see fixes below):

```
gftools==0.9.996
fontbakery
setuptools<81
```

Resolved versions that worked: fontmake 3.12.1, fonttools 4.63.0,
glyphsLib 6.13.1, protobuf 3.20.3.

### 1b. Fixes that were needed (expect the same in nunito-sans)

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: pkg_resources` | Python 3.14 / setuptools ≥ 81 removed it | `pip install "setuptools<81"` |
| `TypeError: Descriptors cannot be created directly` (protobuf) | gftools 0.8.8's generated protos clash with modern deps | Upgrade to gftools 0.9.996 **in a fresh venv** (mixing old+new pins leaves an unresolvable protobuf soup — recreate the venv, don't upgrade in place) |
| `FileNotFoundError: builder.yaml` | Upstream renamed the config to `config.yaml` but `build.sh` wasn't updated | `build.sh`: `gftools builder config.yaml` |
| `gen-stat: unrecognized arguments: --axis-order` | CLI flag removed in newer gftools; axis order is now inferred | `build.sh`: drop `--axis-order 'wght' 'ital'`, keep `--inplace` |
| `ModuleNotFoundError: fontbakery` (in `fix.py`) | Never listed in requirements | `pip install fontbakery` (now in requirements.txt) |

### 1c. Build

```bash
source .venv/bin/activate
cd sources && ./build.sh
```

Outputs in `fonts/variable/`: `Nunito[ital,wght].ttf` (combined),
`Nunito[wght].ttf` (roman), `Nunito-Italic[wght].ttf`.
Rebuilt binaries differ byte-wise from the committed ones (newer toolchain) —
expected, not a problem.

### 1d. Sanity check the output

```bash
.venv/bin/python - <<'EOF'
from fontTools.ttLib import TTFont
f = TTFont('fonts/variable/Nunito[wght].ttf')
print('Family:', f['name'].getDebugName(1))
print('Axes:', [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in f['fvar'].axes])
print('Glyphs:', f['maxp'].numGlyphs)
EOF
```

Nunito result: family "Nunito", wght 200–1000, 1103 glyphs, version 3.602.

## Step 2 — tabular figures check (DONE for Nunito: solved for free)

Nunito ships no `tnum` feature because it doesn't need one: **all ten default
digits already share a fixed 600-unit advance width** — figures are tabular out
of the box. The fonts.md "figures" workstream is moot for Nunito.

**Repeat this check for Nunito Sans** (don't assume — it's a separate drawing):

```bash
.venv/bin/python - <<'EOF'
from fontTools.ttLib import TTFont
f = TTFont('fonts/variable/Nunito[wght].ttf')
hmtx, cmap = f['hmtx'], f.getBestCmap()
w = {c: hmtx[cmap[ord(c)]][0] for c in '0123456789'}
print(w, '— tabular:' , len(set(w.values())) == 1)
EOF
```

## Step 3 — rename (Nunito → Nunuiko) — TODO

Do this as its own commit, **before** any glyph edits, so test installs
coexist with real Nunito for side-by-side comparison.

- Mechanical rename in `sources/Nunito.glyphs`: `familyName`, instance/style
  names (e.g. "Nunito Heavy"), then the filenames referenced in `build.sh` and
  `config.yaml`, and the source filename itself.
- **Keep everything ASCII internally** (`Nunuiko`): PostScript names,
  filenames, family name. The display form `Nunuïko` (diaeresis) can be added
  later as a name-table nicety if wanted.
- Naming scheme (two-font route, from fonts.md): this repo → **`Nunuiko`**
  (rounded text cut); the nunito-sans fork → **`Nunuiko Display`**
  (straight display cut).
- Update `OFL.txt` copyright line to note the derivative; OFL terms carry over.

## Step 4 — the six glyph edits — TODO

Applies identically to BOTH cuts (this repo and the nunito-sans fork).
Order (easiest first): **l → f → J → Q → G → K/k**. Full design specs in
`fonts.md` § "The actual changes are small".

Linux workflow (Glyphs.app is Mac-only):

1. Convert source to per-master UFOs + designspace:
   `fontmake -g sources/Nunito.glyphs -o ufo`
   (or `glyphs2ufo` from glyphsLib).
2. Edit each master's glyph in **FontForge** (opens UFOs cleanly). Keep point
   structure identical across masters or interpolation breaks.
   6 masters if keeping italics; consider deferring italics to halve the work.
3. Rebuild: `fontmake -m <designspace> -o variable`; fix any interpolation
   errors fontmake reports.
4. After each glyph: install locally, render a size ramp, inspect at ~10px.
   For `l` specifically: test `Il1` adjacent at 10px before committing
   (the tail is the l/I/1 disambiguator).

## Step 5 — later / deferred

- **opsz variable-font merge** (rounded small ↔ straight large in one family):
  phase 2; requires redrawing one family to match the other's point structure.
  Ship the two renamed cuts first.
- **KDE rollout**: set all font roles (`kdeglobals`: `[General]` `font`,
  `menuFont`, `toolBarFont`, `smallestReadableFont`; `[WM]` `activeFont`) —
  see fonts.md § "Apply in KDE".

## Nunito Sans run — differences to expect

- Fork `googlefonts/nunito-sans`; its source/config layout may differ slightly
  (check for `.glyphs` vs UFO sources, and the builder config filename).
- Different axes: Nunito Sans upstream has **wght AND opsz/wdth variants** in
  some releases — check `fvar` after the first build and read its
  `config.yaml` before assuming the Nunito recipe applies 1:1.
- Re-check RFN in its OFL.txt (step 0) and tabular figures (step 2).
- Target name: **`Nunuiko Display`**.
