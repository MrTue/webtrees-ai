# -*- coding: utf-8 -*-
"""bindsam.py <NgId> <samling> — lister bind for et arkiv i en VILKAARLIG AO-samling.
bind2.py er laast til samling 5 (kirkeboeger); 18 = skifter, 9 = skoede- og panteprotokoller."""
import html as H
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0"}


def hent(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                                  timeout=120).read().decode("utf-8", "replace")


ngid, samling = sys.argv[1], sys.argv[2]
s = hent("https://arkivalieronline.rigsarkivet.dk/da/geo/archive-series/%s/%s" % (samling, ngid))
eps = list(dict.fromkeys(re.findall(r'data-epid="(\d+)"', s)))
print("%d serier" % len(eps))
for ep in eps:
    p = hent("https://arkivalieronline.rigsarkivet.dk/da/geo/picture-series/%s" % ep)
    print("=== epid %s ===" % ep)
    for m in re.finditer(r"bsid=(\d+)[^>]*>(.*?)</a>", p, re.S):
        t = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
        print("  %-10s %s" % (m.group(1), t[:120]))
