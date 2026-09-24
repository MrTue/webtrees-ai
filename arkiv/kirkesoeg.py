# -*- coding: utf-8 -*-
"""kirkesoeg.py <kirkenavn> — finder sognekirkens punkt i Dataforsyningens
stednavneregister og skriver koordinaten i webtrees-steder.csv's format."""
import json
import ssl
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "slaegtsforskning/1.0"}


def hent(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                                            timeout=90, context=CTX))


navn = sys.argv[1]
r = hent("https://api.dataforsyningen.dk/stednavne2?navn=%s" % urllib.parse.quote(navn))
if not r:
    print("intet traef paa %r" % navn)
    raise SystemExit(0)
for x in r[:5]:
    s = x.get("sted", {})
    sid = s.get("id")
    if not sid:
        continue
    d = hent("https://api.dataforsyningen.dk/steder/%s" % sid)
    vc = d.get("visueltcenter") or []
    if len(vc) == 2:
        print("%-28s %-22s E%.4f  N%.4f" % (x.get("navn"), s.get("undertype"), vc[0], vc[1]))
    else:
        print("%-28s %-22s (intet punkt)" % (x.get("navn"), s.get("undertype")))
