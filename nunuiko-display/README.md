# Nunuïko Display

A sans derived from [Nunito Sans](https://github.com/Fonthausen/NunitoSans),
the plain-terminal sister of [Nunuïko](../nunuiko/).

**Proof:** [https://braintapper.github.io/nunuiko-family/#stock/nunuiko-display](https://braintapper.github.io/nunuiko-family/#stock/nunuiko-display) (Nunito tab: above the original Nunito Sans)

- Version 1.0.0 (font version 1.000).
- Variable, Roman and Italic, with Nunito Sans's axes: weight, width,
  optical size and lowercase height
  (`fonts/variable/NunuikoDisplay[YTLC,opsz,wdth,wght].ttf` and the Italic).
  Static instances are in `fonts/ttf/`.
- Changes from Nunito Sans so far: a plain l like I by default (the tailed l
  is in ss02); a downturned f terminal; a J with an upturned hooked foot, rising as high as Nunuïko's; a Jost-style Q slash; ff / ffi / ffl ligatures with a
  joined crossbar; a K and k whose leg grows out of the arm; round dots, and
  round heads on commas and quotes; a rounder a; a $ that is a full-size S with a stroke through it; a G as wide as the O whose right side drops straight from the bar halfway down (the round G is in ss03); a % with round rings; a ¢ with a full stroke; a shorter & arm; an R whose leg leaves the bowl straight; a shorter tail on the 6; and a footless 1, proportional by default. Every change is logged
  per master in `GLYPHLOG.md`.

## Building

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd sources && PATH=../.venv/bin:$PATH sh build.sh
cd .. && .venv/bin/python ../proof/make_proof.py   # the family proof, docs/index.html
```

## License

SIL Open Font License 1.1 — see `OFL.txt`. Credits for Nunito Sans are in
the [family README](../README.md#credits).
