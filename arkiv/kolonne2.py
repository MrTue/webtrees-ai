# -*- coding: utf-8 -*-
"""kolonne2.py <bsid> <opslag,opslag,...> <navn> <x0> <x1> [bredde]

Klipper den samme lodrette kolonne ud af en raekke opslag og stiller dem side om
side. Opslagsnumrene slaas op i bindets RIGTIGE billed-id-liste i stedet for at
regne grundtal + nummer. Brug altid denne, naar opslagid.py melder
SPRING — ellers henter man AO's splash-billede i stedet for siden.
"""
import tempfile
import os
import json, sys, urllib.request
from PIL import Image, ImageDraw
from hent import hent

D = ((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())
U = "https://api.rigsarkivet.dk/ao/v1/billedviser/billed-reference-lister?bsid="

BSID = sys.argv[1]
NUMRE = [int(n) for n in sys.argv[2].split(",")]
TAG = sys.argv[3]
X0, X1 = float(sys.argv[4]), float(sys.argv[5])
BREDDE = int(sys.argv[6]) if len(sys.argv) > 6 else 300

d = json.load(urllib.request.urlopen(urllib.request.Request(
    U + BSID, headers={"User-Agent": "slaegtsforskning/1.0"}), timeout=60))
ider = [int(s.split(",")[1]) for s in d["SA_GUIDs"]]

kolonner = []
for n in NUMRE:
    if not 1 <= n <= len(ider):
        print("opslag %d uden for bindet (1-%d)" % (n, len(ider)))
        continue
    try:
        im = hent(ider[n - 1])
    except Exception as e:                                   # noqa: BLE001
        print("opslag %d: %s" % (n, e))
        continue
    w, h = im.size
    s = im.crop((int(w * X0), int(h * 0.11), int(w * X1), h))
    s = s.resize((BREDDE, int(s.height * BREDDE / s.width)), Image.LANCZOS)
    k = Image.new("RGB", (BREDDE, s.height + 26), "white")
    k.paste(s, (0, 26))
    ImageDraw.Draw(k).text((4, 7), "OPSL %d" % n, fill="black")
    kolonner.append(k)

if kolonner:
    H = max(k.height for k in kolonner)
    ark = Image.new("RGB", (BREDDE * len(kolonner), H), "white")
    for i, k in enumerate(kolonner):
        ark.paste(k, (i * BREDDE, 0))
    p = D + "\\" + TAG + ".png"
    ark.save(p)
    print("gemt:", p, ark.size, "-", len(kolonner), "sider")
