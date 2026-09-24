# -*- coding: utf-8 -*-
"""Finder forsiderne i en folketælling og klipper 'Byens Navn'-feltet ud af hver,
stablet i ét billede, så mange skemaer kan læses på én gang."""
import tempfile
import os
import io, sys, urllib.request
from PIL import Image, ImageDraw

D = ((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())
BASE = int(sys.argv[1])          # grundtal
N = int(sys.argv[2])             # antal opslag
FRA = int(sys.argv[3]) if len(sys.argv) > 3 else 1
TIL = int(sys.argv[4]) if len(sys.argv) > 4 else N
TAG = sys.argv[5] if len(sys.argv) > 5 else "forsider"

strimler = []
for n in range(FRA, TIL + 1):
    try:
        data = urllib.request.urlopen(
            "https://api.rigsarkivet.dk/ao/v1/images/%d" % (BASE + n), timeout=30).read()
        im = Image.open(io.BytesIO(data))
    except Exception as e:                       # noqa: BLE001
        print("opslag %d: fejl %s" % (n, e))
        continue
    w, h = im.size
    if w > h * 1.4:                              # bred = husstandsliste, ikke forside
        continue
    # øverste tredjedel: amt/herred/sogn + byens navn
    s = im.convert("RGB").crop((int(w * 0.44), int(h * 0.185), int(w * 0.95), int(h * 0.26)))
    s = s.resize((1300, int(s.height * 1300 / s.width)), Image.LANCZOS)
    mærkat = Image.new("RGB", (1300, s.height + 34), "white")
    mærkat.paste(s, (0, 34))
    ImageDraw.Draw(mærkat).text((8, 8), "OPSLAG %d" % n, fill="black")
    strimler.append((n, mærkat))
    print("forside fundet: opslag %d  (%dx%d)" % (n, w, h))

if strimler:
    total = sum(s.height for _, s in strimler)
    ark = Image.new("RGB", (1300, total), "white")
    y = 0
    for _, s in strimler:
        ark.paste(s, (0, y))
        y += s.height
    p = D + "\\" + TAG + ".png"
    ark.save(p)
    print("gemt:", p, ark.size, "-", len(strimler), "forsider")
