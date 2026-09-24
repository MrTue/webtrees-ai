# -*- coding: utf-8 -*-
"""ftaar.py <aarstal> — lister FT-samlingens underafdelinger for et aar
(landdistrikter, koebstaeder, sognelister, Koebenhavn ...) med select-id."""
import urllib.request, re, sys, html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
aar = sys.argv[1] if len(sys.argv) > 1 else ""
u = "https://arkivalieronline.rigsarkivet.dk/da/rif/rif-collection/7"
t = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90
                           ).read().decode("utf-8", "replace")
for m in re.finditer(r'href="([^"]*?/rif/select/7/(\d+))"[^>]*>(.*?)</a>', t, re.S):
    navn = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", m.group(3)))).strip()
    if aar and aar not in navn:
        continue
    print("  select/7/%-10s %s" % (m.group(2), navn[:100]))
