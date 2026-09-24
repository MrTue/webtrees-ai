# -*- coding: utf-8 -*-
"""raavis.py <xref> [filter] - hele teksten af hver kendsgerning, evt. kun dem der
starter med <filter>."""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import webtrees_klient as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
creds = K.load_creds(Path.home() / ".webtrees" / "login.json",
                     Path(__file__).resolve().parent.parent)
c = K.WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])
FAK = re.compile(r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>')

xref = sys.argv[1]
filt = sys.argv[2] if len(sys.argv) > 2 else ""

s, h, t = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, xref))
if s != 200:
    print("%s: edit-raw %s" % (xref, s))
    raise SystemExit(1)
f = [html.unescape(a).strip() for a in FAK.findall(t) if a.strip()]
n = 0
for e in f:
    if filt and not e.startswith(filt):
        continue
    n += 1
    print("---------------------------------------------------------------")
    print(e)
print("===============================================================")
print("%s: %d kendsgerninger i alt, %d vist" % (xref, len(f), n))
