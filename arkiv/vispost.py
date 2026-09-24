# -*- coding: utf-8 -*-
"""vispost.py <xref> [xref ...] — foerste linje af hver kendsgerning."""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import webtrees_klient as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
creds = K.load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
c = K.WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])
FAK = re.compile(r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>')

for x in sys.argv[1:]:
    s, h, t = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, x))
    if s != 200:
        print("%s: edit-raw %s" % (x, s))
        continue
    f = [html.unescape(a).strip() for a in FAK.findall(t) if a.strip()]
    print("=== %s — %d kendsgerninger" % (x, len(f)))
    for e in f:
        print("   %s" % e.split("\n")[0][:96])
