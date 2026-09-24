# -*- coding: utf-8 -*-
"""opslagid.py <bsid> [opslag,opslag,...]

Giver de RIGTIGE billed-id'er for et bind. Grundtal + opslagsnummer holder kun,
naar bindets billed-id'er er sammenhaengende — og det er de ikke altid. Springer
et binds id'er, rammer grundtal-metoden AO's splash-billede (1920x1080) i stedet
for siden.

Uden opslagsliste vises binddets foerste og sidste id samt eventuelle spring.
"""
import json, sys, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
U = "https://api.rigsarkivet.dk/ao/v1/billedviser/billed-reference-lister?bsid="

bsid = sys.argv[1]
d = json.load(urllib.request.urlopen(urllib.request.Request(
    U + bsid, headers={"User-Agent": "slaegtsforskning/1.0"}), timeout=60))
ider = [int(s.split(",")[1]) for s in d["SA_GUIDs"]]

if len(sys.argv) > 2:
    for n in sys.argv[2].split(","):
        n = int(n)
        if 1 <= n <= len(ider):
            print("opslag %-5d billed-id %d" % (n, ider[n - 1]))
        else:
            print("opslag %-5d UDEN FOR BINDET (1-%d)" % (n, len(ider)))
else:
    spring = [(i + 1, ider[i - 1], ider[i]) for i in range(1, len(ider))
              if ider[i] != ider[i - 1] + 1]
    print("bsid %s  opslag 1-%d  foerste %d  sidste %d" %
          (bsid, len(ider), ider[0], ider[-1]))
    print("sammenhaengende" if not spring else "SPRING ved %d opslag:" % len(spring))
    for n, a, b in spring[:20]:
        print("   ved opslag %-5d %d -> %d" % (n, a, b))
