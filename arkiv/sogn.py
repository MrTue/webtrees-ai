# -*- coding: utf-8 -*-
"""sogn.py <soegeord> — finder NgId for sogne i AO's geo-samling 5."""
import re, sys, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0"}
s = urllib.request.urlopen(urllib.request.Request(
    "https://arkivalieronline.rigsarkivet.dk/da/geo/geo-collection/5",
    headers=UA), timeout=90).read().decode("utf-8", "replace")
ord_ = [a.lower() for a in sys.argv[1:]]
for m in re.finditer(r'\{"Amt":"([^"]*)", "Arkivskaber":"([^"]*)", "NgId":(\d+)\}', s):
    amt, navn, ngid = m.group(1), m.group(2), m.group(3)
    if any(o in navn.lower() for o in ord_):
        print("%-10s %-28s %s" % (ngid, amt, navn))
