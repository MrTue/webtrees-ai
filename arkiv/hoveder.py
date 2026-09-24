# -*- coding: utf-8 -*-
"""Stabler overskriftsbåndet fra mange opslag oven på hinanden, så et binds
afsnit (fødte/konfirmerede/viede/døde) kan findes i ét billede.

    python hoveder.py <grundtal> <opslag,opslag,...> <navn> [y0] [y1]

Standard y 0.00-0.10 rammer den trykte sektionsoverskrift øverst på siden.
"""
import tempfile
import os
import io, sys, urllib.request
from PIL import Image, ImageDraw

D = ((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())

BASE = int(sys.argv[1])
NUMRE = [int(n) for n in sys.argv[2].split(",")]
TAG = sys.argv[3]
Y0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.00
Y1 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.10
BREDDE = 1500

baand = []
for n in NUMRE:
    try:
        data = urllib.request.urlopen(
            "https://api.rigsarkivet.dk/ao/v1/images/%d" % (BASE + n), timeout=30).read()
        im = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:                                  # noqa: BLE001
        print("opslag %d: %s" % (n, e))
        continue
    w, h = im.size
    s = im.crop((0, int(h * Y0), w, int(h * Y1)))
    s = s.resize((BREDDE, int(s.height * BREDDE / s.width)), Image.LANCZOS)
    rk = Image.new("RGB", (BREDDE + 130, s.height), "white")
    rk.paste(s, (130, 0))
    ImageDraw.Draw(rk).text((8, s.height // 2 - 6), "OPSLAG %d" % n, fill="black")
    baand.append(rk)
    print("opslag", n, im.size)

if baand:
    ark = Image.new("RGB", (BREDDE + 130, sum(b.height for b in baand)), "white")
    y = 0
    for b in baand:
        ark.paste(b, (0, y))
        y += b.height
    p = D + "\\" + TAG + ".png"
    ark.save(p)
    print("gemt:", p, ark.size, "-", len(baand), "opslag")
