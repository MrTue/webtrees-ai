# -*- coding: utf-8 -*-
"""Demografisk Databas Soedra Sverige (DDSS) som frit CC0-datasaet fra Riksarkivet.

Riksarkivets egne soegeformularer paa sok.riksarkivet.se er ALTCHA-beskyttede og kan
ikke bruges maskinelt. Hele indholdet ligger til gengaeld frit til download, og det er
baade hurtigere og mere fleksibelt at soege i lokalt.

  python arkiv\\dds.py --hent                     # henter de tre zip-filer (167 MB)
  python arkiv\\dds.py foedte Blekinge  Datum~1862-04-11
  python arkiv\\dds.py foedte _fodelse  Datum~1862- Fornamn~per Far_fornamn~olof
  python arkiv\\dds.py doede  Blekinge  Forsamling=Ronneby Datum~1877-
  python arkiv\\dds.py viede  Vasternorrland  Brudgum_efternamn~nyman
  python arkiv\\dds.py --daekning foedte Blekinge 1860   # hvilke sogne har det aar?

Andet argument er en delstreng af filnavnet i zip'en (et laen, eller "_fodelse" for
alle). Derefter foelger krav: "kol=vaerdi" er noejagtigt, "kol~tekst" er indeholder.
Alt er smaa/store-ufoelsomt.

FAELDER
  * Filerne er kodet **cp1252**, ikke UTF-8. Semikolon skiller felterne.
  * `Datum_avser` siger, om `Datum` er foedsel eller daab -- tjek den, foer et
    negativt resultat skrives ned.
  * Privatliv: foedselsregistret mangler alt fra **1915**, vielsesregistret fra **1930**.
  * **Daekningen er ujaevn.** For aaret 1860 har foedselsregistret poster fra 13 af
    Blekinge laens 32 sogne og 19 af Vaesternorrlands 24.
    Koer `--daekning`, foer et nul kaldes et negativt resultat.
  * Laen med data: Blekinge, Halland (kun eet sogn), Jaemtland, Kristianstad,
    Malmoehus, Vaesternorrland -- og Gotland i doede og viede.
"""
import csv
import io
import os
import sys
import urllib.request
import zipfile
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

MAPPE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dds")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0 Safari/537.36"

SAET = {
    "foedte": ("Fodelse_csv.zip",
               "https://filer.riksarkivet.se/registerdata/DDS/Fodda/Fodelse_csv.zip"),
    "doede": ("Doda_csv.zip",
              "https://filer.riksarkivet.se/registerdata/DDS/Doda/Doda_csv.zip"),
    "viede": ("Vigsel_csv.zip",
              "https://filer.riksarkivet.se/registerdata/DDS/Vigslar/Vigsel_csv.zip"),
}


def hent():
    os.makedirs(MAPPE, exist_ok=True)
    for navn, url in SAET.values():
        sti = os.path.join(MAPPE, navn)
        if os.path.exists(sti):
            print("findes", sti, os.path.getsize(sti))
            continue
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=900) as r, open(sti, "wb") as f:
            n = 0
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                f.write(b)
                n += len(b)
        print("hentet", sti, "%.1f MB" % (n / 1e6))


def raekker(saet, filmatch):
    sti = os.path.join(MAPPE, SAET[saet][0])
    if not os.path.exists(sti):
        raise SystemExit("Datasaettet mangler. Koer: python arkiv\\dds.py --hent")
    with zipfile.ZipFile(sti) as z:
        for info in z.infolist():
            if filmatch.lower() not in info.filename.lower():
                continue
            with z.open(info) as fh:
                txt = io.TextIOWrapper(fh, encoding="cp1252", newline="")
                yield info.filename, csv.DictReader(txt, delimiter=";")


def lav_krav(args):
    ud = []
    for a in args:
        if "~" in a and ("=" not in a or a.index("~") < a.index("=")):
            k, v = a.split("~", 1)
            ud.append((k, v.lower(), "i"))
        else:
            k, v = a.split("=", 1)
            ud.append((k, v.lower(), "e"))
    return ud


def passer(row, krav):
    for k, v, t in krav:
        c = (row.get(k) or "").strip().lower()
        if t == "e" and c != v:
            return False
        if t == "i" and v not in c:
            return False
    return True


def soeg(saet, filmatch, krav, maks=300):
    for navn, r in raekker(saet, filmatch):
        n = 0
        for row in r:
            if not passer(row, krav):
                continue
            n += 1
            print("---", navn)
            for k, val in row.items():
                val = (val or "").strip()
                if val and val != "NULL":
                    print("  %s: %s" % (k, val))
            if n >= maks:
                print("...afbrudt ved", maks)
                break
        print("== %s: %d traef" % (navn, n))


def daekning(saet, filmatch, aar):
    for navn, r in raekker(saet, filmatch):
        c, alle = Counter(), set()
        for row in r:
            f = (row.get("Forsamling") or "").strip()
            alle.add(f)
            if (row.get("Datum") or "").startswith(aar):
                c[f] += 1
        print("%s: %d sogne i alt, %d med poster i %s, %d poster"
              % (navn, len(alle), len(c), aar, sum(c.values())))
        print("  ", ", ".join(sorted(c)))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
    elif sys.argv[1] == "--hent":
        hent()
    elif sys.argv[1] == "--daekning":
        daekning(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        soeg(sys.argv[1], sys.argv[2], lav_krav(sys.argv[3:]))
