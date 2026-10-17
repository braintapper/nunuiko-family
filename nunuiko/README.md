# Nunuïko

A rounded sans derived from [Nunito](https://github.com/googlefonts/nunito).

**Proof:** [https://braintapper.github.io/nunuiko-family/#stock/nunuiko](https://braintapper.github.io/nunuiko-family/#stock/nunuiko) (Stock tab: above the original Nunito)

- Variable weight 200–1000, Roman and Italic
  (`fonts/variable/Nunuiko[wght].ttf`, `Nunuiko-Italic[wght].ttf`).
- Changes from Nunito so far: a shorter l tail; a downturned f terminal; a J
  with an upturned hooked foot; a Jost-style Q slash; ff / ffi / ffl ligatures
  with a joined crossbar; a K and k whose leg grows out of the arm; round dots;
  a rounder a; a G as wide as the O whose right side drops straight from the bar halfway down (the round G is in ss03); a $ that is a full-size S with a stroke through it; a % with round rings; a ¢ with a full stroke; a shorter & arm; an R whose leg leaves the bowl straight; a shorter tail on the 6; and a footless 1, proportional by
  default. Every change is
  logged per master in `GLYPHLOG.md`.

## Building

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd sources && PATH=../.venv/bin:$PATH sh build.sh
cd .. && .venv/bin/python ../proof/make_proof.py   # the family proof, docs/index.html
```

## License

SIL Open Font License 1.1 — see `OFL.txt`. Credits for Nunito are in the
[family README](../README.md#credits).
