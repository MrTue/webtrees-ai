# -*- coding: utf-8 -*-
"""nygaard.py <ord> — prøver Nygaards Sedler (ddd.dda.dk/nygaard)."""
import re
import sys
import urllib.parse
import urllib.request
import html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://ddd.dda.dk/nygaard/sogeside.asp",
      "Content-Type": "application/x-www-form-urlencoded"}

ord_ = sys.argv[1]
for u, felter in [
    ("https://ddd.dda.dk/nygaard/visning.asp", {"navn": ord_}),
    ("https://ddd.dda.dk/nygaard/sogeresultat.asp", {"navn": ord_}),
    ("https://ddd.dda.dk/nygaard/sogeside.asp", {}),
]:
    try:
        d = urllib.parse.urlencode(felter, encoding="windows-1252", errors="replace").encode() if felter else None
        r = urllib.request.urlopen(urllib.request.Request(u, data=d, headers=UA), timeout=90)
        t = r.read().decode("windows-1252", "replace")
        flad = re.sub(r"\s+", " ", H.unescape(re.sub(r"(?is)<script.*?</script>|<[^>]+>", " ", t)))
        print("===", u, r.status, len(t))
        print(flad[:900])
        print()
    except Exception as e:
        print("FEJL", u, e)
