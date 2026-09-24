# -*- coding: utf-8 -*-
"""bovrup.py -- soeg i Bovrup-kartoteket hos Danske Slaegtsforskere.

    python arkiv\\bovrup.py Eksempelsen Prøvesen       # efternavne
    python arkiv\\bovrup.py --fritekst Silkeborg       # fuldtekst
    python arkiv\\bovrup.py --fornavn Anders --efternavn Eksempelsen

Kartoteket er DNSAP's medlemsliste (Bovrup-kartoteket), 18.670 personer af den
samlede liste paa 22.792. Danske Slaegtsforskere har renset den: alle er
efterprøvet døde i mindst ti aar. Databasen har ophavsret hos foreningen, saa
tag kun det, der skal bruges, og skriv kilden.

Formularen er POST til BovrupList.php med felterne fulltext, enavn, fnavn,
stilling, bopael, omraade. Svaret er én tabel; der vises hoejst 200 raekker,
og overskriften siger, hvor mange der er i alt.
"""
import html
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://slaegtsbibliotek.dk/bovrup/BovrupList.php"
FELTER = ("fulltext", "enavn", "fnavn", "stilling", "bopael", "omraade")
KOL = ("Efternavn", "Fornavn", "Stilling", "Bopæl", "Område", "Side", "Fødselsdag", "Indmeldt")


def soeg(**par):
    """Returnerer (antal_i_alt, [raekker]) -- hver raekke er en dict."""
    data = {f: "" for f in FELTER}
    data.update({k: v for k, v in par.items() if v})
    krop = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        URL, data=krop,
        headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"})
    h = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")

    m = re.search(r"ud af i alt\s*([\d.]+)\s*fundne", h)
    antal = int(m.group(1).replace(".", "")) if m else 0

    raekker = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", h, re.S):
        celler = [html.unescape(re.sub(r"<[^>]+>", "", c)).replace("\xa0", " ").strip()
                  for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(celler) >= 8 and celler[0] and "Efternavn" not in celler[0]:
            raekker.append(dict(zip(KOL, celler)))
    return antal, raekker


def vis(overskrift, antal, raekker):
    print("== %s: %d" % (overskrift, antal))
    for r in raekker[:25]:
        print("   %(Efternavn)s, %(Fornavn)s -- %(Stilling)s, %(Bopæl)s (%(Område)s) "
              "f. %(Fødselsdag)s, indmeldt %(Indmeldt)s" % r)
    if antal > len(raekker):
        print("   ... %d flere; indsnaevr soegningen" % (antal - len(raekker)))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "--fritekst":
        n, r = soeg(fulltext=" ".join(a[1:]))
        vis(" ".join(a[1:]), n, r)
    elif "--efternavn" in a or "--fornavn" in a:
        par = {}
        for i, x in enumerate(a):
            if x == "--efternavn":
                par["enavn"] = a[i + 1]
            if x == "--fornavn":
                par["fnavn"] = a[i + 1]
            if x == "--bopael":
                par["bopael"] = a[i + 1]
        n, r = soeg(**par)
        vis(str(par), n, r)
    else:
        for navn in a:
            n, r = soeg(enavn=navn)
            vis(navn, n, r)
