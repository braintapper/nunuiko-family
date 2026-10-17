# Nunuïko Display

A sans derived from [Nunito Sans](https://github.com/Fonthausen/NunitoSans),
the plain-terminal sister of [Nunuïko](../nunuiko/).

**Proof:** [https://braintapper.github.io/nunuiko-family/nunuiko-display/](https://braintapper.github.io/nunuiko-family/nunuiko-display/) (compared with the original Nunito Sans)

- Variable, Roman and Italic, with Nunito Sans's axes: weight, width,
  optical size and lowercase height
  (`fonts/variable/NunuikoDisplay[YTLC,opsz,wdth,wght].ttf` and the Italic).
  Static instances are in `fonts/ttf/`.
- Changes from Nunito Sans so far: a plain l like I by default (the tailed l
  is in ss02); a downturned f terminal; a G built on the O's bowl; a J with an
  upturned hooked foot; a Jost-style Q slash; ff / ffi / ffl ligatures with a
  joined crossbar; a K and k whose leg grows out of the arm; round dots; a
  rounder a; and a footless 1, proportional by default. Every change is logged
  per master in `GLYPHLOG.md`.

## Building

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd sources && PATH=../.venv/bin:$PATH sh build.sh
cd .. && .venv/bin/python sources/proof/make_proof.py   # proof page
```

## License

SIL Open Font License 1.1 — see `OFL.txt`. Credits for Nunito Sans are in
the [family README](../README.md#credits).
