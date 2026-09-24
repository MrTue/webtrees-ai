# -*- coding: utf-8 -*-
"""Autoritativ optaelling: kryds hele grafen igennem via FAMS/FAMC og
familiernes HUSB/WIFE/CHIL, indtil der ikke kommer flere til.
Listesiderne i webtrees viser IKKE alle - de kan ikke bruges som facit."""
import tempfile
import os
import html
import io
import json
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
cache = {}


def fakta(x):
    if x in cache:
        return cache[x]
    s, h, t = c._request("GET", "/tree/%s/edit-raw/%s" % (T, x))
    if s != 200:
        cache[x] = None
        return None
    ids = IDS.findall(t)
    tek = [html.unescape(f).strip() for f in FAK.findall(t)]
    cache[x] = [{"id": a, "tekst": b} for a, b in zip(ids, tek) if a]
    return cache[x]


start = set(json.load(io.open("%s/alle_personer.json" % S, encoding="utf-8")))
koe = list(start)
personer, familier = set(), set()
runde = 0
while koe:
    runde += 1
    nye_fam = set()
    for x in koe:
        f = fakta(x)
        if f is None:
            continue
        personer.add(x)
        for e in f:
            nye_fam |= set(re.findall(r"^1 FAM[SC] @([A-Za-z0-9_]+)@", e["tekst"], re.M))
    nye_fam -= familier
    koe = []
    for fx in sorted(nye_fam):
        f = fakta(fx)
        if f is None:
            continue
        familier.add(fx)
        for e in f:
            for p in re.findall(r"^1 (?:HUSB|WIFE|CHIL) @([A-Za-z0-9_]+)@", e["tekst"], re.M):
                if p not in personer:
                    koe.append(p)
    koe = sorted(set(koe))
    print("runde %d: %d personer, %d familier, %d nye i koe" %
          (runde, len(personer), len(familier), len(koe)))

print("\nPERSONER I GRAFEN: %d" % len(personer))
print("FAMILIER I GRAFEN: %d" % len(familier))
mangler = sorted(personer - start, key=lambda z: int(re.sub(r"\D", "", z) or 0))
print("\nIKKE MED I LISTESIDERNE (%d): %s" % (len(mangler), mangler))
io.open("%s/graf_personer.json" % S, "w", encoding="utf-8", newline="\n").write(
    json.dumps({"personer": sorted(personer), "familier": sorted(familier)}, ensure_ascii=False))
