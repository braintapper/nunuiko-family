# Working ground rules

The Nunuiko Family repo holds three font families built on Nunito, each in
its own folder with its own build, proof and log:

| Folder | Family | Built from |
|---|---|---|
| `nunuiko/` | Nunuïko | Nunito |
| `nunuiko-display/` | Nunuïko Display | Nunito Sans (this was the `nunuiko-sans` repo) |
| `nunuikode/` | Nunuïkode, monospaced for code | a snapshot of Nunuïko's source |

Each family's `AGENTS.md` holds its own rules and build steps; read it before
changing that family. The rules below hold for all three.

1. **Don't visual-test the fonts.** After a change, build and regenerate that
   family's proof (each `AGENTS.md` names the command); the owner does the
   visual testing. Don't render glyphs to images or judge their appearance.
2. **Weights over 700 are unlikely to ever be used.** The owner works in
   200–700. Prioritise that range when judging trade-offs.
3. **Italics are in scope.** Express every glyph change as a geometric rule
   that runs on every master, worked unslanted (x − y·tan), never as literal
   coordinates copied from one master.
4. **Avoid drift between the families.** Many changes apply to both Nunuïko
   and Nunuïko Display. When a change is made to one, say whether it applies
   to the other, and make it there too unless the owner says otherwise.
   Nunuïkode follows Nunuïko.
5. **Work on `main` only.** Never create a branch, worktree or pull request
   unless the owner asks. Commit or push only when asked.

## Plan

The repo was created on 2026-10-17 by importing the three old repos with
their full histories (`braintapper/nunuiko`, `nunuiko-sans`, `nunuikode`,
left as they were). Next, in order:

1. One proof for all three families, with a family switcher and side by side.
2. Shared edits: each edit that exists in both Nunuïko and Display (l tail,
   f terminal, Q slash, J hook, ff ligatures, K leg, a bowl, footless and
   proportional 1, and `lib.py`) merged into one rule that runs on both, with
   per-family settings where their outlines differ. One edit at a time, with
   a proof for the owner to check after each, since merging changes glyphs.
3. Nunuïkode builds from Nunuïko's source in this repo instead of a copied
   snapshot.

## Workspace

This repo is one of several projects in the owner's development workspace;
the workspace map, with every project and how they depend on each other, is
in `../CLAUDE.md`. Other projects copy the built font files out of
`nunuiko/fonts/` and `nunuiko-display/fonts/`; nothing references the
folders by path. Do not edit a project outside this repo without asking the
owner first.
