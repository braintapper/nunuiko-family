# Working ground rules

The Nunuiko Family repo holds three font families built on Nunito, each in
its own folder:

| Folder | Family | Built from |
|---|---|---|
| `nunuiko/` | Nunuïko | Nunito |
| `nunuiko-display/` | Nunuïko Display | Nunito Sans (this was the `nunuiko-sans` repo) |
| `nunuikode/` | Nunuïkode, monospaced for code | a snapshot of Nunuïko's source |

These rules hold for all three. Each family's `AGENTS.md` adds what is
particular to it; read it before changing that family.

1. **Don't visual-test the fonts.** After a change, build and regenerate that
   family's proof; a person does the visual testing. Don't render glyphs to
   images or judge their appearance. A rebuilt font without a refreshed proof
   is an incomplete step.
2. **Weights 200–700 come first.** Heavier weights are rarely used.
   Prioritise 200–700 when judging trade-offs; don't sink effort into making
   Heavy (900+) perfect at its expense.
3. **Italics are in scope.** See "Italics" below.
4. **Avoid drift between the families.** Many changes apply to both Nunuïko
   and Nunuïko Display. When a change is made to one, say whether it applies
   to the other, and make it there too unless told otherwise.
   Nunuïkode follows Nunuïko. Keep the folders laid out alike (below): a file
   that every family has lives at the same path in each, and a document that
   is the same for every family lives once, at the repo root.
5. **Work on `main` only.** Don't create branches, worktrees or pull
   requests unless asked. Commit or push only when asked.

## Layout

Every family folder has the same shape:

```
<family>/
  README.md  AGENTS.md  CLAUDE.md          what it is; family rules
  OFL.txt  AUTHORS.txt  CONTRIBUTORS.txt   license and credits
  GLYPHLOG.md                              every glyph change, per master
  requirements.txt                         Python packages for .venv/
  fonts/variable/                          built variable fonts (committed)
  sources/
    build.sh  config.yaml  display_name.py the build
    edits/                                 glyph edits (NN_name.py)
  archive/                                 kept for reference, not built
  penpot/                                  static .ttf, .otf and .woff for Penpot (sources/penpot/README.md)
```

plus what only some families have: `fonts/ttf/` (Display's static
instances) and Nunuïkode's `sources/build.py` and `sources/upstream/`.

At the repo root: `proof/`, the one proof for all three families, and `docs/`, where it is published (below); `PLAYBOOK.md` (build process and troubleshooting) and
`fonts.md` (design intent), shared by Nunuïko and Display, and `OFL.txt` with
every family's copyright lines.

## Build and proof

The same in every family. Once per family folder, set up its venv:

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Then, from the family folder:

```sh
cd sources && PATH=../.venv/bin:$PATH sh build.sh && cd ..   # fonts/variable/
.venv/bin/python ../proof/make_proof.py                       # ../docs/index.html
```

The proof is one page for all three families (`proof/template.html`, built
by `proof/make_proof.py` into `docs/index.html`). Four tabs: **Family**
compares the families with each other; **Nunito** (`#stock` in the URL) compares Nunuïko and
Display with their stock fonts (Nunito and Nunito Sans) and lists every
change from them (Nunuïkode is derived from Nunuïko, so it has no toggle there); **Code** shows Nunuïkode
in the samples, and compares it with Nunuïko in the character grid. **Test** holds only the
"Try your own" text box, in any of the five fonts (the three families, Nunito,
Nunito Sans). In each tab, toggle buttons switch each font on or off
independently. Every sample is set once
per font shown, stacked one above the next (or overlaid), and a character
grid stacks them inside each character's cell. The grid's tabs are Core (the
most used characters, listed in the template), Tabular figures (tnum on)
and, from the fonts' cmaps at
proof time, every other character the families map: Latin Extended, Cyrillic,
Symbols, Accents and Greek; a font that lacks a character gets an empty line
in its cell. The grid draws grey guides at each
font's baseline and cap height, and for the monospaced Nunuïkode at the left and right edges of the advance. In the Family and Nunito tabs that grid
marks non-stock characters, those a family draws differently from its stock
font: `proof/changed.py` compares the .glyphs sources with the stock ones in
git history, and for Nunuïkode adds the characters its code edits changed,
which its build writes to `nunuikode/sources/edited-characters.txt`. It embeds every font, so it opens anywhere, from
disk or the web. After a build of any family, regenerate it. The URL hash
holds the tab and the fonts on: `#stock/nunuiko`, `#family/nunuiko,nunuikode`,
`#code/nunuikode,nunuiko` (also `nunuiko-display`). When a glyph edit lands, add it
to that family's list in the template's `CHANGES`: title, caption, sample, and the
characters of the grid it changes (hovering a tinted cell shows the changes that list it).

## Italics

The italics are separately designed masters, not obliques. Propagate upright
fixes into them algorithmically; never regenerate italics by slanting the
upright, which would discard them. Express every glyph change as a geometric
rule (line intersections, rotations, fractions, reversal or overlap tests)
that loops over every master, worked unslanted (x − y·tan of the italic
angle), never as literal coordinates copied from one master: those don't
transfer to the slant.

## Plan

The repo was created on 2026-10-17 by importing the three old repos with
their full histories (`braintapper/nunuiko`, `nunuiko-sans`, `nunuikode`;
those were deleted from GitHub on 2026-10-18). Next, in order:

1. ~~One proof for all three families~~ (done 2026-10-17: `proof/`).
2. Shared edits: each edit that exists in both Nunuïko and Display (l tail,
   f terminal, Q slash, J hook, ff ligatures, K leg, a bowl, footless and
   proportional 1, and `lib.py`) merged into one rule that runs on both, with
   per-family settings where their outlines differ. One edit at a time, with
   a proof to check after each, since merging changes glyphs.
3. Nunuïkode builds from Nunuïko's source in this repo instead of a copied
   snapshot.

## Downstream use

Projects that use these fonts copy the built files out of each family's
`fonts/` folder; nothing references the folders by path, so a rebuilt font
reaches them only when the files are copied again. When a change alters file
names, family names or metrics, say so, since users declare the family by
name (e.g. in `@font-face`) and size text against the current metrics.

## Publishing the proofs

The proof is generated locally, not in CI, and committed: `docs/` is
served by GitHub Pages (from `main`, folder `/docs`). Commit the regenerated
proof together with the font build it shows.
