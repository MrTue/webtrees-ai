# -*- coding: utf-8 -*-
"""avissweep.py <roster.txt> — maaler hver person i traeet i Mediestream.

Frasesoeger paa det fulde navn. Skriver en tabel sorteret efter FRIE traef
(aeldre end 140 aar = laesbar fuldtekst), for det er dem, der kan bruges.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
API = "https://labs.statsbiblioteket.dk/labsapi/api/aviser"
UA = {"User-Agent": "slaegtsforskning/1.0"}


def hits(q):
    u = API + "/hits?" + urllib.parse.urlencode({"query": q})
    for i in range(4):
        try:
            d = json.loads(urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=120).read())
            return d.get("public", 0), d.get("restricted", 0)
        except Exception:                                    # noqa: BLE001
            time.sleep(2 + 3 * i)
    return -1, -1


rader = []
for linje in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    d = linje.split("|")
    if len(d) < 7:
        continue
    x, navn, f, dd, steder, occu, priv = d[:7]
    if priv == "JA":
        continue
    if len(navn.split()) < 2:
        continue
    q = '"%s"' % navn
    p, r = hits(q)
    rader.append((p, r, x, navn, f, dd, steder.split(",")[0].strip(), occu))
    print("%-6s %-38s frit:%-5d spærret:%-6d" % (x, navn[:38], p, r), flush=True)

print("\n\n===== SORTERET EFTER FRIE TRÆF =====")
for p, r, x, navn, f, dd, sted, occu in sorted(rader, reverse=True):
    if p or r:
        print("%5d frit %6d spærret  %-6s %-36s %s %s  %s %s" % (
            p, r, x, navn[:36], f[-4:], dd[-4:], sted[:18], occu[:28]))
