# -*- coding: utf-8 -*-
"""stedtjek.py -- efterproever, at hvert `2 PLAC` i traeet har en raekke i stedfilen.

De tre andre kontroller ser paa henvisninger og filer. INGEN AF DEM SER PAA STEDER.
Et `2 PLAC`, der ikke har en raekke i `webtrees-steder.csv`, faar ingen prik paa kortet,
og det opdager man foerst, naar man kigger paa netop den post -- eller aldrig.

    python arkiv\\stedtjek.py

Kraever facit.json (koer `facit.py` foerst).

DEN SAMMENLIGNER PAA FORM, IKKE PAA STED. Traeet skriver «Sogn, Herred, Amt, Danmark»;
stedfilen har «3;Danmark;<Amt>;<Herred>;<Sogn>;...». Skriver traeet «Viborg» og filen
«Viborg Domsogn», er det to forskellige steder for webtrees, og saa meldes det her.
Det er med vilje: den slags uoverensstemmelser er praecis dem, der ellers bliver
staaende i aarevis.

FAELDER:
 * Stedfilen er UTF-8 UDEN BOM og med CRLF. Laes den binaert og afkod selv.
 * Felter med mellemrum staar i anfoerselstegn i filen -- de skal strippes.
 * Et `2 PLAC` med faerre end fire led (fx «Eksempel, Eksempel Amt, Danmark») er en
   FORMFEJL i traeet, ikke et manglende sted. De meldes for sig.
"""
from pathlib import Path
import collections
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

STEDFIL = str(Path(__file__).resolve().parent.parent / "webtrees-steder.csv")


def facitsti():
    for sti in (os.path.join((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH", "")), "facit.json"),
                "facit.json",
                os.path.join(os.path.dirname(__file__), "facit.json")):
        if sti and os.path.exists(sti):
            return sti
    sys.exit("facit.json blev ikke fundet. Koer facit.py foerst.")


def laes_stedfil(sti):
    """Returnerer (sogne, herreder, alle_knuder).

    `alle_knuder` er HVER raekke i filen som en tuple skrevet indefra og ud --
    ogsaa niveau 0 og 1. Den bruges til knudekontrollen nedenfor.
    """
    if not os.path.exists(sti):
        sys.exit("stedfilen blev ikke fundet: %s" % sti)
    raa = io.open(sti, "rb").read()
    if raa.startswith(b"\xef\xbb\xbf"):
        print("ADVARSEL: stedfilen har BOM -- webtrees importerer den forkert.")
        raa = raa[3:]
    sogne, herreder, knuder = set(), set(), set()
    for linje in raa.decode("utf-8").split("\r\n"):
        d = linje.split(";")
        if len(d) < 6 or not d[0].isdigit():
            continue
        af = lambda i: d[i].strip('"').strip()          # noqa: E731
        if d[0] == "3":
            sogne.add((af(4), af(3), af(2), af(1)))
        elif d[0] == "2":
            herreder.add((af(3), af(2), af(1)))
        # enhver raekke er ogsaa en knude: Place0..Place3 vendt om
        dele = [af(i) for i in (1, 2, 3, 4)]
        knuder.add(tuple(reversed([p for p in dele if p])))
    return sogne, herreder, knuder


def main():
    sti = facitsti()
    d = json.load(io.open(sti, encoding="utf-8"))
    print("poster i traeet: %d   (%s)" % (len(d), sti))

    brug = collections.Counter()
    hvor = collections.defaultdict(set)
    for x, p in d.items():
        for fakta in p.get("fakta", []):
            for linje in fakta.get("tekst", "").split("\n"):
                linje = linje.strip()
                if linje.startswith("2 PLAC "):
                    v = linje[7:].strip()
                    if v:
                        brug[v] += 1
                        hvor[v].add(x)

    sogne, herreder, knuder = laes_stedfil(STEDFIL)
    print("stednavne i traeet: %d   raekker i stedfilen: %d sogne, %d herreder"
          % (len(brug), len(sogne), len(herreder)))

    # --- KNUDEKONTROL ------------------------------------------------------
    # webtrees bygger en knude for HVERT led i en stednavnesti. «Sogn,
    # Herred, Amt, Danmark» er FIRE knuder, ikke een, og en knude
    # uden raekke faar ingen koordinat -- en gul trekant i stedlisten.
    # Kontrollen ovenfor ser kun paa hele stien og overser derfor et helt AMT,
    # der mangler. Et helt amt eller herred kan staa uden raekke, mens alle
    # sogne under det er paa plads, og stien-kontrollen melder nul.
    mangler_knude = collections.defaultdict(set)
    for v in brug:
        led = [s.strip() for s in v.split(",")]
        for i in range(len(led)):
            k = tuple(led[i:])
            if k not in knuder:
                mangler_knude[k].update(hvor[v])

    mangler, formfejl, grove = [], [], []
    for v, n in sorted(brug.items()):
        led = [s.strip() for s in v.split(",")]
        if led[-1] != "Danmark":
            grove.append((v, n))            # udenlandsk -- ikke vores form
        elif len(led) == 4:
            if tuple(led) not in sogne:
                mangler.append((v, n))
        elif len(led) == 3:
            formfejl.append((v, n))         # herredet ser ud til at mangle
        else:
            grove.append((v, n))            # «Bornholm, Danmark» o.l. -- med vilje groft

    ud = 0
    if formfejl:
        ud = 1
        print("\nDANSKE 2 PLAC MED TRE LED -- HERREDET SER UD TIL AT MANGLE:")
        print("(formen skal vaere «Sogn, Herred, Amt, Danmark»)")
        for v, n in formfejl:
            print("   %-52s %d gange   %s"
                  % (v, n, ", ".join(sorted(hvor[v])[:6])))
    if mangler:
        ud = 1
        print("\nSTEDER UDEN RAEKKE I STEDFILEN:")
        for v, n in mangler:
            print("   %-52s %d gange   %s"
                  % (v, n, ", ".join(sorted(hvor[v])[:6])))
        print("\nTilfoej dem som «3;Danmark;<Amt>;<Herred>;<Sogn>;E<laengde>;N<bredde>;14;»")
        print("med SOGNEKIRKENS koordinat -- ikke landsbyens.")
    # knuder, der ikke allerede er meldt som manglende hele stier
    meldt = set(tuple(s.strip() for s in v.split(",")) for v, _ in mangler)
    resten = {k: v for k, v in mangler_knude.items() if k not in meldt}
    if resten:
        ud = 1
        print("\nMELLEMNIVEAUER UDEN RAEKKE -- GUL TREKANT I STEDLISTEN:")
        print("(sognet kan godt vaere paa plads; det er amtet eller herredet OVER det,")
        print(" der mangler. webtrees laver en knude for hvert led i stien.)")
        for k in sorted(resten, key=lambda t: (len(t), t)):
            # «Danmark» = niveau 0, «Viborg, Danmark» = 1 (amt),
            # «Odense, Odense, Danmark» = 2 (herred), fire led = 3 (sogn)
            niveau = len(k) - 1
            poster = sorted(resten[k], key=lambda x: int(x[1:]) if x[1:].isdigit() else 0)
            print("   niveau %d  %-44s %2d poster   %s"
                  % (niveau, ", ".join(k), len(poster), ", ".join(poster[:5])))
        print("\nNiveau 1 (amt) og 2 (herred) er AFRUNDEDE midtpunkter -- reglen om")
        print("sognekirkens koordinat gaelder niveau 3.")
    if not ud:
        print("\n0 steder uden raekke")
    if grove:
        print("\nTIL ORIENTERING -- udenlandske og bevidst grove steder (ikke fejl): %d"
              % len(grove))
        for v, n in grove:
            print("   %-52s %d gange" % (v, n))
    return ud


if __name__ == "__main__":
    sys.exit(main())
