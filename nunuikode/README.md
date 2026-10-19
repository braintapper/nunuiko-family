# Nunuïkode

A monospaced cut of [Nunuïko](../nunuiko/) for code,
derived from Nunito.

**Proof:** [https://braintapper.github.io/nunuiko-family/#code](https://braintapper.github.io/nunuiko-family/#code) (Code tab: with Nunuïko in the character grid)

- Version 0.1.0 (font version 0.100). Its own version, separate from Nunuiko's.
- Variable weight 200–1000, Roman and Italic
  (`fonts/variable/Nunuikode[wght].ttf`, `Nunuikode-Italic[wght].ttf`).
- Every glyph is 600 units wide (combining marks: 0). Wide letters are condensed
  with their stems thickened back so their weight holds.
- No kerning and no f-ligatures.
- Lowercase letters that sit in too much white (v y x k s z) are widened a
  little, and open-sided ones (c k e) sit toward their open side.
- Texture healing (`calt`): next to i j l r t f I, the wide letters m w M W
  A O Q V borrow some of the narrow letter's space. Every cell stays 600 wide.
  Turn off `calt` in your editor to disable it.
- Code-specific changes so far: a dotted zero (0 vs O); a footed 1 (the
  footless 1 is in ss01); an i with a long foot and a top-left flag; Nunuïko's tailed l
  with the same flag and a longer tail that turns up; a j with the flag and a hook that curls up like a u; an r arched like the n, its arm stretched to fill the cell; c, e and a as wide as the o; wider t and f bars, a longer t tail and an f whose top
  arches down at the r's arch weight; a boxier O (and Q); an I with equal top and bottom bars; dots on ï that clear the stem;
  brackets and bars centred on the capitals; round %
  rings; a lower middle on W; and round © and ® and an @ centred on the capitals. From Nunuïko it takes, among others, a G with a straight drop under the bar (the round G in ss03), a $ that is a full-size S with a stroke through it, a straight-legged R and a shorter tail on the 6.

## Building

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd sources && PATH=../.venv/bin:$PATH sh build.sh
cd .. && .venv/bin/python ../proof/make_proof.py   # the family proof, docs/index.html
```

The glyph source is a snapshot of Nunuïko's (`sources/upstream/`); see
`AGENTS.md` for how the pipeline works.

## License

SIL Open Font License 1.1 — see `OFL.txt`. Credits for Nunito are in the
[family README](../README.md#credits).
