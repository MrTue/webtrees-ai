# -*- coding: utf-8 -*-
"""Facit: proev hvert xref X1..X2399 direkte. Listesiderne i webtrees er
paginerede og kan ikke bruges til optaelling.

HAEV OEVRE GRAENSE, NAAR TRAEET VOKSER. Er traeet vokset forbi den, misser
scriptet alt, der er skabt over graensen, UDEN at sige det.
Sammenhold altid med graf.py, som crawler grafen og ikke kan loebe toer."""
import tempfile
import html
import io
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import webtrees_klient as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
S = ((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())
creds = K.load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
c = K.WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])
T = c.tree
FAK = re.compile(r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>')
IDS = re.compile(r'<input[^>]*name="fact_id\[\]"[^>]*value="([^"]*)"')

ud = {}
for n in range(1, 2400):
    x = "X%d" % n
    s, h, t = c._request("GET", "/tree/%s/edit-raw/%s" % (T, x))
    if s != 200:
        continue
    ids = IDS.findall(t)
    tek = [html.unescape(f).strip() for f in FAK.findall(t)]
    fakta = [{"id": a, "tekst": b} for a, b in zip(ids, tek) if a]
    tags = {e["tekst"].split("\n")[0].split()[1] for e in fakta
            if len(e["tekst"].split("\n")[0].split()) > 1}
    if "SEX" in tags or "NAME" in tags:
        slags = "PERSON"
    elif tags & {"HUSB", "WIFE", "CHIL"}:
        slags = "FAMILIE"
    elif tags & {"TITL", "ABBR", "TEXT", "AUTH"}:
        slags = "KILDE"
    elif tags & {"FILE"}:
        slags = "MEDIE"
    else:
        slags = "ANDET:" + ",".join(sorted(tags))
    ud[x] = {"slags": slags, "fakta": fakta}
    if n % 100 == 0:
        print("  ... %s (%d poster indtil nu)" % (x, len(ud)))

from collections import Counter
tael = Counter(v["slags"] for v in ud.values())
print("\nFACIT:")
for k, n in tael.most_common():
    print("   %-14s %d" % (k, n))
print("   I ALT          %d poster" % len(ud))
io.open("%s/facit.json" % S, "w", encoding="utf-8", newline="\n").write(
    json.dumps(ud, ensure_ascii=False, indent=1))
print("gemt facit.json")
