# -*- coding: utf-8 -*-
"""njavis.py -- søg i NORDJYSKEs Historiske Avisarkiv (nordjyske-avisarkiv.dk).

    python arkiv\\njavis.py "Anders Eksempelsen" 1985-03-10 1985-03-17
    python arkiv\\njavis.py "Karen Eksempelsen" 1978-06-02 1978-06-09 --udgivelse "Thisted Dagblad"

**Scriptet viser arkivets gratis søgeuddrag**: et kort OCR-uddrag omkring træfordet,
som arkivet selv viser ved hver søgning. Selve siden kræver abonnement. Uddraget er
nok til at se, om og hvornår et navn står i avisen — er teksten lang, er den klippet
i begge ender.

Arkivet rummer **Vendsyssel Tidende 1873-1999** (to udgaver: Hjørring og Frederikshavn),
**Aalborg Stiftstidende 1767-1999**, NORDJYSKE Stiftstidende, Frederikshavn Avis,
Thisted Dagblad, Morsø Folkeblad, Løgstør Avis, Fjerritslev Avis og Skagens Avis.
**Aalborg Amtstidende og Nordjyllands Social-Demokrat er IKKE med.**

Søgetips fra arkivet selv:
 * Sæt navne i **citationstegn**, ellers søges der på hvert ord for sig med «og» imellem
   — og hvert ord matcher også alle længere ord, der begynder sådan.
 * **Skriv ikke punktum i forkortelser**: «Anders Chr Eksempelsen», ikke «Anders Chr. Eksempelsen».
 * Teksten er OCR af mikrofilm. Et navn, du ved står der, kan være ulæseligt — prøv en
   anden ordlyd, og husk at aviser før 1948 skriver navneord med stort.
 * **Uddraget kan løbe to nabospalter sammen.** To dødsannoncer ved siden af hinanden
   bliver til én tekstklump, så læs efter, hvor den ene slutter.
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://nordjyske-avisarkiv.dk/soegning"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")


def soeg(ord_, fra, til, forsoeg=3):
    """Returnerer [{avis, dato, uddrag}] -- fra og til er «ÅÅÅÅ-MM-DD»."""
    # VIGTIGT: mellemrum skal være %20, ikke +. Med + falder citationstegnene ud af kraft,
    # og «"Anders Eksempelsen"» bliver til to løsrevne ord -- mange flere træf end frasen.
    p = "from=%s&to=%s&searchterm=%s" % (fra, til, urllib.parse.quote(ord_, safe=""))
    req = urllib.request.Request(URL + "?" + p, headers={"User-Agent": UA})
    for n in range(forsoeg):
        try:
            h = urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "replace")
            break
        except Exception as e:
            if n == forsoeg - 1:
                raise
            time.sleep(3)

    ud = []
    # Hver traef er en blok med avisnavn + dato i en overskrift og uddraget i et afsnit.
    for blok in re.split(r'(?i)<(?:li|article|div)[^>]*class="[^"]*(?:result|traef|hit)[^"]*"', h)[1:]:
        ud.append(blok)
    if not ud:
        ud = [h]

    svar, set_ = [], set()
    # Overskriftslinjen ser ud som «<avis> - <udgave> - 14/03 1985».
    m = re.finditer(r'>([^<>]{3,60}?)\s*-\s*(\d{2}/\d{2}\s*\d{4})\s*<', h)
    pos = [(x.start(), html.unescape(x.group(1)).strip(), x.group(2).replace(" ", "")) for x in m]
    tekster = [(x.start(), re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x.group(1)))).strip())
               for x in re.finditer(r'(?is)Tekstudsnit:\s*</?[^>]*>(.{20,4000}?)(?:Se siden|</li>|</article>)', h)]
    for start, avis, dato in pos:
        naeste = [t for p_, t in tekster if p_ > start]
        uddrag = naeste[0] if naeste else ""
        noegle = (avis, dato)
        if noegle in set_:
            continue
        set_.add(noegle)
        d, mnd, aar = re.match(r"(\d{2})/(\d{2})(\d{4})", dato).groups()
        svar.append({"avis": avis, "dato": "%s-%s-%s" % (aar, mnd, d), "uddrag": uddrag})
    return svar


def vis(ord_, fra, til):
    r = soeg(ord_, fra, til)
    print("== «%s»  %s .. %s   -- %d træf" % (ord_, fra, til, len(r)))
    for x in r:
        print("\n  %s  %s" % (x["dato"], x["avis"]))
        t = x["uddrag"]
        for i in range(0, len(t), 110):
            print("     %s" % t[i:i + 110])
    print()
    return r


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) < 3:
        sys.exit(__doc__)
    # PowerShell æder citationstegn i argumenter, så de kan ikke skrives med på
    # kommandolinjen. Derfor sættes de på HER: flere ord søges som én frase,
    # med mindre --ord er angivet.
    ord_ = a[0]
    if " " in ord_ and '"' not in ord_ and "--ord" not in sys.argv:
        ord_ = '"%s"' % ord_
    vis(ord_, a[1], a[2])
