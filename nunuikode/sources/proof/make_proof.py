"""Build the Nunuïkode code proof (self-contained HTML).

Embeds the current Roman and Italic variable fonts as base64 woff2 into
template.html, plus, for the side-by-side comparison, Nunuïko's (read
from the sibling ../nunuiko checkout) and Cascadia Code's (Latin and Latin
Extended woff2 from the pinned fontsource package, OFL; downloaded once
into sources/proof/.cache/, gitignored). Run from the repo root after every build:
  .venv/bin/python sources/proof/make_proof.py
Output: sources/proof/nunuikode-proof.html (gitignored; regenerate at will)
"""
import base64
import pathlib
import tempfile
import urllib.request

from fontTools.ttLib.woff2 import compress

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
FONTS = {
    "%%NR%%": "fonts/variable/Nunuikode[wght].ttf",
    "%%NI%%": "fonts/variable/Nunuikode-Italic[wght].ttf",
    "%%PR%%": "../nunuiko/fonts/variable/Nunuiko[wght].ttf",
    "%%PI%%": "../nunuiko/fonts/variable/Nunuiko-Italic[wght].ttf",
}

CASCADIA = "https://cdn.jsdelivr.net/npm/@fontsource-variable/cascadia-code@5.2.2/files/"
REMOTE = {
    "%%CR%%": "cascadia-code-latin-wght-normal.woff2",
    "%%CI%%": "cascadia-code-latin-wght-italic.woff2",
    "%%CXR%%": "cascadia-code-latin-ext-wght-normal.woff2",
    "%%CXI%%": "cascadia-code-latin-ext-wght-italic.woff2",
}
CACHE = HERE / ".cache"


def remote_b64(name):
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(exist_ok=True)
        with urllib.request.urlopen(CASCADIA + name, timeout=60) as r:
            path.write_bytes(r.read())
    return base64.b64encode(path.read_bytes()).decode()


def font_b64(path):
    with tempfile.NamedTemporaryFile(suffix=".woff2") as woff:
        compress(str(ROOT / path), woff.name)
        return base64.b64encode(pathlib.Path(woff.name).read_bytes()).decode()


def main():
    html = (HERE / "template.html").read_text()
    for token, path in FONTS.items():
        html = html.replace(token, font_b64(path))
    for token, name in REMOTE.items():
        html = html.replace(token, remote_b64(name))
    out = HERE / "nunuikode-proof.html"
    out.write_text(html)
    print(out, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
