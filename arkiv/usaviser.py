# -*- coding: utf-8 -*-
"""usaviser.py <frase> [ekstraord] — amerikanske avisbaser med fri fuldtekst.

Proever begge de aabne Chronicling America-instanser:
  chroniclingamerica.loc.gov  (hele USA, til ca. 1963)
  oregonnews.uoregon.edu      (Oregon, flere lokalaviser)
"""
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "application/json,text/html;q=0.9",
      "Accept-Language": "en-US,en;q=0.9"}
BASER = [
    ("loc", "https://chroniclingamerica.loc.gov/search/pages/results/"),
    ("oregon", "https://oregonnews.uoregon.edu/search/pages/results/"),
]

frase = sys.argv[1]
ekstra = sys.argv[2] if len(sys.argv) > 2 else None
sidste = frase.split()[-1]

for navn, base in BASER:
    par = {"andtext": frase, "format": "json", "rows": "40"}
    u = base + "?" + urllib.parse.urlencode(par)
    try:
        raa = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                                     timeout=180, context=CTX).read()
        d = json.loads(raa)
    except Exception as e:                                   # noqa: BLE001
        print("### %-7s FEJL %s" % (navn, e))
        continue
    print("### %-7s total: %s" % (navn, d.get("totalItems")))
    for it in d.get("items", []):
        tekst = re.sub(r"\s+", " ", it.get("ocr_eng", "") or "")
        if ekstra and not re.search(re.escape(ekstra), tekst, re.I):
            continue
        m = re.search(re.escape(sidste), tekst, re.I)
        if not m:
            continue
        a, b = max(0, m.start() - 450), min(len(tekst), m.end() + 650)
        print("\n" + "=" * 78)
        print("%s  %s  %s, %s  s.%s" % (it.get("date"), it.get("title"),
                                        it.get("county"), it.get("state"),
                                        it.get("page")))
        print("https://chroniclingamerica.loc.gov" + (it.get("id") or ""))
        print("-" * 78)
        print(tekst[a:b])
