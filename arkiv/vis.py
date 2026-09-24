# -*- coding: utf-8 -*-
"""vis.py <xref> [soegetekst] — udskriver alle kendsgerninger paa en post i traeet.

Bruger webtrees' egen «rediger raa GEDCOM»-side, som klienten alligevel kalder
for at finde fact_id til `edit-fact`. Den er den eneste maade at SE, hvad der
staar paa en post, foer man erstatter den — og `edit-fact` erstatter HELE
kendsgerningen, saa det er noedvendigt at vide.

    python vis.py X14                 alle kendsgerninger
    python vis.py X14 BIRT            kun dem, hvis foerste linje rummer BIRT

Virker paa baade personer, familier og kilder. Kodeordet passerer aldrig
herigennem; klienten laeser selv loginfilen.
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import webtrees_klient as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

if len(sys.argv) < 2:
    print(__doc__)
    raise SystemExit(1)

xref = sys.argv[1]
filt = sys.argv[2].upper() if len(sys.argv) > 2 else ""

creds = K.load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).parent.parent)
c = K.WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])

status, hdrs, text = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, xref))
if status != 200:
    raise SystemExit("edit-raw svarede %s for %s" % (status, xref))

ids = re.findall(r'<input[^>]*name="fact_id\[\]"[^>]*value="([^"]*)"', text)
facts = re.findall(r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', text)
print("%s — %d kendsgerninger\n" % (xref, len(facts)))
for i, f in zip(ids, facts):
    f = html.unescape(f).strip()
    if filt and filt not in f.split("\n")[0].upper():
        continue
    print("--- fact_id %s ---" % i)
    print(f)
    print()
