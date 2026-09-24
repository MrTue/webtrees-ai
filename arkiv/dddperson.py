# -*- coding: utf-8 -*-
"""dddperson.py <amt> <kipnr> <lbnr> — alle felter for én person i DDD.

Soegeresultatet fra `ddd5.py` rummer for hver post en lille formular:

    POST https://www.ddd.dda.dk/asp/alle_opl.asp
    felter: amt, indtastningsnr (KIP-nummeret), lbnr

Den giver **hele den indtastede raekke**, ogsaa de felter, soegesvaret ikke
viser — og i tyske taellinger fra Soenderjylland er det dér, husstandens
sammenhaeng staar.

Der er ogsaa en knap til dokumentationen for hele indtastningen:

    POST https://www.ddd.dda.dk/asp/doku_dk.asp   felt: indtastningsnr
"""
import html as H
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
URL = "https://www.ddd.dda.dk/asp/alle_opl.asp"
UA = {"User-Agent": "Mozilla/5.0",
      "Content-Type": "application/x-www-form-urlencoded",
      "Referer": "https://www.ddd.dda.dk/soeg_person.asp"}


def hent(amt, kip, lbnr):
    d = urllib.parse.urlencode(
        {"amt": amt, "indtastningsnr": kip, "lbnr": str(lbnr)},
        encoding="utf-8").encode()  # utf-8 som i ddd5/ddd6 — ellers 500 på æøå
    return urllib.request.urlopen(
        urllib.request.Request(URL, data=d, headers=UA), timeout=180
    ).read().decode("windows-1252", "replace")


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__.split("\n\n")[0])
    t = hent(sys.argv[1], sys.argv[2], sys.argv[3])
    flad = re.sub(r"[ \t]+", " ", H.unescape(
        re.sub(r"(?is)<br\s*/?>|</tr>|</p>", "\n", re.sub(r"(?is)<[^>]+>", " ", t))))
    for linje in flad.split("\n"):
        linje = linje.strip()
        if linje:
            print(linje)


if __name__ == "__main__":
    main()
