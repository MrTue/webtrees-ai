# -*- coding: utf-8 -*-
"""ftsogn.py <select-url> <soegetekst>  — finder sogne i en FT-aargangs indeks."""
import urllib.request, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
t = urllib.request.urlopen(urllib.request.Request(sys.argv[1], headers=UA), timeout=90).read().decode("utf-8", "replace")
data = json.loads(re.search(r"var\s+data\s*=\s*(\[.*?\]);", t, re.S).group(1))
print("poster:", len(data))
soeg = sys.argv[2]
for d in data:
    if re.search(soeg, json.dumps(d, ensure_ascii=False), re.I):
        print(" ", json.dumps(d, ensure_ascii=False))
