# -*- coding: utf-8 -*-
"""Grundtal og opslagsantal for et eller flere bsid."""
import urllib.request, json, sys

sys.stdout.reconfigure(encoding="utf-8")

for bsid in sys.argv[1].split(","):
    u = "https://api.rigsarkivet.dk/ao/v1/billedviser/billed-reference-lister?bsid=" + bsid
    r = urllib.request.Request(u, headers={"User-Agent": "slaegtsforskning/1.0"})
    d = json.load(urllib.request.urlopen(r, timeout=60))
    ids = [int(s.split(",")[1]) for s in d["SA_GUIDs"]]
    print("bsid %-8s grundtal %-12d opslag 1-%d" % (bsid, ids[0] - 1, len(ids)))
