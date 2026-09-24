# -*- coding: utf-8 -*-
import re
import sys
import urllib.request
import html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
t = urllib.request.urlopen(urllib.request.Request(
    "http://www.salldata.dk/", headers=UA), timeout=90).read().decode("utf-8", "replace")
ord_ = ["lægd", "skiftemyndighed", "matrikelnumre", "ejerlav", "stednavn",
        "gade til sogn", "csv", "lægedistrikt", "hyppighed", "kirkesogne",
        "amts", "folketal", "ordbog", "download"]
for m in re.finditer(r'(?is)<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', t):
    txt = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", m.group(2)))).strip()
    if any(o in txt.lower() for o in ord_):
        print("%-46s %s" % (txt[:46], m.group(1)))
