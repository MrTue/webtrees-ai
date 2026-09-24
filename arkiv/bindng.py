# -*- coding: utf-8 -*-
"""bindng.py <aar> <NgId> [<NgId> ...] — bind for et sogn slaaet op paa NgId.

`bind1919.py` slaar sognet op paa NAVN og viser kun det foerste traef. Naar flere
sogne deler navn — «Nykøbing» er baade Nykøbing Falster, Nykøbing Mors og Nykøbing
Sjælland — rammer den let det forkerte. Find NgId'et med `geosoeg.py <ord>` og
brug det her.

    python geosoeg.py nykøbing     ->  Nykøbing Mors Sogn ... NgId 532839
    python bindng.py 1842 532839
"""
import html as H
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "slaegtsforskning/1.0"}
AO = "https://arkivalieronline.rigsarkivet.dk"
API = "https://api.rigsarkivet.dk/ao/v1"


def hent(u):
    return urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=120).read().decode("utf-8", "replace")


SAML = "5"          # geo-samling: 5 kirkeboeger · 9 skoede/pante · 18 skifter · 8 brand


def bind(ng):
    s = hent(AO + "/da/geo/archive-series/%s/%d" % (SAML, ng))
    ud = []
    for epid in dict.fromkeys(re.findall(r'data-epid="(\d+)"', s)):
        t = hent(AO + "/da/geo/picture-series/%s" % epid)
        for m in re.finditer(r'bsid=(\d+)[^>]*>(.*?)</a>', t, re.S):
            txt = re.sub(r"\s+", " ", H.unescape(
                re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
            ud.append((int(m.group(1)), txt))
    return ud


def grundtal(bsid):
    d = json.loads(hent(API + "/billedviser/billed-reference-lister?bsid=%d" % bsid))
    ider = [int(s.split(",")[1]) for s in d.get("SA_GUIDs", [])]
    if not ider:
        return None, None, False
    sammen = all(ider[i] == ider[i - 1] + 1 for i in range(1, len(ider)))
    return ider[0] - 1, len(ider), sammen


arg = sys.argv[1:]
if arg and arg[0].startswith("--saml="):
    SAML = arg.pop(0).split("=", 1)[1]
aar = int(arg[0])
for ng in arg[1:]:
    print("=== NgId %s, år %d ===" % (ng, aar))
    for bsid, tekst in bind(int(ng)):
        aarstal = [int(a) for a in re.findall(r"\b(1[6-9]\d\d)\b", tekst)]
        if not aarstal or not (min(aarstal) <= aar <= max(aarstal)):
            continue
        g, n, sammen = grundtal(bsid)
        print("   %-9d %-46s grundtal %-10s opslag %-5s %s" % (
            bsid, tekst[:46], g, n, "" if sammen else "SPRING!"))
