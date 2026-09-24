# -*- coding: utf-8 -*-
"""ddd6.py <amt> <aar> [--navn X] [--navn2 Y] [--og] [--alder N] [--sogn X]

Som `ddd5.py`, men med BEGGE navnefelter og navnelogikken, saa man kan kraeve to
ord i det SAMME navn:

    python ddd6.py Sorø 1845 --navn Skov --navn2 Karen --og

**Det er den vigtigste soegeform i praksis.** En ren soegning paa \u00abSkov\u00bb i et amt
giver hundredvis af Skovsted, Skovby, Noerskov og Oesterskov, fordi operatoren er
\u00abindeholder\u00bb. Med to ord og `--og` bliver listen brugbar.

Uden `--og` er logikken ELLER, alts\u00e5 navne der indeholder det ene ELLER det andet.

**AMT ER OBLIGATORISK** \u2014 se `ddd5.py` for hvorfor, og for hele diagnosen af den
omlagte soegeside. **Aaret kan v\u00e6re `alle`.**

**FELTET `f\u00f8dested` VIRKER IKKE.** Det findes i formularen, men serveren ignorerer
det, uanset hvordan det sendes. Man kan alts\u00e5 ikke soege \u00aballe f\u00f8dt i et bestemt sogn\u00bb.
Naar man har fundet en person, giver `dddperson.py` derimod b\u00e5de f\u00f8dested og hele
husstanden.
"""
from pathlib import Path
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")
import ddd5  # noqa: E402


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__.split("\n\n")[0])

    def flag(navn, d=""):
        return a[a.index(navn) + 1] if navn in a else d

    amt, aar = a[0], a[1]
    f = [("kipnr", ""), ("stednavn", ""), ("county", amt), ("herred", ""),
         ("parish", flag("--sogn")), ("navn", flag("--navn")),
         ("navn2", flag("--navn2")), ("operator", "3"),
         ("navnelogik", "And" if "--og" in a else "OR"), ("erhverv", ""),
         ("f\u00f8dested", ""), ("alder_valg", ""), ("alder", flag("--alder")),
         ("faarb", ""), ("interval", "2"), ("sex", ""), ("kilde", aar),
         ("sorter", "a.navn"), ("sorter2", "b.aarfra")]
    # utf-8, ikke windows-1252 — se noten i ddd5.soeg(). Amter med æøå gav 500.
    d = urllib.parse.urlencode(f, encoding="utf-8").encode()
    t = urllib.request.urlopen(
        urllib.request.Request(ddd5.URL, data=d, headers=ddd5.UA), timeout=300
    ).read().decode("windows-1252", "replace")

    s = ddd5.flad(t)
    m = re.search(r"([\d.]+)\s+poster fundet", s)
    # Ved NUL traef skriver serveren slet ingen "poster fundet"-linje. Uden det her
    # ville et tomt resultat se ud som en fejl.
    print("%s poster fundet i %s" % (m.group(1) if m else "0", amt))
    if "Kun 250 poster vises" in s:
        print("** KUN 250 VISES \u2014 snaevr soegningen **")
    for p in ddd5.poster(t):
        print("%-32s %-4s %-22s %-20s %-10s lbnr=%s" % (
            p.get("Navn", "")[:32], p.get("Alder", "")[:4],
            p.get("Sogn", "")[:22], p.get("F\u00f8dested", "")[:20],
            p.get("KIPnr", "")[:10], p.get("Lbnr", "")))


if __name__ == "__main__":
    main()
