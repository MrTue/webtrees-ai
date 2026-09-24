# -*- coding: utf-8 -*-
"""ft1950.py <soegeord> [--stat NE] [--filter Skov] [--sider 5]

USA's folketaelling 1950, frigivet 2022. Aabent JSON-API, ingen noegle:

    https://1950census.archives.gov/api/search/?name=<navn>&state=<XX>&page=<n>

FAELDE: API'et svarer med hele TAELLINGSDISTRIKTER, ikke personer, og navnene er
maskinlaest af haandskrift. En soegning paa "Skov" rammer ogsaa "Skovs", "Skovby"
og "Skovman". Derfor filtreres traeffene her paa en streng, man selv angiver.

Taellingen er den nyeste amerikanske, der er offentlig (1960 aabner i 2032), og
dermed den eneste vej til en dansk udvandrer, der rejste efter krigen og foer
april 1950.

    python ft1950.py Skov --stat NE
    python ft1950.py Skov --stat NE --filter Skov --sider 10
"""
import json
import ssl
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
BASE = "https://1950census.archives.gov/api/search/"

if len(sys.argv) < 2:
    print(__doc__)
    raise SystemExit(1)

rest = sys.argv[1:]
opt = {"--stat": None, "--filter": None, "--sider": "3"}
for flag in list(opt):
    if flag in rest:
        i = rest.index(flag)
        opt[flag] = rest[i + 1]
        rest = rest[:i] + rest[i + 2:]

navn = " ".join(rest)
naal = (opt["--filter"] or navn).lower()
ialt = 0

for side in range(1, int(opt["--sider"]) + 1):
    q = {"name": navn, "page": str(side)}
    if opt["--stat"]:
        q["state"] = opt["--stat"]
    url = BASE + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers=UA)
    d = json.loads(urllib.request.urlopen(req, timeout=60, context=CTX).read())
    if side == 1:
        print("DISTRIKTER I ALT: %s   (filtrerer navne paa '%s')"
              % (d.get("total"), naal))
    for r in d.get("results", []):
        traf = [n for n in (r.get("names") or [])
                if naal in (n.get("name") or "").lower()]
        for n in traf:
            ialt += 1
            print("%-28s | %-14s %-18s ED %-10s raekke %s"
                  % (n["name"], r.get("state"), r.get("county"),
                     r.get("ed"), n.get("row")))
    if not d.get("results"):
        break

print("Navnetraef med '%s': %d" % (naal, ialt))
