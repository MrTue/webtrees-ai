# -*- coding: utf-8 -*-
"""ftnavne.py <bsid> <opslag,opslag,...> <navn> [x0 x1 y0 y1] [--bredde N]

Kontaktark over NAVNEKOLONNEN i en raekke FT-skemaer: klipper den samme kasse ud
af hvert opslag og saetter dem under hinanden med opslagsnummer ved siden af.
Bruges til at finde den rigtige husstand i en gade uden at hente hvert skema.

    python ftnavne.py 123456 3,6,9,12,15,18,21 gade 0.02 0.22 0.28 0.56
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

bsid, opslag, navn = sys.argv[1], sys.argv[2], sys.argv[3]
rest = sys.argv[4:]
bredde = 1200
if "--bredde" in rest:
    i = rest.index("--bredde")
    bredde = int(rest[i + 1])
    rest = rest[:i] + rest[i + 2:]
x0, x1, y0, y1 = ([float(v) for v in rest] if len(rest) == 4
                  else [0.02, 0.22, 0.28, 0.56])

req = urllib.request.Request(U + bsid, headers={"User-Agent": "slaegtsforskning/1.0"})
ids = [int(s.split(",")[1]) for s in json.load(urllib.request.urlopen(req, timeout=60))["SA_GUIDs"]]

striber = []
for n in [int(v) for v in opslag.split(",")]:
    im = hent(ids[n - 1])
    b, h = im.size
    st = im.crop((int(x0 * b), int(y0 * h), int(x1 * b), int(y1 * h)))
    st = st.resize((bredde, int(st.size[1] * bredde / st.size[0])))
    striber.append((n, st))
    print("opslag %d  %dx%d" % (n, st.size[0], st.size[1]))

sam = Image.new("RGB", (bredde + 90, sum(s.size[1] + 8 for _, s in striber)), "white")
y = 0
d = ImageDraw.Draw(sam)
for n, s in striber:
    sam.paste(s, (90, y))
    d.text((10, y + 10), "%d" % n, fill="black")
    d.line([(0, y), (sam.size[0], y)], fill="black", width=3)
    y += s.size[1] + 8
sti = os.path.join(D, "%s-navne.jpg" % navn)
sam.save(sti, quality=85)
print(sti, sam.size)
