# Nunuïkode

A monospaced cut of [Nunuïko](https://github.com/braintapper/nunuiko) for code,
derived from Nunito.

- Variable weight 200–1000, Roman and Italic
  (`fonts/variable/Nunuikode[wght].ttf`, `Nunuikode-Italic[wght].ttf`).
- Every glyph is 600 units wide (combining marks: 0). Wide letters are condensed
  with their stems thickened back so their weight holds.
- No kerning and no f-ligatures.
- Code-specific changes so far: a dotted zero (0 vs O). The l keeps Nunuïko's
  tail, so Il1| stay distinct.

## Building

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd sources && PATH=../.venv/bin:$PATH sh build.sh
cd .. && .venv/bin/python sources/proof/make_proof.py   # proof page
```

The glyph source is a snapshot of Nunuïko's (`sources/upstream/`); see
`AGENTS.md` for how the pipeline works.

## License

SIL Open Font License 1.1 — see `OFL.txt`.
