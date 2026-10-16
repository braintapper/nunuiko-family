"""Build the Nunuïkode code proof (self-contained HTML).

Embeds the current Roman and Italic variable fonts as base64 woff2 into
template.html. Run from the repo root after every build:
  .venv/bin/python sources/proof/make_proof.py
Output: sources/proof/nunuikode-proof.html (gitignored; regenerate at will)
"""
import base64
import pathlib
import tempfile

from fontTools.ttLib.woff2 import compress

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
FONTS = {
    "%%NR%%": "fonts/variable/Nunuikode[wght].ttf",
    "%%NI%%": "fonts/variable/Nunuikode-Italic[wght].ttf",
}


def font_b64(path):
    with tempfile.NamedTemporaryFile(suffix=".woff2") as woff:
        compress(str(ROOT / path), woff.name)
        return base64.b64encode(pathlib.Path(woff.name).read_bytes()).decode()


def main():
    html = (HERE / "template.html").read_text()
    for token, path in FONTS.items():
        html = html.replace(token, font_b64(path))
    out = HERE / "nunuikode-proof.html"
    out.write_text(html)
    print(out, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
