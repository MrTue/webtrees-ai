# -*- coding: utf-8 -*-
"""hjorne.py <bsid> <opslag,...> <navn> [x0] [x1] [y0] [y1]
Stabler et lille hjørne fra mange opslag — til at læse sidetal og lægdnumre."""
from pathlib import Path
import tempfile
import os
import json
import sys
import urllib.request
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hent import hent

D = ((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())
U = "https://api.rigsarkivet.dk/ao/v1/billedviser/billed-reference-lister?bsid="

bsid, numre, tag = sys.argv[1], [int(n) for n in sys.argv[2].split(",")], sys.argv[3]
x0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.82
x1 = float(sys.argv[5]) if len(sys.argv) > 5 else 1.00
y0 = float(sys.argv[6]) if len(sys.argv) > 6 else 0.02
y1 = float(sys.argv[7]) if len(sys.argv) > 7 else 0.13

d = json.load(urllib.request.urlopen(urllib.request.Request(
    U + bsid, headers={"User-Agent": "slaegtsforskning/1.0"}), timeout=60))
ider = [int(s.split(",")[1]) for s in d["SA_GUIDs"]]

baand = []
for n in numre:
    if not 1 <= n <= len(ider):
        continue
    im = hent(ider[n - 1])
    w, h = im.size
    c = im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
    B = 900
    c = c.resize((B, int(c.height * B / c.width)), Image.LANCZOS)
    k = Image.new("RGB", (B + 120, c.height), "white")
    k.paste(c, (120, 0))
    ImageDraw.Draw(k).text((6, c.height // 2 - 6), "opsl %d" % n, fill="black")
    baand.append(k)

ud = Image.new("RGB", (baand[0].width, sum(b.height for b in baand)), "white")
y = 0
for b in baand:
    ud.paste(b, (0, y))
    y += b.height
ud.save(D + r"\%s.png" % tag)
print("gemt %s.png  %s" % (tag, ud.size))
