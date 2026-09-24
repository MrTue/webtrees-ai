# -*- coding: utf-8 -*-
"""gentagtjek.py -- finder personer, der har den samme livshændelse to gange.

    python arkiv\\gentagtjek.py            # alle
    python arkiv\\gentagtjek.py --fra 1850 # kun poster fra og med X1850

En person bliver født, døbt, konfirmeret, død og begravet **én gang hver**. Står en
af dem to gange, er det enten en dublet -- eller to kilder, der siger noget
forskelligt. **Kontrollen kan ikke selv se forskel, og det skal den heller ikke.**
Den sorterer i stedet i tre bunker:

 * **ORDRET ENS** -- tegn for tegn den samme tekst. Det er altid en fejl, og
   `arkiv/fjerndublet.py` fjerner den uden tab.
 * **DEN ENE INDEHOLDT I DEN ANDEN** -- fx en nøgen `1 BIRT` med dato og kilde ved
   siden af en med samme dato, samme kilde, plus sted og note. Den nøgne kan væk;
   brug `fjernnoter2.py` og skriv nok af teksten til at ramme netop den.
 * **FORSKELLIGE** -- to udsagn med hver sin kilde. **Rør dem ikke.** Det er sådan
   træet skal se ud, når en trykt slægtsbog og en kirkebog er uenige om dødsdagen,
   eller når tre kilder hver bidrager til den samme begravelse.

Den er en **revision**, ikke en af de fem faste kontroller -- kør den, når der er
oprettet mange personer, ligesom `dubletjek.py`.

Baggrund: en dåb, der tilføjes med `add-fact` efter et `add-child`, der allerede fik
`1 CHR` med, står bagefter to gange. Den slags fejl er let at lave og svær at se.
"""
import io
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

SLAGS = ("BIRT", "CHR", "DEAT", "BURI", "CREM", "CONF", "BAPM")


def find_facit():
    for sti in (os.path.join((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH", "")), "facit.json"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "facit.json"),
                "facit.json"):
        if sti and os.path.exists(sti):
            return os.path.abspath(sti)
    raise SystemExit("facit.json ikke fundet -- koer arkiv\\facit.py foerst "
                     "(og saet $env:SLAEGT_ARBEJDSMAPPE)")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def navn(p):
    for f in p["fakta"]:
        if f["tekst"].startswith("1 NAME"):
            return f["tekst"].split("\n")[0][7:].replace("/", "").strip()
    return "?"


def main():
    fra = 0
    if "--fra" in sys.argv:
        fra = int(sys.argv[sys.argv.index("--fra") + 1])
    sti = find_facit()
    d = json.load(io.open(sti, encoding="utf-8"))
    print("poster i traeet: %d   (%s)\n" % (len(d), sti))

    bunker = {"ordret": [], "indeholdt": [], "forskellige": []}
    for x, p in d.items():
        if p.get("slags") != "PERSON":
            continue
        if fra and (not x[1:].isdigit() or int(x[1:]) < fra):
            continue
        efter = defaultdict(list)
        for f in p["fakta"]:
            k = f["tekst"].split()
            if len(k) > 1 and k[1] in SLAGS:
                efter[k[1]].append(f["tekst"])
        for slag, liste in efter.items():
            if len(liste) < 2:
                continue
            n = [norm(t) for t in liste]
            if len(set(n)) < len(n):
                bunke = "ordret"
            elif any(a != b and (a.startswith(b) or b.startswith(a)) for a in n for b in n):
                bunke = "indeholdt"
            else:
                bunke = "forskellige"
            bunker[bunke].append((x, navn(p), slag, len(liste), liste))

    for bunke, overskrift, raad in (
            ("ordret", "ORDRET ENS -- altid en fejl", "python arkiv\\fjerndublet.py %s"),
            ("indeholdt", "DEN ENE INDEHOLDT I DEN ANDEN -- den korte kan sandsynligvis vaek",
             "brug fjernnoter2.py paa %s"),
            ("forskellige", "FORSKELLIGE -- to kilder, der siger hver sit. ROER DEM IKKE", None)):
        raekker = bunker[bunke]
        print("== %s: %d" % (overskrift, len(raekker)))
        for x, nv, slag, n, liste in raekker:
            print("   %-7s %-40s %s x%d" % (x, nv[:40], slag, n))
            if bunke != "forskellige":
                for t in liste:
                    print("        | %s" % " / ".join(l.strip() for l in t.split("\n")[:3])[:120])
        if raad and raekker:
            print("   -> %s" % (raad % " ".join(sorted({r[0] for r in raekker}))))
        print()

    fejl = len(bunker["ordret"]) + len(bunker["indeholdt"])
    print("%d der skal rettes, %d der skal staa" % (fejl, len(bunker["forskellige"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
