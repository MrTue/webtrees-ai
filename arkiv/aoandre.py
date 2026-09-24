# -*- coding: utf-8 -*-
"""aoandre.py <sti> [soegeord] — browser Arkivalieronlines IKKE-geografiske samlinger.

Kirkebøger, folketaellinger og skoede-/panteprotokoller ligger i geo-browseren
(/da/geo/...), men laegdsruller, skifter, faengsler og retsvaesen ligger i en
anden gren:

    /da/collection/theme/<n>            tema (21 = laegdsruller, 30 = skifter,
                                        12 = ejendomme)
    /da/other/other-collection/<n>      samling (170 = laegdsruller fra
                                        centraladministrationen 1706-1931)
    /da/other/archive-series/<...>      arkivserier
    /da/other/picture-series/<epid>     billedserier med bsid

Scriptet viser links og tabelrækker paa en vilkaarlig AO-side, saa strukturen
kan foelges et niveau ad gangen.
"""
import html as H
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "slaegtsforskning/1.0"}
AO = "https://arkivalieronline.rigsarkivet.dk"

sti = sys.argv[1]
if not sti.startswith("http"):
    sti = AO + sti
ord_ = sys.argv[2].lower() if len(sys.argv) > 2 else None

t = urllib.request.urlopen(urllib.request.Request(sti, headers=UA),
                           timeout=120).read().decode("utf-8", "replace")

print("=== %s" % sti)
m = re.search(r"<title>(.*?)</title>", t, re.S)
if m:
    print("    " + re.sub(r"\s+", " ", H.unescape(m.group(1))).strip())

vist = 0
for mm in re.finditer(r'href="([^"]*(?:other|geo|billedviser|bsid)[^"]*)"[^>]*>(.*?)</a>', t, re.S):
    url = mm.group(1)
    txt = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", mm.group(2)))).strip()
    if not txt or txt.lower() in ("læs her", "her"):
        continue
    if ord_ and ord_ not in txt.lower() and ord_ not in url.lower():
        continue
    print("    %-58s %s" % (txt[:58], url))
    vist += 1
    if vist > 120:
        print("    ... (afkortet)")
        break

if not vist:
    # nogle sider lægger indholdet i data-attributter i stedet for <a>
    for mm in re.finditer(r'data-(?:epid|bsid|id)="(\d+)"[^>]*>(.*?)<', t, re.S)  :
        txt = re.sub(r"\s+", " ", H.unescape(mm.group(2))).strip()
        if txt:
            print("    data-id %-10s %s" % (mm.group(1), txt[:60]))
            vist += 1
    if not vist:
        flad = re.sub(r"\s+", " ", H.unescape(re.sub(
            r"(?s)<(script|style).*?</\1>", " ", re.sub(r"<[^>]+>", " ", t))))
        print("    (ingen links) " + flad[:1200])
