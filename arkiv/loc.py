# -*- coding: utf-8 -*-
"""loc.py <frase> [ekstraord] — Library of Congress' nye Chronicling America-API.

chroniclingamerica.loc.gov er nedlagt; samlingen ligger nu paa loc.gov med
`fo=json`. Fri fuldtekst, ingen noegle.
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
      "Accept": "application/json"}

frase = sys.argv[1]
ekstra = sys.argv[2] if len(sys.argv) > 2 else None

par = {"q": frase, "fo": "json", "c": "40", "at": "results"}
u = "https://www.loc.gov/collections/chronicling-america/?" + urllib.parse.urlencode(par)
raa = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                             timeout=240, context=CTX).read()
d = json.loads(raa)
res = d.get("results", d.get("content", {}).get("results", []))
print("resultater i svaret: %d" % len(res))
for it in res:
    titel = it.get("title", "")
    dato = it.get("date", "")
    tekst = " ".join(it.get("description", []) if isinstance(it.get("description"), list)
                     else [str(it.get("description", ""))])
    tekst = re.sub(r"\s+", " ", tekst)
    if ekstra and not re.search(re.escape(ekstra), titel + " " + tekst, re.I):
        continue
    print("\n" + "=" * 78)
    print("%s  %s" % (dato, titel[:110]))
    print(it.get("id", ""))
    m = re.search(re.escape(frase.split()[-1]), tekst, re.I)
    if m:
        a, b = max(0, m.start() - 400), min(len(tekst), m.end() + 600)
        print(tekst[a:b])
    else:
        print(tekst[:500])
