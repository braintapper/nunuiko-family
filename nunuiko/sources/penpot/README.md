# Penpot uploads

`../../penpot-uploads/` holds the Nunuiko font files that were uploaded to the owner's self-hosted
Penpot as a custom font, so the interface designs there use the same typeface as the apps. That
folder contains font files only, so everything in it can be selected at once in the upload dialog.

Generated 2026-10-12 from `fonts/variable/` at commit `93a695c3`.

## Why these files exist

Penpot (2.16, as installed) cannot take the fonts as built:

- It wants one file per weight. `fonts/variable/` holds variable fonts, so each weight is cut out
  as a static instance.
- The server cannot convert between font formats (its converter program is missing), so each
  weight is supplied as `.ttf`, `.otf` and `.woff` together and nothing is left for it to convert.

The family name inside these files is the plain-ASCII `Nunuiko`, not `Nunuïko`.

## What is in the folder

48 files: eight weights (ExtraLight 200, Light 300, Regular 400, Medium 500, SemiBold 600,
Bold 700, ExtraBold 800, Black 900), upright and italic, each in three formats.

The `.otf` files have their outlines converted from quadratic to cubic curves. They are for Penpot
only; do not ship them anywhere else.

## Uploading

1. In the Penpot dashboard (not inside a file), open **Fonts**.
2. Add fonts, and select **every file in `penpot-uploads/` in one pick**. Penpot groups the three
   formats of a weight into one entry only when they arrive together; a format uploaded by itself
   fails.
3. Press **Upload all**.

Penpot shows a warning about vertical metrics. It is expected: the fonts use the usual
Google Fonts setup, where the Windows clipping bounds differ from the line-height values on
purpose. Do not "fix" the files to silence it.

## Regenerating

Do this when the fonts change and the Penpot copy should follow. It needs `fonttools`.

```bash
# from the repo root
python sources/penpot/make_statics.py fonts/variable /tmp/nunuiko-static
python sources/penpot/make_formats.py /tmp/nunuiko-static penpot-uploads
```

`make_statics.py` cuts the 16 static `.ttf` files from the two variable fonts. `make_formats.py`
copies each `.ttf` and writes the `.otf` and `.woff` beside it. Then delete the old Nunuiko family
in Penpot's Fonts page and upload the new files.
