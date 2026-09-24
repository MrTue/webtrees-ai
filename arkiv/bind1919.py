# -*- coding: utf-8 -*-
"""bind1919.py <aar> <sogn> [sogn ...] [--amt=<amt>]

For hvert sognenavn: slaa NgId op i AO's geo-samling, hent alle arkivserier og
billedserier, og vis de bind, hvis periode daekker <aar>. Til sidst grundtal og
opslagsantal for hvert bind, saa en dato kan slaas op med det samme.

Har flere sogne samme navn, vinder det, hvis navn BEGYNDER med soegeordet. Med
`--amt=<amt>` (fx `--amt=Viborg`) sorteres sogne i det amt desuden foran de andre.
Uden `--amt` er der ingen amtsforkaerlighed.
"""
import html as H, json, re, sys, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "slaegtsforskning/1.0"}
AO = "https://arkivalieronline.rigsarkivet.dk"
API = "https://api.rigsarkivet.dk/ao/v1"


def hent(u):
    return urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=120).read().decode("utf-8", "replace")


_geo = None
AMT = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--amt=")), "")
sys.argv = [a for a in sys.argv if not a.startswith("--amt=")]


def ngid(navn):
    global _geo
    if _geo is None:
        _geo = hent(AO + "/da/geo/geo-collection/5")
    ud = []
    for m in re.finditer(
            r'\{"Amt":"([^"]*)", "Arkivskaber":"([^"]*)", "NgId":(\d+)\}', _geo):
        if navn.lower() in m.group(2).lower():
            ud.append((m.group(1), m.group(2), int(m.group(3))))
    # praeciseste foerst: begynder med navnet, og --amt (hvis givet) foran andre amter
    ud.sort(key=lambda r: (not r[1].lower().startswith(navn.lower()),
                           bool(AMT) and AMT.lower() not in r[0].lower()))
    return ud


def bind(ng):
    s = hent(AO + "/da/geo/archive-series/5/%d" % ng)
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
        return None, None
    return ider[0] - 1, len(ider)


aar = int(sys.argv[1])
for navn in sys.argv[2:]:
    traf = ngid(navn)
    if not traf:
        print("%-22s INTET SOGN FUNDET" % navn)
        continue
    amt, skaber, ng = traf[0]
    print("=== %s (%s, NgId %d) ===" % (skaber, amt, ng))
    for bsid, tekst in bind(ng):
        aarstal = [int(a) for a in re.findall(r"\b(1[6-9]\d\d)\b", tekst)]
        if not aarstal or not (min(aarstal) <= aar <= max(aarstal)):
            continue
        g, n = grundtal(bsid)
        print("   %-9d %-42s grundtal %-10s opslag %s" % (bsid, tekst[:42], g, n))
