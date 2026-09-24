# -*- coding: utf-8 -*-
"""ronlevsoeg.py <ord> [ord ...] -- soeger i Claus Roenlevs katalogsider.

Katalogsiderne hedder ronlev.dk/kildeskrifter/<nr>-<periode>.html.
"""
import html as H
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
SIDER = [
    "https://www.ronlev.dk/kildeskrifter.html",
    "https://www.ronlev.dk/kildeskrifter/312-middelalderen.html",
    "https://www.ronlev.dk/kildeskrifter/313-renaessancen.html",
    "https://www.ronlev.dk/kildeskrifter/314-enevaelden.html",
    "https://www.ronlev.dk/kildeskrifter/315-nyere-tid.html",
]
ORD = [o.lower() for o in sys.argv[1:]]


def hent(u):
    try:
        return urllib.request.urlopen(
            urllib.request.Request(u, headers=UA), timeout=90
        ).read().decode("utf-8", "replace")
    except Exception as e:
        return "FEJL %s" % e


for u in SIDER:
    t = hent(u)
    if t.startswith("FEJL"):
        print("%-64s %s" % (u.split("/")[-1], t))
        continue
    # hvert vaerk staar som et link til en egen side
    poster = re.findall(r'(?is)<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', t)
    tref = 0
    for href, txt in poster:
        ren = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", txt))).strip()
        if not ren:
            continue
        lav = ren.lower()
        if all(o in lav for o in ORD):
            print("  %-70s %s" % (ren[:70], href[:70]))
            tref += 1
    print("%-64s %d poster, %d traef" % (u.split("/")[-1], len(poster), tref))
