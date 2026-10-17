# Nunuïko

Nunuïko (ASCII name Nunuiko) is a rounded sans derived from Nunito. Read the
repo's top-level `AGENTS.md` first: its rules, layout, build and proof
commands hold here.

- **Source:** `sources/Nunuiko.glyphs`. The glyph edits in `sources/edits/`
  were applied to it as scripts (they rewrite the source; the build doesn't
  run them). Log each edit in `GLYPHLOG.md`, per master.
- **Proof:** compares the build with the original Nunito, read from git
  history (`ORIG_COMMIT` in `sources/proof/make_proof.py`).
- **Italics:** in scope since 2026-07-07. Edits 01, 02, 04 and 05 already
  ran on the italic masters through their all-master scripts, and the fl
  width fix (01c) was extended to them.
- **Sister family:** Nunuïko Display (`../nunuiko-display/`). Most changes
  apply to both.
- **Nunuïkode** (`../nunuikode/`) is built from a snapshot of this source.
