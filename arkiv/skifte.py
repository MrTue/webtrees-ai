# -*- coding: utf-8 -*-
"""skifte.py [fornavn] [efternavn] [sted] — DDD's skifteregister (dprob).

Rigsarkivets frivillige har indtastet skifteprotokollernes REGISTRE — altså hvem
der er skiftet efter, hvornår og i hvilken protokol. Det er den korteste vej fra
et navn til et skifte, og skiftet navngiver arvingerne.

    POST https://ddd.dda.dk/dprob/soeg_skifte.asp
    felter: [Forms]![DialogSearch]![First] / ![Last] / ![Place]

Tomme felter betyder «alle». Sted er herred/sogn/gods, ikke amt.
"""
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0",
      "Content-Type": "application/x-www-form-urlencoded"}

fornavn = sys.argv[1] if len(sys.argv) > 1 else ""
efternavn = sys.argv[2] if len(sys.argv) > 2 else ""
sted = sys.argv[3] if len(sys.argv) > 3 else ""

data = urllib.parse.urlencode({
    "[Forms]![DialogSearch]![First]": fornavn,
    "[Forms]![DialogSearch]![Last]": efternavn,
    "[Forms]![DialogSearch]![Place]": sted,
    "sort1": "",
}).encode("iso-8859-1")

req = urllib.request.Request("https://ddd.dda.dk/dprob/soeg_skifte.asp", data=data, headers=UA)
t = urllib.request.urlopen(req, timeout=120).read().decode("iso-8859-1", "replace")

raekker = re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", t)
ud = 0
for r in raekker:
    celler = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip()
              for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", r)]
    celler = [c for c in celler if c]
    if len(celler) >= 3:
        print(" | ".join(celler))
        ud += 1
print("\nrækker: %d" % ud)
