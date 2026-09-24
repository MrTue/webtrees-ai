# -*- coding: utf-8 -*-
"""banditter.py — indsatte i danske arrester, faengsler og tugthuse 1752-1932.

banditter.dk er Danske Slaegtsforskere Odenses indtastning af fangeprotokoller.
Dertil "offentlige fruentimmere", som var registreret hos politiet uden at vaere
indsat. Gratis, ingen login. Siden er ASP.NET WebForms, saa der skal et
viewstate-omloeb til: hent formularen, ekko de skjulte felter tilbage.

    python banditter.py --efternavn=Eksempelsen
    python banditter.py --fornavn=Anders --efternavn=Eksempelsen --faar=1815-1825
    python banditter.py --efternavn=Eksempelsen --sted=Viborg

Brug IKKE jokertegn — siden normaliserer selv stavemaader.
"""
import re
import sys
import urllib.parse
import urllib.request
import html as H
import http.cookiejar

sys.stdout.reconfigure(encoding="utf-8")
URL = "https://banditter.dk/"
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0",
      "Content-Type": "application/x-www-form-urlencoded",
      "Referer": URL}
P = "ctl00$ContentPlaceHolder1$"

op = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def skjulte(t):
    ud = {}
    for m in re.finditer(r'(?is)<input[^>]*type="hidden"[^>]*>', t):
        n = re.search(r'name="([^"]+)"', m.group(0))
        v = re.search(r'value="([^"]*)"', m.group(0))
        if n:
            ud[n.group(1)] = H.unescape(v.group(1)) if v else ""
    return ud


felt = {"fornavn": "TB_Fornavn", "efternavn": "TB_Efternavn", "sted": "TB_Place",
        "forbrydelse": "TB_Forbrydelse"}
data = {}
for a in sys.argv[1:]:
    k, _, v = a.partition("=")
    k = k.lstrip("-")
    if k in felt:
        data[P + felt[k]] = v
    elif k in ("faar", "foedeaar"):
        a1, _, a2 = v.partition("-")
        data[P + "TB_Born_Fra"], data[P + "TB_Born_To"] = a1, a2 or a1
    elif k in ("indsat",):
        a1, _, a2 = v.partition("-")
        data[P + "TB_Fra"], data[P + "TB_To"] = a1, a2 or a1
if not data:
    raise SystemExit(__doc__)

t = op.open(urllib.request.Request(URL, headers=UA), timeout=120).read().decode("utf-8", "replace")
f = skjulte(t)
for n in ("TB_Fornavn", "TB_Efternavn", "TB_Place", "TB_Forbrydelse",
          "TB_Born_Fra", "TB_Born_To", "TB_Fra", "TB_To"):
    f.setdefault(P + n, "")
f.update(data)
f[P + "Button1"] = "Søg"

d = urllib.parse.urlencode(f, encoding="utf-8").encode()
t2 = op.open(urllib.request.Request(URL, data=d, headers=UA), timeout=180).read().decode("utf-8", "replace")

n = 0
for rk in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", t2):
    c = [re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", x))).strip()
         for x in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", rk)]
    c = [x for x in c if x]
    if len(c) >= 3:
        n += 1
        print(" | ".join(c)[:180])
if not n:
    flad = re.sub(r"\s+", " ", H.unescape(
        re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", t2)))
    i = flad.find("Søg efter indsatte")
    print(flad[max(0, i - 400):i + 200] if i > 0 else flad[:600])
print("\n%d raekker" % n)
