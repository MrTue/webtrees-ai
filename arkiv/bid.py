# -*- coding: utf-8 -*-
"""bid.py <guid> [guid ...] — bildvisnings-GUID -> Riksarkivets billed-id."""
import sys, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
H = {"User-Agent": "Mozilla/5.0", "Referer": "https://sok.riksarkivet.se/"}
for g in sys.argv[1:]:
    u = "https://sok.riksarkivet.se/bildvisning/" + g
    r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60)
    print("%s -> %s" % (g[:8], r.url.rsplit("/", 1)[-1]))
