# -*- coding: utf-8 -*-
"""erstat.py <xref> <gammel> <ny> [--goer]
Finder den kendsgerning paa <xref>, der indeholder <gammel>, erstatter teksten
og skriver kendsgerningen tilbage uaendret i oevrigt. Uden --goer vises kun
forskellen."""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import webtrees_klient as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
xref, gammel, ny = sys.argv[1], sys.argv[2], sys.argv[3]
goer = "--goer" in sys.argv

creds = K.load_creds(Path.home() / ".webtrees" / "login.json",
                     Path(__file__).resolve().parent.parent)
c = K.WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])

FAK = re.compile(
    r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>')
IDS = re.compile(r'name="fact_id\[\]"[^>]*value="([^"]*)"')

s, h, t = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, xref))
if s != 200:
    raise SystemExit("%s: edit-raw %s" % (xref, s))
tekster = [html.unescape(a).strip() for a in FAK.findall(t)]
ider = IDS.findall(t)
if len(tekster) != len(ider):
    print("advarsel: %d tekster, %d id'er" % (len(tekster), len(ider)))

ramt = 0
for fid, tekst in zip(ider, tekster):
    if not fid or gammel not in tekst:
        continue
    ramt += 1
    nytekst = tekst.replace(gammel, ny)
    print("=== %s fact_id %s" % (xref, fid))
    for linje in nytekst.split("\n"):
        if ny in linje:
            print("   NY: %s" % linje[:200])
    if goer:
        c.edit_fact(xref, fid, nytekst.split("\n"))
        print("   skrevet tilbage")
if not ramt:
    print("%s: fandt ikke %r" % (xref, gammel))
else:
    print("%s: %d kendsgerning(er) ramt%s"
          % (xref, ramt, "" if goer else "  (toerkoersel - brug --goer)"))
