# Nunuïko Display

Nunuïko Display (ASCII name Nunuiko Display) is derived from Nunito Sans. It
was the `nunuiko-sans` repo. Read the repo's top-level `AGENTS.md` first: its
rules, layout, build and proof commands hold here.

- **Sources:** `sources/NunuikoDisplay.glyphs` and
  `NunuikoDisplay-Italic.glyphs`. The glyph edits in `sources/edits/` were
  applied to them as scripts (they rewrite the sources; the build doesn't run
  them). Log each edit in `GLYPHLOG.md`, per master.
- **Axes:** YTLC, opsz, wdth and wght, so the variable fonts are named
  `NunuikoDisplay[YTLC,opsz,wdth,wght].ttf`. The build also writes static
  instances to `fonts/ttf/`.
- **Sister family:** Nunuïko (`../nunuiko/`). Most changes apply to both.
