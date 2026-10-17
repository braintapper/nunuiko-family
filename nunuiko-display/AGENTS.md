# Working ground rules

1. **Don't visual-test the fonts.** After a glyph change, build and output to the
   proof (`sources/proof/`) — the user does the visual testing. Do not render
   glyphs to images or judge their appearance yourself.

   **Always regenerate the proof whenever you generate a TTF.** Every time the
   variable font(s) are rebuilt, immediately run
   `.venv/bin/python sources/proof/make_proof.py` (from the repo root) so
   `sources/proof/nunuiko-proof.html` reflects the new build. A rebuilt TTF
   without a refreshed proof is an incomplete step.

2. **Weights over 700 are unlikely to ever be used.** The user works in the
   ExtraLight–Bold range (200–700). When judging trade-offs or where a fix has
   to hold up, prioritize ≤700; don't sink effort into making Heavy/900 (or
   interpolation toward them) perfect at the expense of the usable range.

## Branches

All changes are made on the `main` branch. Never create a branch unless the owner specifically asks
for one.

## When we do address italics

Prefer **propagating upright fixes into the existing true-italic masters
algorithmically** over regenerating italics by slanting the upright. The italics
are separately designed masters, not obliques — auto-slanting the upright would
discard them.

To make a fix propagate, express it as a **geometric rule** (line intersections,
rotations, fractions, reversal/overlap tests) that loops over every master —
the way edits 01–06 already do — rather than as pasted literal coordinates.
Rule-based edits land on the italic masters unchanged because the geometry holds
in slanted space.

Watch out for edits written with **hand-picked coordinates copied from a
single-master SFD** (e.g. edit 07's crotch collapse used literal ExtraLight
points). Those don't transfer to the slant and must be reformulated as a
construction before they can auto-apply to italics.

## Workspace

This folder is one family in the Nunuiko Family repo (`nunuiko-family`): Nunuiko in `nunuiko/`, Nunuiko Display in `nunuiko-display/`, Nunuikode in `nunuikode/`. Rules that hold for every family are in the repo's top-level `AGENTS.md`; read it first. The repo is one of several projects in the owner's development workspace; the workspace map, with every project and how they depend on each other, is in `../../CLAUDE.md`.

**Other projects depend on this family.** They **copy** the built font files out of it into their
own repos (web apps into their `public/fonts/` or `static/fonts/`, the ESPHome panels into
`esphome/fonts/`), and one reads a copy installed on the system under `/usr/local/share/fonts/`.
Nothing references this folder by path. The current list of consumers is in `../../CLAUDE.md` under
"Cross-project dependencies".

- A rebuilt font does not reach any consumer until the files are copied again. When a release
  changes file names, family names or metrics, say so, since consumers declare the family by name
  in `@font-face` and size text against the current metrics.
- The sister family is Nunuiko, in `../nunuiko/`. Many changes apply to both; see the top-level `AGENTS.md`. This folder was the `nunuiko-sans` repo; the fonts it builds are named Nunuiko Display, and consumers refer to them by that name.

Do not edit a project outside this repo from a session here without asking the owner first.
