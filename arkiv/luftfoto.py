# -*- coding: utf-8 -*-
"""luftfoto.py --sted X --bygning Y --person Z --fritekst Q [--fra 1890 --til 2015]

Det Kgl. Biblioteks «Danmark set fra luften» — skraafotos af enkelte gaarde og
huse. Resultaterne foelger ikke med siden: den kalder
POST /danmarksetfraluften/async/search/ og faar JSON tilbage i feltet
`copjects`. Kaldet kraever ogsaa kortets udsnit (bbo, zoom, lat, lng), saa her
saettes en ramme om hele Danmark.

Soegefelter: q_stednavn, q_bygningsnavn, q_person, q_fritekst."""
import urllib.request, urllib.parse, ssl, sys, json

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
URL = "https://www.kb.dk/danmarksetfraluften/async/search/"
UA = {"User-Agent": "Mozilla/5.0",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "X-Requested-With": "XMLHttpRequest",
      "Referer": "https://www.kb.dk/danmarksetfraluften/",
      "Accept": "application/json, text/javascript, */*"}
a = dict(zip(sys.argv[1::2], sys.argv[2::2]))

felt = {"--sted": "q_stednavn", "--bygning": "q_bygningsnavn",
        "--person": "q_person", "--fritekst": "q_fritekst"}
par = [("bbo", a.get("--bbo", "54.4,7.8,57.9,15.4")),
       ("zoom", a.get("--zoom", "7")),
       ("lat", "56.1"), ("lng", "11.5"),
       ("page", a.get("--side", "1"))]
for k, v in felt.items():
    par.append((v, a.get(k, "")))
par += [("notBefore", a.get("--fra", "1890")), ("notAfter", a.get("--til", "2015")),
        ("category", ""), ("itemType", ""), ("correctness", ""),
        ("thumbnailSize", ""), ("sortby", ""), ("sortorder", ""),
        ("resultsPerPage", a.get("--antal", "50"))]

b = urllib.parse.urlencode(par, encoding="utf-8").encode()
try:
    r = urllib.request.urlopen(urllib.request.Request(URL, data=b, headers=UA),
                               timeout=120, context=CTX).read().decode("utf-8", "replace")
except urllib.error.HTTPError as e:                            # noqa: PERF203
    print("HTTP", e.code)
    print(e.read().decode("utf-8", "replace")[:600])
    sys.exit(1)

try:
    d = json.loads(r)
except Exception:
    print("Ikke JSON. Første 600 tegn:"); print(r[:600]); sys.exit(1)

print("status:", d.get("status"), " træf:", d.get("totalResultsCount"),
      " sider:", d.get("pagesCount"))
cop = d.get("copjects") or []
if isinstance(cop, dict):
    cop = list(cop.values())
for c in cop[:50]:
    if not isinstance(c, dict):
        continue
    nyttige = {k: v for k, v in c.items()
               if v not in ("", None, []) and k not in ("thumbnail", "image", "icon")}
    print("  " + json.dumps(nyttige, ensure_ascii=False)[:260])
