# -*- coding: utf-8 -*-
"""avis.py — Mediestream, Det Kgl. Biblioteks digitaliserede aviser 1666-2013.

    python avis.py <soegeord> [<soegeord> ...]      maal navnet i pressen
    python avis.py --tekst <soegeord> [maks]        laes de frie artikler
    python avis.py --aar <soegeord>                 traef aarti for aarti

TRE DOERE I API'ET, og de har hver sin begraensning:

    /aviser/hits            antal traef delt i "public" (aeldre end 140 aar,
                            frit tilgaengeligt) og "restricted". Virker paa
                            HELE perioden. Tager KUN parameteren `query` —
                            aarstal skal ind i selve soegningen som py:[a TO b].
    /aviser/export/fields   selve teksten, men KUN aviser aeldre end 140 aar.
    /aviser/stats/timeline  traef per aar.

FLERE ORD BLIVER TIL ET FRASESOEG. Uden anfoerselstegn soeger Mediestream
OR — et navn paa tre ord som «Anders Eksempel Prøvesen» giver titusinder af traef,
fordi den finder alt med *Anders* eller *Eksempel* eller *Prøvesen*. Scriptet saetter derfor selv anfoerselstegn om
flerordede soegeord. Skriv `--raat` foerst for at slaa det fra og bruge
Solr-syntaks direkte.

NYTTIGE FELTER I QUERY: py:[1880 TO 1890] (aar) · lplace:Svendborg (udgivelsessted)
familyId:"fyensstiftstidende" (avistitel).
"""
import csv
import io
import json
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
API = "https://labs.statsbiblioteket.dk/labsapi/api/aviser"
UA = {"User-Agent": "slaegtsforskning/1.0"}
VINDUER = [(1666, 1799), (1800, 1849), (1850, 1879), (1880, 1899),
           (1900, 1919), (1920, 1949), (1950, 1979), (1980, 2013)]


def hent(sti, *par, **p):
    """par er (navn, vaerdi)-par, saa `fields` kan gentages, som API'et kraever."""
    dele = list(par) + list(p.items())
    u = API + sti + "?" + urllib.parse.urlencode(dele)
    return urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=180).read()


def frase(q, raat=False):
    if raat or '"' in q or ":" in q:
        return q
    return '"%s"' % q if " " in q.strip() else q


def hits(q):
    d = json.loads(hent("/hits", query=q))
    return d.get("public", 0), d.get("restricted", 0)


def link(q):
    return "https://www2.statsbiblioteket.dk/mediestream/avis/search/" + \
        urllib.parse.quote(q, safe="")


FELTER = ("familyId", "timestamp", "lplace", "newspaper_page", "link",
          "fulltext_org")


def tekst(q, maks=20):
    """Henter de frit tilgaengelige artikler (aeldre end 140 aar)."""
    par = [("query", q), ("max", str(maks))]
    par += [("fields", f) for f in FELTER]
    par += [("structure", "content"), ("format", "CSV")]
    return hent("/export/fields", *par).decode("utf-8", "replace")


def maal(q):
    pub, res = hits(q)
    print("%-42s frit:%-6d spærret:%-7d i alt:%d" % (q[:42], pub, res, pub + res))
    print("      %s" % link(q))
    return pub, res


def aar(q):
    print(q)
    for a, b in VINDUER:
        p, r = hits("(%s) AND py:[%d TO %d]" % (q, a, b))
        if p + r:
            print("   %4d-%4d  %6d   (frit %d)" % (a, b, p + r, p))


if __name__ == "__main__":
    arg = sys.argv[1:]
    raat = "--raat" in arg
    arg = [a for a in arg if a != "--raat"]
    if not arg:
        print(__doc__)
        raise SystemExit(1)
    if arg[0] == "--aar":
        for q in arg[1:]:
            aar(frase(q, raat))
    elif arg[0] == "--tekst":
        q = frase(arg[1], raat)
        m = arg[2] if len(arg) > 2 else "20"
        ud = tekst(q, m)
        r = csv.reader(io.StringIO(ud))
        for i, row in enumerate(r):
            print(" | ".join(row)[:1500])
            if i > int(m) + 2:
                break
    else:
        for q in arg:
            maal(frase(q, raat))
