# -*- coding: utf-8 -*-
"""ark.py <grundtal> <fra> <til> <udfil> [x0 x1 y0 y1] — KONTAKTARK af flere opslag.

Henter en raekke opslag fra Arkivalieronline, beskaerer den SAMME kolonne af hvert
og saetter dem SIDE OM SIDE i ét billede med opslagsnummeret skrevet over hver soejle.

Lavet for at kunne feje en kirkebog igennem uden at hente ét billede ad gangen. Naar
man kun leder efter ét efternavn, er navnekolonnen nok — og seks opslag i ét billede
er seks gange faerre opslag at se paa.

    ark.py 12345600 133 138 ark133.jpg 0.26 0.45 0.12 1.0
        -> 2034x1244 med opslag 133-138, kun kolonnen «Barnets fulde Navn»

GRUNDTALLET er saadan at billed_id = grundtal + opslagsnummer. Pas paa: for nogle
bind er grundtallet foerste billed-id MINUS én, for andre foerste billed-id selv.
Kontrollér med opslagid.py og ét proeveopslag, foer du fejer.

KOLONNER, der har vist sig brugbare i kirkeboeger fra 1900-tallet:
    0.26 0.45 0.12 1.0   «Barnets fulde Navn» alene
    0.08 0.60 0.12 1.0   foedselsdato + navn + foraeldre
    0.45 1.00 0.10 0.30  hovedet paa et folketaellingsskema (gade og husnummer)

SOEJLEBREDDEN bliver (x1-x0) gange billedets bredde. Seks soejler af 339 punkter
giver 2034 — det er omtrent graensen for, hvad der kan laeses i ét billede.
"""
import io
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
sys.stdout.reconfigure(encoding="utf-8")

if len(sys.argv) < 5:
    print(__doc__)
    raise SystemExit(1)

grundtal = int(sys.argv[1])
fra = int(sys.argv[2])
til = int(sys.argv[3])
ud = sys.argv[4]
rest = sys.argv[5:9]
x0, x1, y0, y1 = ([float(v) for v in rest] if len(rest) == 4
                  else [0.26, 0.45, 0.12, 1.0])

UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
dele = []
for o in range(fra, til + 1):
    bid = grundtal + o
    u = "https://api.rigsarkivet.dk/ao/v1/images/%s" % bid
    d = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
    im = Image.open(io.BytesIO(d)).convert("L")
    w, h = im.size
    im = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    dele.append((o, im))
    print("  opslag %d  (billed-id %d)  ->  %dx%d" % (o, bid, im.size[0], im.size[1]))

if not dele:
    print("ingen opslag")
    raise SystemExit(1)

top = 26
bh = max(i.size[1] for _, i in dele) + top
bw = sum(i.size[0] for _, i in dele)
ark = Image.new("L", (bw, bh), 255)
d = ImageDraw.Draw(ark)
x = 0
for o, im in dele:
    ark.paste(im, (x, top))
    d.text((x + 6, 6), "opslag %d" % o, fill=0)
    d.line([(x, 0), (x, bh)], fill=0, width=2)
    x += im.size[0]
ark.save(ud, quality=90)
print("%s  (%dx%d)" % (ud, bw, bh))
