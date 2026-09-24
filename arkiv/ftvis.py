# -*- coding: utf-8 -*-
"""ftvis.py <bsid> <opslag[,opslag...]> <navn> [x0 x1 y0 y1] [--bredde N]

Henter opslag fra et AO-bind via bindets EGEN billed-id-liste (aldrig grundtal +
nummer — se kolonne2.py) og gemmer dem som JPEG i sessionens scratchpad, saa de
kan laeses med Read. Udsnit angives som broekdele 0-1 af siden.

    python ftvis.py 123456 1,2,3 gade
    python ftvis.py 123456 400 frsv 0.0 0.5 0.1 0.6 --bredde 2400
"""
import tempfile
import json
import os
import sys
import urllib.request

from hent import hent

D = os.environ.get("SCRATCH") or (os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir()
U = "https://api.rigsarkivet.dk/ao/v1/billedviser/billed-reference-lister?bsid="

bsid, opslag, navn = sys.argv[1], sys.argv[2], sys.argv[3]
rest = sys.argv[4:]
bredde = 2000
if "--bredde" in rest:
    i = rest.index("--bredde")
    bredde = int(rest[i + 1])
    rest = rest[:i] + rest[i + 2:]
kasse = [float(v) for v in rest] if len(rest) == 4 else None

req = urllib.request.Request(U + bsid, headers={"User-Agent": "slaegtsforskning/1.0"})
ids = [int(s.split(",")[1]) for s in json.load(urllib.request.urlopen(req, timeout=60))["SA_GUIDs"]]

for n in [int(v) for v in opslag.split(",")]:
    im = hent(ids[n - 1])
    b, h = im.size
    if kasse:
        im = im.crop((int(kasse[0] * b), int(kasse[2] * h),
                      int(kasse[1] * b), int(kasse[3] * h)))
    if im.size[0] > bredde:
        im = im.resize((bredde, int(im.size[1] * bredde / im.size[0])))
    sti = os.path.join(D, "%s-%03d.jpg" % (navn, n))
    im.save(sti, quality=88)
    print("%s   %dx%d" % (sti, im.size[0], im.size[1]))
