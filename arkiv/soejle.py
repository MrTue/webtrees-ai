# -*- coding: utf-8 -*-
"""soejle.py <bsid> <fra> <til> <navn> <x0> <x1> [y0 y1] [--hoejde N]

Klipper den SAMME lodrette soejle ud af en raekke opslag og stiller dem SIDE OM
SIDE i ét billede med opslagsnummeret over hver. Beregnet til at feje en
vielses- eller doedebog, hvor kun én navnekolonne betyder noget.

`ftark.py` tager en VANDRET stribe paa tvaers af mange opslag; denne tager en
LODRET. Forskellen er afgoerende i en bog, hvor indfoerslerne staar under
hinanden i faste kolonner.

    python soejle.py 123456 100 107 brude 0.32 0.52
    python soejle.py 123456 100 107 brude 0.32 0.52 0.05 1.0 --hoejde 1700

Foerste talargument maa ogsaa vaere en KOMMALISTE af opslag; saa ignoreres
«til», og netop de opslag stilles op. Det bruges til at pejle en aargang ind:

    python soejle.py 123456 1,50,100,150,200,250,303 pejl pejl 0.32 0.60

Otte opslag per billede er som regel graensen for, hvad der kan laeses.
"""
import tempfile
import json
import os
import sys
import urllib.request

from PIL import Image, ImageDraw

from hent import hent

sys.stdout.reconfigure(encoding="utf-8")

D = os.environ.get("SCRATCH") or (os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir()
U = "https://api.rigsarkivet.dk/ao/v1/billedviser/billed-reference-lister?bsid="

if len(sys.argv) < 7:
    print(__doc__)
    raise SystemExit(1)

bsid, navn = sys.argv[1], sys.argv[4]
if "," in sys.argv[2]:
    numre = [int(n) for n in sys.argv[2].split(",")]
else:
    numre = list(range(int(sys.argv[2]), int(sys.argv[3]) + 1))
rest = sys.argv[5:]
hoejde = 1700
if "--hoejde" in rest:
    i = rest.index("--hoejde")
    hoejde = int(rest[i + 1])
    rest = rest[:i] + rest[i + 2:]
x0, x1 = float(rest[0]), float(rest[1])
y0, y1 = (float(rest[2]), float(rest[3])) if len(rest) >= 4 else (0.04, 1.0)

req = urllib.request.Request(U + bsid, headers={"User-Agent": "slaegtsforskning/1.0"})
ids = [int(s.split(",")[1]) for s in
       json.load(urllib.request.urlopen(req, timeout=60))["SA_GUIDs"]]

soejler = []
for n in numre:
    im = hent(ids[n - 1])
    b, h = im.size
    c = im.crop((int(x0 * b), int(y0 * h), int(x1 * b), int(y1 * h)))
    c = c.resize((int(c.width * hoejde / c.height), hoejde))
    soejler.append((n, c))
    print("opslag %d  ->  %dx%d" % (n, c.width, c.height))

top = 34
ark = Image.new("RGB", (sum(c.width for _, c in soejler), hoejde + top), "white")
d = ImageDraw.Draw(ark)
x = 0
for n, c in soejler:
    ark.paste(c, (x, top))
    d.text((x + 6, 8), str(n), fill="black")
    d.line([(x, 0), (x, hoejde + top)], fill="black", width=2)
    x += c.width

sti = os.path.join(D, navn + "-soejle.jpg")
ark.save(sti, quality=88)
print("%s  (%d, %d)" % (sti, ark.width, ark.height))
