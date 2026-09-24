# -*- coding: utf-8 -*-
"""medietjek.py -- efterproever, at hvert medieobjekts `1 FILE` peger paa en fil, der findes.

`linktjek.py` foelger `@X###@`-henvisningerne, og `markutjek.py` tager `[[X###]]`. INGEN AF
DEM AABNER EN FIL. Et medieobjekt med en sti, der ikke findes, viser et brudt billede i
webtrees, og det ser man ikke, foer man kigger paa netop den post.

    python arkiv\\medietjek.py

Kraever facit.json (koer `facit.py` foerst) og at mediemappen er monteret over SMB.

FAELDE, SOM KOSTEDE TID: mediemappens rod er en UNC-sti. Skriver man den som en Python
raw-string med fire baglaens skraastreger -- r"\\\\\\\\NAS\\..." -- bliver det FIRE
tegn, og hver enkelt fil meldes manglende. Brug fremad-skraastreger: "//NAS/...".
Python og Windows tager begge imod dem, og der er intet at taelle galt.
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROD = os.environ.get("WEBTREES_MEDIA", "//NAS/docker/webtrees/data/media")


def facitsti():
    for sti in (os.path.join((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH", "")), "facit.json"),
                "facit.json",
                os.path.join(os.path.dirname(__file__), "facit.json")):
        if sti and os.path.exists(sti):
            return sti
    sys.exit("facit.json blev ikke fundet. Koer facit.py foerst.")


def main():
    sti = facitsti()
    d = json.load(io.open(sti, encoding="utf-8"))
    print("poster i traeet: %d   (%s)" % (len(d), sti))
    if not os.path.isdir(ROD):
        sys.exit("mediemappen svarer ikke: %s -- er SMB-drevet monteret?" % ROD)

    pat = re.compile(r"1 FILE (.+)")
    n = 0
    mangler = []
    for x, p in sorted(d.items()):
        if p.get("slags") != "MEDIE":
            continue
        for fakta in p.get("fakta", []):
            m = pat.match(fakta.get("tekst", "").split("\n")[0])
            if not m:
                continue
            rel = m.group(1).strip()
            n += 1
            if not os.path.exists(ROD + "/" + rel.replace("\\", "/")):
                mangler.append((x, rel))

    print("medieobjekter med filsti: %d" % n)
    if not mangler:
        print("\n0 filer, der ikke findes")
        return 0
    print("\nFILER, DER IKKE FINDES:")
    for x, rel in mangler:
        print("   %-8s -> %s" % (x, rel))
    return 1


if __name__ == "__main__":
    sys.exit(main())
