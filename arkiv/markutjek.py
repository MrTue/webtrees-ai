# -*- coding: utf-8 -*-
"""markutjek.py [--job [moenster]] -- efterproever [[X###]]-markeringerne.

`linktjek.py` efterproever `@X###@` -- de rigtige GEDCOM-pegepinde, som webtrees selv
foelger. Men `[[X###]]` er ren VISNINGSMARKERING og bliver ikke kontrolleret nogen steder,
selv om den bruges i hver anden note i traeet. En tastefejl i den giver en henvisning,
ingen ser er doed.

    python arkiv\\markutjek.py                 # skanner TRAEETS EGNE NOTER (facit.json)
    python arkiv\\markutjek.py --job           # skanner jobfilerne i poster/
    python arkiv\\markutjek.py --job "…\\job-*.json"

Koer den efter et job, der FORUDSIGER xref-numre. Husk da, at en `add-parent` laegger
beslag paa TO numre -- personen og den nye familie -- mens `add-spouse-to-family` kun tager
eet, og at `create-source` og `create-media` taeller med paa lige fod med et menneske.

Kraever SLAEGT_ARBEJDSMAPPE eller at facit.json ligger i arbejdsmappen; koer `facit.py` foerst.
"""
from pathlib import Path
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

PAT = re.compile(r"\[\[(X\d+)\]\]")


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
    findes = set(d.keys())
    print("poster i traeet: %d   (%s)" % (len(findes), sti))

    doede = {}
    n = 0

    if "--job" in sys.argv:
        i = sys.argv.index("--job")
        moenster = (sys.argv[i + 1] if len(sys.argv) > i + 1
                    else str(Path(__file__).resolve().parent.parent / "poster" / "*.json"))
        hvad = "jobfiler: %s" % moenster
        for f in sorted(glob.glob(moenster)):
            t = io.open(f, encoding="utf-8").read()
            for m in set(PAT.findall(t)):
                n += 1
                if m not in findes:
                    doede.setdefault(os.path.basename(f), set()).add(m)
    else:
        hvad = "traeets egne noter"
        for x, p in d.items():
            for fakta in p.get("fakta", []):
                for m in set(PAT.findall(fakta.get("tekst", ""))):
                    n += 1
                    if m not in findes:
                        doede.setdefault(x, set()).add(m)

    print("markeringer efterproevet i %s: %d" % (hvad, n))
    if not doede:
        print("\n0 doede markeringer")
        return 0
    print("\nDOEDE MARKERINGER:")
    for k, s in sorted(doede.items()):
        print("   %-26s -> %s" % (k, ", ".join(sorted(s))))
    return 1


if __name__ == "__main__":
    sys.exit(main())
