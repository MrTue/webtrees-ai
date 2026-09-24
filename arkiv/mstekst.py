# -*- coding: utf-8 -*-
"""mstekst.py "<frase>" [maks] [ekstraord] — fri fuldtekst fra Mediestream, selvfiltreret.

/export/fields OR-soeger uanset anfoerselstegn. Scriptet henter derfor bredt og
filtrerer selv: alle ordene i frasen skal staa i teksten, med slaek imellem,
fordi OCR'en indsaetter tilfaeldige tegn. Er `ekstraord` givet, skal DET ord
ogsaa staa (fx et stednavn).
"""
import csv
import io
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
csv.field_size_limit(10_000_000)
API = "https://labs.statsbiblioteket.dk/labsapi/api/aviser"
UA = {"User-Agent": "slaegtsforskning/1.0"}
FELTER = ("familyId", "timestamp", "lplace", "newspaper_page", "link", "fulltext_org")

frase = sys.argv[1]
maks = sys.argv[2] if len(sys.argv) > 2 else "50"
ekstra = sys.argv[3] if len(sys.argv) > 3 else None

par = [("query", '"%s"' % frase if " " in frase else frase), ("max", maks)]
par += [("fields", f) for f in FELTER]
par += [("structure", "content"), ("format", "CSV")]
u = API + "/export/fields?" + urllib.parse.urlencode(par)
raa = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                             timeout=300).read().decode("utf-8", "replace")

ord_ = frase.split()
# slaek: op til 3 vilkaarlige tegn mellem ordene, og OCR forveksler ofte oe/o
moenster = re.compile(r"[\W_]{0,3}".join(re.escape(o) for o in ord_), re.I)

r = csv.reader(io.StringIO(raa))
hoved = next(r, None)
traf = 0
for row in r:
    if len(row) < 6:
        continue
    avis, tid, sted, side, lnk, tekst = row[0], row[1], row[2], row[3], row[4], row[5]
    flad = re.sub(r"\s+", " ", tekst)
    if not moenster.search(flad):
        continue
    if ekstra and not re.search(re.escape(ekstra), flad, re.I):
        continue
    traf += 1
    m = moenster.search(flad)
    a, b = max(0, m.start() - 700), min(len(flad), m.end() + 900)
    print("\n" + "=" * 78)
    print("%s  %s  %s  s.%s" % (tid[:10], avis, sted, side))
    print(lnk)
    print("-" * 78)
    print(flad[a:b])
print("\n\n*** %d træf efter filtrering ***" % traf)
