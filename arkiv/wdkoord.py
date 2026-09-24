# -*- coding: utf-8 -*-
"""wdkoord.py <soegeord> -- slaar en koordinat op i Wikidata.

Bruges til at faa sognekirkens punkt, naar et nyt sted skal skrives ind i
webtrees-steder.csv. Kilden er maskinlaesbar og kan efterproeves.
"""
import json
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "slaegtsforskning/1.0 (kontakt via projektet)"}
API = "https://www.wikidata.org/w/api.php"


def api(**p):
    p.setdefault("format", "json")
    u = API + "?" + urllib.parse.urlencode(p)
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=90).read().decode("utf-8"))


ord_ = " ".join(sys.argv[1:])
s = api(action="wbsearchentities", search=ord_, language="da", uselang="da", limit=8)
for t in s.get("search", []):
    qid = t["id"]
    e = api(action="wbgetentities", ids=qid, props="claims|descriptions|labels")
    ent = e["entities"][qid]
    kr = ent.get("claims", {}).get("P625")
    besk = (ent.get("descriptions", {}).get("da")
            or ent.get("descriptions", {}).get("en") or {}).get("value", "")
    if not kr:
        print("%-10s %-34s %s  (ingen koordinat)" % (qid, t.get("label", "")[:34], besk[:40]))
        continue
    v = kr[0]["mainsnak"]["datavalue"]["value"]
    print("%-10s %-34s %s\n            N%.4f  E%.4f" % (
        qid, t.get("label", "")[:34], besk[:40], v["latitude"], v["longitude"]))
