# -*- coding: utf-8 -*-
"""ftfind.py <rif-id> <soegeord> — finder sogne-poster i en folketælling paa AO.

rif-id'er (samling 7, folketaellinger) faas af rif-collection/7. Eksempler:
    16924511  FT1911 Landdistrikter      16925563  FT1916 Landdistrikter
    16955693  FT1921 Sognelister         16969292  FT1925 Sognelister
    16924206  FT1911 Koebenhavn          16955688  FT1921 Koebenhavn
"""
import json, re, sys, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0"}
s = urllib.request.urlopen(urllib.request.Request(
    "https://arkivalieronline.rigsarkivet.dk/da/rif/select/7/%s" % sys.argv[1],
    headers=UA), timeout=120).read().decode("utf-8", "replace")
m = re.search(r"var\s+data\s*=\s*(\[.*?\]);", s, re.S)
if not m:
    print("fandt ikke 'var data' — sidens opbygning er aendret")
    print(s[:800])
    raise SystemExit(1)
rows = json.loads(m.group(1))
ord_ = [a.lower() for a in sys.argv[2:]]
n = 0
for r in rows:
    t = json.dumps(r, ensure_ascii=False)
    if ord_ and not any(o in t.lower() for o in ord_):
        continue
    n += 1
    print(t[:400])
print("---", n, "af", len(rows), "poster")
