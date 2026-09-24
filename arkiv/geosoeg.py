# -*- coding: utf-8 -*-
"""geosoeg.py <ord> [samling] — raa opslag i en af Arkivalieronlines geo-samlinger.

    5  = kirkeboeger (standard)      9  = realregistre, skoede- og panteprotokoller
    8  = brandforsikring             18 = skifter, hele landet
    3  = personregistre Soenderjylland   12 = borgerlige vielser   49 = skifter Soenderjylland
"""
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "slaegtsforskning/1.0"}
AO = "https://arkivalieronline.rigsarkivet.dk"

saml = sys.argv[2] if len(sys.argv) > 2 else "5"
t = urllib.request.urlopen(urllib.request.Request(
    AO + "/da/geo/geo-collection/%s" % saml, headers=UA),
    timeout=120).read().decode("utf-8", "replace")

ord_ = sys.argv[1].lower()
n = 0
for m in re.finditer(r'\{"Amt":"([^"]*)", "Arkivskaber":"([^"]*)", "NgId":(\d+)\}', t):
    amt, skaber, ngid = m.group(1), m.group(2), m.group(3)
    if ord_ in skaber.lower() or ord_ in amt.lower():
        n += 1
        print("%-46s %-22s NgId %s" % (skaber, amt, ngid))
print("\n%d træf" % n)
