"""Build the Nunuïko Family proof: one self-contained HTML page for all three
families, with a switch between them and a comparison column.

Embeds as base64 woff2 into template.html:
  - the current builds of Nunuïko, Nunuïko Display and Nunuïkode (Roman and
    Italic, from each family's fonts/variable/);
  - the sources as they were before any edit, Nunito and Nunito Sans, read
    from git history (ORIGINALS), so they never drift;
  - Cascadia Code (Latin and Latin Extended woff2 from the pinned fontsource
    package, OFL), downloaded once into proof/.cache/ (gitignored).

Run from the repo root with any family's venv (it needs fontTools and
brotli), after every build:
  nunuikode/.venv/bin/python proof/make_proof.py
Output: docs/index.html, committed and served by GitHub Pages.
"""
import base64
import pathlib
import subprocess
import tempfile
import urllib.request

from fontTools.ttLib.woff2 import compress

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
CASCADIA = "https://cdn.jsdelivr.net/npm/@fontsource-variable/cascadia-code@5.2.2/files/"
REMOTE = {
    "%%CAS_R%%": "cascadia-code-latin-wght-normal.woff2",
    "%%CAS_I%%": "cascadia-code-latin-wght-italic.woff2",
    "%%CASX_R%%": "cascadia-code-latin-ext-wght-normal.woff2",
    "%%CASX_I%%": "cascadia-code-latin-ext-wght-italic.woff2",
}
CACHE = HERE / ".cache"


def woff2_b64(ttf_bytes):
    with tempfile.TemporaryDirectory() as tmp:
        ttf, woff = pathlib.Path(tmp, "f.ttf"), pathlib.Path(tmp, "f.woff2")
        ttf.write_bytes(ttf_bytes)
        compress(str(ttf), str(woff))
        return base64.b64encode(woff.read_bytes()).decode()


def from_history(commit, path):
    return subprocess.run(["git", "-C", ROOT, "show", f"{commit}:{path}"],
                          check=True, capture_output=True).stdout


def remote_b64(name):
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(exist_ok=True)
        with urllib.request.urlopen(CASCADIA + name, timeout=60) as r:
            path.write_bytes(r.read())
    return base64.b64encode(path.read_bytes()).decode()


def main():
    html = (HERE / "template.html").read_text()
    for token, path in BUILT.items():
        html = html.replace(token, woff2_b64((ROOT / path).read_bytes()))
    for token, (commit, path) in ORIGINALS.items():
        html = html.replace(token, woff2_b64(from_history(commit, path)))
    for token, name in REMOTE.items():
        html = html.replace(token, remote_b64(name))
    assert "%%" not in html
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(OUT, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
