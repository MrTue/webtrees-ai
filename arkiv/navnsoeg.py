# -*- coding: utf-8 -*-
"""navnsoeg.py <fritekst> - webtrees' egen personsoegning."""
import html
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import webtrees_klient as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
creds = K.load_creds(Path.home() / ".webtrees" / "login.json",
                     Path(__file__).resolve().parent.parent)
c = K.WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])

q = " ".join(sys.argv[1:])
sti = "/tree/%s/search-general?query=%s&search_individuals=on" % (
    c.tree, urllib.parse.quote(q))
s, h, t = c._request("GET", sti)
print("status %s  soegte paa: %s" % (s, q))
traef = re.findall(r'href="[^"]*/tree/[^"/]+/individual/(X\d+)[^"]*"[^>]*>(.*?)</a>', t)
set_ = []
for x, n in traef:
    n = re.sub(r"<[^>]+>", "", html.unescape(n)).strip()
    if (x, n) not in set_ and n:
        set_.append((x, n))
for x, n in set_[:40]:
    print("  %-8s %s" % (x, n))
print("  %d traef" % len(set_))
