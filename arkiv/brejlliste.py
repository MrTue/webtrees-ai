# -*- coding: utf-8 -*-
"""Lister alle Erik Brejls sider med etiket, så filnavnene kendes."""
import re
import sys
import urllib.request
import html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
t = urllib.request.urlopen(urllib.request.Request(
    "https://www.brejl.dk/", headers=UA), timeout=60).read().decode("utf-8", "replace")
ud = []
for m in re.finditer(r'(?is)<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', t):
    h = m.group(1)
    txt = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", m.group(2)))).strip()
    if txt:
        ud.append((txt, h.replace("https://www.brejl.dk/", "").replace("https://brejl.dk/", "")))
for txt, h in ud:
    print("%-42s %s" % (txt[:42], h))
