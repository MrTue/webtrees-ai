# -*- coding: utf-8 -*-
"""foedtden.py <dd-mm-aaaa> [<dd-mm-aaaa> ...] [--aar] [--kgd <id>] [--csv <fil>]

FEJER HELE LANDETS KIRKEGAARDE PAA EN FOEDSELSDAG -- UDEN AT KENDE NAVNET.

Den er til det problem, som en vielsesbog ikke kan loese: **en kvinde, der forsvinder ind i et
giftenavn.** En kvinde kan soeges i flere sognes vielsesboeger uden resultat, og det kan
ikke undgaas -- man finder ikke en vielse, naar man ikke ved, hvad hun kom til at hedde.
Men **foedselsdagen foelger hende hele livet**, ogsaa paa gravstenen.

Nøglen ligger i `gravsted.py`: `AfdoedeSoeg` tager
`InFodselsAar` + `InFodselLigMed=J`, og en TOM `InSoegekriterie` giver hele kirkegaarden.
Tilsammen: hver eneste begravet i Danmark med et bestemt foedselsaar. Og svaret baerer feltet
**`AKT_EFTERNAVN`** -- «aktuelt efternavn», altsaa netop giftenavnet.

    python arkiv\\foedtden.py 14-03-1921 02-11-1924
    python arkiv\\foedtden.py 14-03-1921 --aar            # hele aargangen, ikke kun dagen
    python arkiv\\foedtden.py 14-03-1921 --kgd <id>       # én kirkegaard (til afproevning)
    python arkiv\\foedtden.py 14-03-1921 --csv ud.csv     # gem traeffene

**Proev altid `--kgd` foerst.** Serveren er Folkekirkens, ikke vores, og en landsfejning er
1.750 kald. Brug scriptet til personlig slaegtsforskning, hold lav hastighed (pause mellem
kaldene), og respekter sidens vilkaar.

DET NEGATIVE RESULTAT ER SVAGT, OG DET SKAL SKRIVES SOM SAADAN: registret daekker ca. 1.750
kirkegaarde i Folkekirkens faelles system, men **ikke alle** -- et ryddet gravsted, en
kirkegaard uden for systemet, en urne spredt over havet eller en kvinde, der ligger i udlandet,
giver alle et nul, der intet betyder. Og **den doede skal vaere doed**: lever hun, staar hun
ikke der.
"""
import csv
import io
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gravsted import KLIENT, blokke, kald  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def afdoede_aar(kgd, aar, antal=500, index=0):
    """Alle begravede paa én kirkegaard med et bestemt FOEDSELSAAR."""
    x = kald("/bsk_app/bsk_wsoffentlig_pck.AfdoedeSoeg",
             {"InKlientHttp": KLIENT, "InDBSID": "BSK", "InKirkegaardID": kgd,
              "InSoegekriterie": "", "InIndex": index, "InAntalHits": antal,
              "InFodselsAar": aar, "InFodselLigMed": "J",
              "InFodselMindreEnd": "N", "InFodselStorreEnd": "N",
              "InDodsAar": 2026, "InDodLigMed": "N",
              "InDodMindreEnd": "N", "InDodStorreEnd": "N"})
    return blokke(x, "AFDOED")


def fej(datoer, kun_aar=False, kgd_valgt=None, log=print):
    """Traef paa de givne foedselsdatoer. `datoer` er dd-mm-aaaa."""
    aargange = sorted({d[-4:] for d in datoer})
    if kgd_valgt:
        kgde = [{"KIRKEGAARD_ID": kgd_valgt, "KIRKEGAARD_NAVN": "(valgt)"}]
    else:
        # `kirkegaarde()` svarer med KIRKEGAARD_ID og KIRKEGAARD_NAVN, ikke ID/NAVN.
        from gravsted import kirkegaarde
        kgde = kirkegaarde("")
        log("%d kirkegaarde i registret" % len(kgde))

    traef = []
    for n, k in enumerate(kgde, 1):
        kid = k["KIRKEGAARD_ID"]
        for aar in aargange:
            try:
                for a in afdoede_aar(kid, aar):
                    fdato = a.get("DATO_FODT", "")
                    if not kun_aar and fdato not in datoer:
                        continue
                    traef.append(a)
            except Exception as e:                        # noqa: BLE001
                log("  fejl paa %s (%s): %s" % (k.get("KIRKEGAARD_NAVN", ""), kid, e))
        if n % 100 == 0:
            log("... %d/%d kirkegaarde, %d traef" % (n, len(kgde), len(traef)))
        time.sleep(0.05)
    return traef


if __name__ == "__main__":
    rest = sys.argv[1:]
    kun_aar = "--aar" in rest
    if kun_aar:
        rest.remove("--aar")
    kgd_valgt = csvfil = None
    for flag in ("--kgd", "--csv"):
        if flag in rest:
            i = rest.index(flag)
            v = rest[i + 1] if i + 1 < len(rest) else None
            del rest[i:i + 2]
            if flag == "--kgd":
                kgd_valgt = v
            else:
                csvfil = v

    datoer = [d for d in rest if re.match(r"^\d{2}-\d{2}-\d{4}$", d)]
    if not datoer:
        print(__doc__)
        raise SystemExit(1)

    traef = fej(datoer, kun_aar, kgd_valgt)

    print()
    print("=" * 84)
    print("TRAEF: %d" % len(traef))
    print("=" * 84)
    for a in sorted(traef, key=lambda r: r.get("DATO_FODT", "")):
        navn = " ".join(x for x in (a.get("FORNAVNE", ""),
                                    a.get("AKT_EFTERNAVN", "")) if x)
        print("  %-40s f. %s  d. %s" % (navn[:40], a.get("DATO_FODT", ""),
                                        a.get("DATO_DOD", "")))
        print("        %s · gravsted %s" % (a.get("KIRKEGAARD_NAVN", ""),
                                            a.get("GRAVSTED_NR", "")))

    if csvfil:
        felter = ["DATO_FODT", "FORNAVNE", "AKT_EFTERNAVN", "DATO_DOD",
                  "KIRKEGAARD_NAVN", "GRAVSTED_NR", "AFDOED_ID"]
        with io.open(csvfil, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(felter)
            for a in traef:
                w.writerow([a.get(k, "") for k in felter])
        print("\ngemt %s" % csvfil)
