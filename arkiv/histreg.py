# -*- coding: utf-8 -*-
"""histreg.py — Histreg, Norges historiske befolkningsregister (histreg.no).

Personbaseret indeks til HELE Digitalarkivet: kirkeboeger, folketaellinger og
udvandrerprotokoller er koblet sammen person for person. Gratis, uden login,
daekker afdoede personer foer 1923.

    python histreg.py --efternavn=Nordmann --faar=1760-1775 --fsted=Krist*
    python histreg.py --fornavn=Ola --efternavn=Nordmann

Jokertegn: Krist* = begynder med · *nes = slutter paa · -Videnes = undtaget ·
Nils|Niels = enten eller.
"""
import re
import sys
import urllib.parse
import urllib.request
import html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0",
      "Content-Type": "application/x-www-form-urlencoded",
      "Referer": "https://www.histreg.no/index.php/search"}
URL = "https://www.histreg.no/index.php/searchresults"

f = {"name": "", "surname": "", "birthyearfrom": "", "birthyearto": "",
     "birthdate": "", "birthplace": "", "place": "", "job": "", "variant": "1"}
for a in sys.argv[1:]:
    k, _, v = a.partition("=")
    k = k.lstrip("-")
    if k in ("fornavn", "name"):
        f["name"] = v
    elif k in ("efternavn", "etternavn", "surname"):
        f["surname"] = v
    elif k in ("faar", "birthyear"):
        a1, _, a2 = v.partition("-")
        f["birthyearfrom"], f["birthyearto"] = a1, a2 or a1
    elif k in ("fsted", "birthplace"):
        f["birthplace"] = v
    elif k in ("sted", "place"):
        f["place"] = v
    elif k in ("stilling", "job"):
        f["job"] = v

d = urllib.parse.urlencode(f).encode()
t = urllib.request.urlopen(urllib.request.Request(URL, data=d, headers=UA),
                           timeout=180).read().decode("utf-8", "replace")
raek = re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", t)
n = 0
for rk in raek:
    c = [re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", x))).strip()
         for x in re.findall(r"(?is)<td[^>]*>(.*?)</td>", rk)]
    c = [x for x in c if x]
    if len(c) >= 3:
        n += 1
        pf = re.search(r"pfid=(\d+)", rk)
        print("%-9s %s" % (pf.group(1) if pf else "-", " | ".join(c)[:170]))
if not n:
    flad = re.sub(r"\s+", " ", H.unescape(
        re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", t)))
    i = flad.lower().find("treff")
    print(flad[max(0, i - 300):i + 400] if i > 0 else flad[:600])
print("\n%d raekker" % n)
