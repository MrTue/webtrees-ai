# -*- coding: utf-8 -*-
"""Klipper navnekolonnen ud af folketællingens husstandssider og sætter dem
side om side, så mange opslag kan skimmes i ét billede."""
import tempfile
import os
import io, sys, urllib.request
from PIL import Image, ImageDraw

D = ((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())

BASE = int(sys.argv[1])
FRA, TIL = int(sys.argv[2]), int(sys.argv[3])
TAG = sys.argv[4]
X0, X1 = (float(sys.argv[5]), float(sys.argv[6])) if len(sys.argv) > 6 else (0.05, 0.24)
ALLE = int(sys.argv[7]) if len(sys.argv) > 7 else 0
BREDDE = 620

søjler = []
for n in range(FRA, TIL + 1):
    try:
        data = urllib.request.urlopen(
            "https://api.rigsarkivet.dk/ao/v1/images/%d" % (BASE + n), timeout=30).read()
        im = Image.open(io.BytesIO(data))
    except Exception as e:                                  # noqa: BLE001
        print("opslag %d: %s" % (n, e))
        continue
    w, h = im.size
    if ALLE == 0 and w < h * 1.4:                           # smal = forside, spring over
        continue
    s = im.convert("RGB").crop((int(w * X0), int(h * 0.10), int(w * X1), h))
    s = s.resize((BREDDE, int(s.height * BREDDE / s.width)), Image.LANCZOS)
    kol = Image.new("RGB", (BREDDE, s.height + 30), "white")
    kol.paste(s, (0, 30))
    ImageDraw.Draw(kol).text((6, 8), "OPSLAG %d" % n, fill="black")
    søjler.append(kol)
    print("husstandsside:", n)

if søjler:
    hoejde = max(k.height for k in søjler)
    ark = Image.new("RGB", (BREDDE * len(søjler), hoejde), "white")
    for i, k in enumerate(søjler):
        ark.paste(k, (i * BREDDE, 0))
    p = D + "\\" + TAG + ".png"
    ark.save(p)
    print("gemt:", p, ark.size, "-", len(søjler), "sider")
