# -*- coding: utf-8 -*-
"""dr.py --for FORNAVN --efter EFTERNAVN [--fra 1912 --til 1925]
        [--doedfra 2000 --doedtil 2012] [--koen M|K|B] [--sted Middelfart]
Danske Slaegtsforskeres samlede doedsregister, dodsregister.dk.
CPR-numre maskeres — de maa hverken vises eller gemmes.

--sted filtrerer raekkerne paa sidste bopael eller doedssted."""
import urllib.request, urllib.parse, http.cookiejar, ssl, sys, re, html as H

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded",
      "Referer": "https://dodsregister.dk/"}
URL = "https://dodsregister.dk/"
P = "ctl00$ContentPlaceHolder1$"
CPR = re.compile(r"\b\d{6}[- ]?\d{4}\b")
a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
op = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
    urllib.request.HTTPSHandler(context=CTX))


def hent(data=None):
    b = urllib.parse.urlencode(data, encoding="utf-8").encode() if data else None
    return op.open(urllib.request.Request(URL, data=b, headers=UA),
                   timeout=120).read().decode("utf-8", "replace")


side = hent()
knap = re.findall(r'<input type="submit" name="([^"]+)"[^>]*value="([^"]*)"', side)
f = {m.group(1): H.unescape(m.group(2)) for m in
     re.finditer(r'<input type="hidden" name="([^"]+)"[^>]*value="([^"]*)"', side)}
f[P + "TB_Fornavn"] = a.get("--for", "")
f[P + "TB_Efternavn"] = a.get("--efter", "")
f[P + "UC_PeriodeF$TB_Fra"] = a.get("--fra", "")
f[P + "UC_PeriodeF$TB_Til"] = a.get("--til", "")
f[P + "UC_PeriodeD$TB_Fra"] = a.get("--doedfra", "")
f[P + "UC_PeriodeD$TB_Til"] = a.get("--doedtil", "")
f[P + "RadioButtonList1"] = a.get("--koen", "B")
for n, v in knap:
    if "Clear" not in n and "Nulstil" not in v:
        f[n] = v
res = hent(f)

sted = a.get("--sted")
print("SØGNING:", a)
n = vist = 0
for row in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", res):
    c = [re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", x))).strip()
         for x in re.findall(r"(?s)<t[dh][^>]*>(.*?)</t[dh]>", row)]
    c = [CPR.sub("******-****", x) for x in c if x]
    if len(c) < 2:
        continue
    n += 1
    linje = "  ".join(x[:46] for x in c)
    if sted and sted.lower() not in linje.lower():
        continue
    vist += 1
    print("  %3d | %s" % (n, linje))
print("rækker i alt:", n, "| vist:", vist)
