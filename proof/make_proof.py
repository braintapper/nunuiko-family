"""Build the Nunuïko Family proof: one self-contained HTML page for all three
families, with a switch between them and a comparison column.

Embeds as base64 woff2 into template.html:
  - the current builds of Nunuïko, Nunuïko Display and Nunuïkode (Roman and
    Italic, from each family's fonts/variable/);
  - the sources as they were before any edit, Nunito and Nunito Sans, read
    from git history (ORIGINALS), so they never drift;
and, for the non-stock marks, which characters each family draws
differently from its stock font (changed.py); and, for the character grid's
tabs, every character the families map, by group, with the characters
each font shown lacks (it gets an empty cell, not a fallback font's glyph).

Run from the repo root with any family's venv (it needs fontTools and
brotli), after every build:
  nunuikode/.venv/bin/python proof/make_proof.py
Output: docs/index.html, committed and served by GitHub Pages.
"""
import base64
import json
import pathlib
import subprocess
import tempfile
import unicodedata

from fontTools.ttLib import TTFont
from fontTools.ttLib.woff2 import compress

import changed

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
OUT = ROOT / "docs" / "index.html"

BUILT = {
    "%%NK_R%%": "nunuiko/fonts/variable/Nunuiko[wght].ttf",
    "%%NK_I%%": "nunuiko/fonts/variable/Nunuiko-Italic[wght].ttf",
    "%%ND_R%%": "nunuiko-display/fonts/variable/NunuikoDisplay[YTLC,opsz,wdth,wght].ttf",
    "%%ND_I%%": "nunuiko-display/fonts/variable/NunuikoDisplay-Italic[YTLC,opsz,wdth,wght].ttf",
    "%%KD_R%%": "nunuikode/fonts/variable/Nunuikode[wght].ttf",
    "%%KD_I%%": "nunuikode/fonts/variable/Nunuikode-Italic[wght].ttf",
}
# last commits before the renames and edits: pristine Nunito / Nunito Sans
# (8c6a9bb9 in the old nunuiko repo, 058bd7a in the old nunuiko-sans repo)
ORIGINALS = {
    "%%NO_R%%": ("7539f1e9", "nunuiko/fonts/variable/Nunito[wght].ttf"),
    "%%NO_I%%": ("7539f1e9", "nunuiko/fonts/variable/Nunito-Italic[wght].ttf"),
    "%%NS_R%%": ("0bac6f5d", "nunuiko-display/fonts/variable/NunitoSans[YTLC,opsz,wdth,wght].ttf"),
    "%%NS_I%%": ("0bac6f5d", "nunuiko-display/fonts/variable/NunitoSans-Italic[YTLC,opsz,wdth,wght].ttf"),
}
# stock and our .glyphs sources, for the non-stock marks
SOURCES = {
    "nk": [(("7539f1e9", "nunuiko/sources/Nunito.glyphs"), "nunuiko/sources/Nunuiko.glyphs")],
    "nd": [(("0bac6f5d", "nunuiko-display/sources/NunitoSans.glyphs"),
            "nunuiko-display/sources/NunuikoDisplay.glyphs"),
           (("0bac6f5d", "nunuiko-display/sources/NunitoSans-Italic.glyphs"),
            "nunuiko-display/sources/NunuikoDisplay-Italic.glyphs")],
}
KODE_EDITED = "nunuikode/sources/edited-characters.txt"


def woff2_b64(ttf_bytes):
    with tempfile.TemporaryDirectory() as tmp:
        ttf, woff = pathlib.Path(tmp, "f.ttf"), pathlib.Path(tmp, "f.woff2")
        ttf.write_bytes(ttf_bytes)
        compress(str(ttf), str(woff))
        return base64.b64encode(woff.read_bytes()).decode()


def from_history(commit, path):
    return subprocess.run(["git", "-C", ROOT, "show", f"{commit}:{path}"],
                          check=True, capture_output=True).stdout


def non_stock():
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for fam, pairs in SOURCES.items():
            chars = set()
            for (commit, stock), ours in pairs:
                dest = pathlib.Path(tmp, pathlib.Path(stock).name)
                changed.from_history(ROOT, commit, stock, dest)
                chars |= changed.source_changes(str(dest), str(ROOT / ours))
            out[fam] = chars
    out["kd"] = out["nk"] | set((ROOT / KODE_EDITED).read_text().strip())
    return {k: "".join(sorted(v)) for k, v in out.items()}


def cmap(data):
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp, "f")
        path.write_bytes(data)
        return set(TTFont(str(path)).getBestCmap())


def group(cp):
    """The grid tab a character goes in; None for spaces and controls."""
    ch = chr(cp)
    cat, name = unicodedata.category(ch), unicodedata.name(ch, "")
    if cat[0] in "ZC":
        return None
    if cat[0] == "M":
        return "marks"
    for script, key in (("LATIN", "latin"), ("CYRILLIC", "cyrillic"), ("GREEK", "greek")):
        if name.startswith(script + " "):
            return key
    return "symbols"


def charset():
    """Every character the three families map, by group (the template takes
    out the Core tab's), and the ones each face lacks."""
    faces = {"nk": [BUILT["%%NK_R%%"]], "nd": [BUILT["%%ND_R%%"]], "kd": [BUILT["%%KD_R%%"]]}
    have = {k: cmap((ROOT / v[0]).read_bytes()) for k, v in faces.items()}
    have["no"] = cmap(from_history(*ORIGINALS["%%NO_R%%"]))
    have["ns"] = cmap(from_history(*ORIGINALS["%%NS_R%%"]))
    every = sorted(have["nk"] | have["nd"] | have["kd"])
    groups = {}
    for cp in every:
        g = group(cp)
        if g:
            groups[g] = groups.get(g, "") + chr(cp)
    missing = {k: "".join(chr(cp) for cp in every if group(cp) and cp not in v) for k, v in have.items()}
    return groups, missing


def main():
    html = (HERE / "template.html").read_text()
    html = html.replace("%%NONSTOCK%%", json.dumps(non_stock(), ensure_ascii=False))
    groups, missing = charset()
    html = html.replace("%%GROUPS%%", json.dumps(groups, ensure_ascii=False))
    html = html.replace("%%MISSING%%", json.dumps(missing, ensure_ascii=False))
    for token, path in BUILT.items():
        html = html.replace(token, woff2_b64((ROOT / path).read_bytes()))
    for token, (commit, path) in ORIGINALS.items():
        html = html.replace(token, woff2_b64(from_history(commit, path)))
    assert "%%" not in html
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(OUT, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
