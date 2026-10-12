"""Cut static instances from the Nunuiko variable fonts, for tools that cannot use variable fonts."""
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

src_dir, out_dir = sys.argv[1], sys.argv[2]
WEIGHTS = [("ExtraLight", 200), ("Light", 300), ("Regular", 400), ("Medium", 500),
           ("SemiBold", 600), ("Bold", 700), ("ExtraBold", 800), ("Black", 900)]
FAMILY = "Nunuiko"

for src, italic in (("Nunuiko[wght].ttf", False), ("Nunuiko-Italic[wght].ttf", True)):
    vf = TTFont(f"{src_dir}/{src}")
    axis = next(a for a in vf["fvar"].axes if a.axisTag == "wght")
    print(src, "wght axis", axis.minValue, axis.defaultValue, axis.maxValue)
    for label, w in WEIGHTS:
        font = instancer.instantiateVariableFont(TTFont(f"{src_dir}/{src}"), {"wght": w})
        if italic:
            sub = "Italic" if label == "Regular" else f"{label} Italic"
        else:
            sub = label
        ps = f"{FAMILY}-{sub.replace(' ', '')}"
        name = font["name"]
        ribbi = sub in ("Regular", "Italic", "Bold", "Bold Italic")
        for rec in list(name.names):
            if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
                name.removeNames(nameID=rec.nameID)
        def put(i, v):
            name.setName(v, i, 3, 1, 0x409)
            name.setName(v, i, 1, 0, 0)
        if ribbi:
            put(1, FAMILY); put(2, sub)
        else:
            put(1, f"{FAMILY} {label}"); put(2, "Italic" if italic else "Regular")
            put(16, FAMILY); put(17, sub)
        put(3, f"{ps};static"); put(4, f"{FAMILY} {sub}"); put(6, ps)
        font["OS/2"].usWeightClass = w
        fs = font["OS/2"].fsSelection & ~0b1100001
        if italic: fs |= 1
        if w == 700: fs |= 1 << 5
        if not italic and w == 400: fs |= 1 << 6
        font["OS/2"].fsSelection = fs
        mac = 0
        if w == 700: mac |= 1
        if italic: mac |= 2
        font["head"].macStyle = mac
        if "STAT" in font: del font["STAT"]
        font.save(f"{out_dir}/{ps}.ttf")
