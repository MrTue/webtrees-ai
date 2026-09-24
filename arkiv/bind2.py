# -*- coding: utf-8 -*-
"""bind2.py <NgId> — lister alle bind (bsid + periode) for et sogn."""
import html as H, re, sys, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0"}


def hent(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                                  timeout=90).read().decode("utf-8", "replace")


s = hent("https://arkivalieronline.rigsarkivet.dk/da/archive-series/5/%s"
         % sys.argv[1]) if False else hent(
    "https://arkivalieronline.rigsarkivet.dk/da/geo/archive-series/5/%s" % sys.argv[1])
for ep in dict.fromkeys(re.findall(r'data-epid="(\d+)"', s)):
    p = hent("https://arkivalieronline.rigsarkivet.dk/da/geo/picture-series/%s" % ep)
    print("=== epid", ep, "===")
    for m in re.finditer(r'bsid=(\d+)[^>]*>(.*?)</a>', p, re.S):
        t = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
        print("  %-10s %s" % (m.group(1), t[:110]))
