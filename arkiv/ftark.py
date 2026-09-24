# -*- coding: utf-8 -*-
"""ftark.py <bsid> <fra> <til> <navn> [y0 y1] [--bredde N] [--kol M]

Kontaktark: klipper den samme vandrette stribe ud af en raekke opslag og saetter
dem under hinanden med opslagsnummeret skrevet ved siden af. Beregnet til at
finde det rigtige opslag i et FT-bind uden at hente hver side for sig.

    python ftark.py 123456 1 22 gade 0.14 0.26
"""
import tempfile
import json
import os
import sys
import urllib.request

from PIL import Image, ImageDraw

from hent import hent

D = ((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())
U = "https://api.rigsarkivet.dk/ao/v1/billedviser/billed-reference-lister?bsid="

bsid, fra, til, navn = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
rest = sys.argv[5:]
bredde = 1500
if "--bredde" in rest:
    i = rest.index("--bredde")
    bredde = int(rest[i + 1])
    rest = rest[:i] + rest[i + 2:]
y0, y1 = (float(rest[0]), float(rest[1])) if len(rest) >= 2 else (0.13, 0.27)

req = urllib.request.Request(U + bsid, headers={"User-Agent": "slaegtsforskning/1.0"})
ids = [int(s.split(",")[1]) for s in json.load(urllib.request.urlopen(req, timeout=60))["SA_GUIDs"]]

striber = []
for n in range(fra, til + 1):
    im = hent(ids[n - 1])
    b, h = im.size
    st = im.crop((0, int(y0 * h), b, int(y1 * h)))
    st = st.resize((bredde, int(st.size[1] * bredde / st.size[0])))
    striber.append((n, st))
    print("opslag %d  %dx%d -> %dx%d" % (n, b, h, st.size[0], st.size[1]))

sam = Image.new("RGB", (bredde + 90, sum(s.size[1] + 8 for _, s in striber)), "white")
y = 0
d = ImageDraw.Draw(sam)
for n, s in striber:
    sam.paste(s, (90, y))
    d.text((10, y + 10), "%d" % n, fill="black")
    d.line([(0, y), (sam.size[0], y)], fill="black", width=3)
    y += s.size[1] + 8
sti = os.path.join(D, "%s-ark.jpg" % navn)
sam.save(sti, quality=85)
print(sti, sam.size)
