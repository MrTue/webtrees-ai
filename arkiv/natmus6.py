# -*- coding: utf-8 -*-
"""natmus6.py --efter X --for Y --rederi Z --skib Q [--foedt dd-mm-aaaa]
Frihedsmuseets base 'I allieret tjeneste', afdelingen CIVILE SOEFOLK.
Typen skiftes med en aegte ASP.NET-postback foerst; foerst derefter
hedder felterne TextBoxRederi og TextBoxSkib."""
import urllib.request, urllib.parse, http.cookiejar, ssl, sys, re, html as H

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0",
      "Content-Type": "application/x-www-form-urlencoded",
      "Referer": "https://allieret.natmus.dk/"}
URL = "https://allieret.natmus.dk/"
P = "ctl00$indhold$"
op = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
    urllib.request.HTTPSHandler(context=CTX))
a = dict(zip(sys.argv[1::2], sys.argv[2::2]))


def hent(data=None):
    b = urllib.parse.urlencode(data, encoding="utf-8").encode() if data else None
    return op.open(urllib.request.Request(URL, data=b, headers=UA),
                   timeout=90).read().decode("utf-8", "replace")


def skjulte(h):
    return {m.group(1): H.unescape(m.group(2)) for m in
            re.finditer(r'<input type="hidden" name="([^"]+)"[^>]*value="([^"]*)"', h)}


f = skjulte(hent())
f["__EVENTTARGET"] = P + "DropDownListType"
f["__EVENTARGUMENT"] = ""
f[P + "DropDownListType"] = "2"
f[P + "TextBoxFornavne"] = ""
f[P + "TextBoxEfternavne"] = ""
f[P + "TextBoxTjenesteland"] = ""
f[P + "TextBoxEnhed"] = ""
side2 = hent(f)

d, mnd, aar = (a.get("--foedt", "--") + "--").split("-")[:3] if "--foedt" in a else ("", "", "")
g = skjulte(side2)
g[P + "DropDownListType"] = "2"
g[P + "TextBoxFornavne"] = a.get("--for", "")
g[P + "TextBoxEfternavne"] = a.get("--efter", "")
g[P + "PartialDateControlFødt$dateTextBox"] = d
g[P + "PartialDateControlFødt$monthTextBox"] = mnd
g[P + "PartialDateControlFødt$yearTextBox"] = aar
g[P + "PartialDateControlDød$dateTextBox"] = ""
g[P + "PartialDateControlDød$monthTextBox"] = ""
g[P + "PartialDateControlDød$yearTextBox"] = ""
g[P + "TextBoxRederi"] = a.get("--rederi", "")
g[P + "TextBoxSkib"] = a.get("--skib", "")
g[P + "ButtonSoeg"] = "Søg i databasen"
res = hent(g)

flad = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", res)))
m = re.search(r"(\d+) personer som matcher", flad)
print("ANTAL:", m.group(1) if m else "?", "|", a)
for row in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", res):
    if "person.aspx" not in row:
        continue
    c = [re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", x))).strip()
         for x in re.findall(r"(?s)<td[^>]*>(.*?)</td>", row)]
    lnk = re.search(r'href="([^"]+)"', row)
    c = (c + ["", "", ""])[:3]
    print("  | %-40s %-20s %-26s %s" % (c[0], c[1], c[2], lnk.group(1) if lnk else ""))
