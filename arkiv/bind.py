# -*- coding: utf-8 -*-
"""Alle bind under en epid, med bsid og periode."""
import urllib.request, re, sys, html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
p = urllib.request.urlopen(urllib.request.Request(
    "https://arkivalieronline.rigsarkivet.dk/da/geo/picture-series/%s" % sys.argv[1],
    headers=UA), timeout=60).read().decode("utf-8", "replace")

# hver raekke: link med bsid + synlig tekst
for m in re.finditer(r'bsid=(\d+)"[^>]*>(.*?)</a>', p, re.S):
    t = H.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))
    t = re.sub(r"\s+", " ", t).strip()
    print("  bsid %-8s %s" % (m.group(1), t[:100]))
