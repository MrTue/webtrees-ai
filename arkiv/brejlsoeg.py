# -*- coding: utf-8 -*-
"""brejlsoeg.py <ord> <side.html> [side.html ...] — søger i Erik Brejls skifteuddrag.

Siderne er Brejls filnavne for de herreder/sogne, der skal gennemsøges (fx
`<herred>.html`); `brejlliste.py` lister dem alle. MINDST ÉN SIDE ER PÅKRÆVET. Vil du
have din egen standard, så udfyld STD nedenfor.
"""
import re
import sys
import urllib.request
import html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
BASE = "https://www.brejl.dk/"

# Din egen standardliste af Brejl-sider, fx ["<herred>.html", "<sogn>.html"]. Tom = påkrævet argument.
STD = []


def hent(sti):
    u = sti if sti.startswith("http") else BASE + sti
    raw = urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=120).read()
    kand = []
    for enc in ("utf-8", "windows-1252"):
        s = raw.decode(enc, "replace")
        kand.append((s.count("�") + s.count("Ã"), s))
    return min(kand, key=lambda x: x[0])[1]


if len(sys.argv) < 2:
    raise SystemExit(__doc__)
ord_ = sys.argv[1]
sider = sys.argv[2:] or STD
if not sider:
    raise SystemExit(__doc__)
for s in sider:
    try:
        t = hent(s)
    except Exception as e:
        print("%-20s FEJL %s" % (s, e))
        continue
    flad = re.sub(r"\s+", " ", H.unescape(
        re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", t)))
    traf = [m.start() for m in re.finditer(re.escape(ord_), flad, re.I)]
    print("%-20s %7d tegn  %d træf" % (s, len(flad), len(traf)))
    for p in traf[:12]:
        print("    …" + flad[max(0, p - 160):p + 220].strip() + "…")
