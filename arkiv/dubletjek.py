# -*- coding: utf-8 -*-
"""dubletjek.py -- finder personer i traeet, der baerer samme navn.

Dubletter opstaar let, naar der handles paa en xref-liste i stedet for paa navnene:
en familie har fem boern, og et «sjette» bliver oprettet, som i virkeligheden er et
af de fem. Denne kontrol fanger dem bagefter -- ogsaa dem, der har staaet laenge.

    python arkiv\\dubletjek.py
    python arkiv\\dubletjek.py --fra 500       # kun poster fra og med X500

Kraever facit.json (koer `facit.py` foerst).

DEN STOEJER MED VILJE. Slaegten kalder op efter doede boern -- et nyt barn faar den
afdoede soeskendes navn -- saa de fleste traef er AEGTE navnefaeller, ikke dubletter.
Kontrollen viser derfor foedselsaar og familie ved siden af, saa de kan skilles ad
paa et blik. Et par med SAMME FOEDSELSDAG er naesten altid en dublet.

Navnene normaliseres foer sammenligningen: smaa bogstaver, aeoeaa foldet ud,
ph->f, th->t, ch->k, c->k, w->v, z->s, aa->a, og ordene sorteres som en maengde,
saa «Anne Sophie Eksempelsen» og «Eksempelsen, Anne Sofie» rammer hinanden.
"""
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")

ERSTAT = [("ph", "f"), ("th", "t"), ("ch", "k"), ("z", "s"),
          ("c", "k"), ("w", "v"), ("aa", "a")]


def facitsti():
    for sti in (os.path.join((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH", "")), "facit.json"),
                "facit.json",
                os.path.join(os.path.dirname(__file__), "facit.json")):
        if sti and os.path.exists(sti):
            return sti
    sys.exit("facit.json blev ikke fundet. Koer facit.py foerst.")


def noegle(navn):
    n = unicodedata.normalize("NFKD", navn.lower())
    n = "".join(c for c in n if c.isalpha() or c == " ")
    for a, b in ERSTAT:
        n = n.replace(a, b)
    ord_ = sorted(set(n.split()))
    return " ".join(ord_) if len(ord_) > 1 else ""      # ét ord alene er for lidt


def foerste(p, praefiks):
    for f in p.get("fakta", []):
        linjer = f["tekst"].split("\n")
        if linjer[0].startswith(praefiks):
            for l in linjer[1:]:
                if l.strip().startswith("2 DATE "):
                    return l.strip()[7:]
            return "-"
    return ""


def main():
    fra = 0
    if "--fra" in sys.argv:
        fra = int(sys.argv[sys.argv.index("--fra") + 1])

    sti = facitsti()
    d = json.load(io.open(sti, encoding="utf-8"))
    print("poster i traeet: %d   (%s)" % (len(d), sti))

    pers = {x: p for x, p in d.items()
            if p.get("slags") == "PERSON" and re.match(r"^X\d+$", x)}
    idx = {}
    for x, p in pers.items():
        for f in p.get("fakta", []):
            linje = f["tekst"].split("\n")[0]
            if not linje.startswith("1 NAME"):
                continue
            k = noegle(linje[7:].replace("/", ""))
            if k:
                idx.setdefault(k, set()).add(x)

    par = [(k, sorted(v, key=lambda a: int(a[1:])))
           for k, v in idx.items() if len(v) > 1]
    par = [(k, xs) for k, xs in par
           if any(int(x[1:]) >= fra for x in xs)]
    par.sort(key=lambda kv: kv[0])

    print("navnenoegler baaret af mere end een person: %d%s"
          % (len(par), ("   (kun fra X%d)" % fra) if fra else ""))
    if not par:
        print("\n0 navnefaeller")
        return 0

    mistanke = 0
    print("")
    for k, xs in par:
        foedt = [foerste(pers[x], "1 BIRT") or foerste(pers[x], "1 CHR") for x in xs]
        ens = len([f for f in foedt if f and f != "-"]) > 1 and \
            len(set(f for f in foedt if f and f != "-")) == 1
        mark = "   <== SAMME DATO, TJEK DEN" if ens else ""
        if ens:
            mistanke += 1
        print("  %s%s" % (k[:46], mark))
        for x, f in zip(xs, foedt):
            navne = [l.split("\n")[0][7:].replace("/", "").strip()
                     for l in [g["tekst"] for g in pers[x]["fakta"]]
                     if l.startswith("1 NAME")]
            fam = [g["tekst"].split("\n")[0] for g in pers[x]["fakta"]
                   if g["tekst"].startswith(("1 FAMC", "1 FAMS"))]
            print("      %-7s %-32s f. %-14s %s"
                  % (x, " / ".join(navne)[:32], f or "?", " ".join(fam)))
        print("")

    print("%d par med samme foedselsdato -- dem foerst." % mistanke)
    print("Resten er som regel opkaldelser: et barn med en doed soeskendes navn.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
