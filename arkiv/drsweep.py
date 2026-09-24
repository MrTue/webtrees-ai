# -*- coding: utf-8 -*-
"""drsweep.py — alle i traeet uden doedsdato gennem dodsregister.dk.

Soeger paa EFTERNAVN + foedselsaar +/- 1 og melder kun de raekker, hvor
FOEDSELSDATOEN er praecis den samme som traeets. Registret forkorter fornavne
(«AND», «KAR M»), saa fornavnet duer ikke som noegle — datoen goer.
"""
import tempfile
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
PY = sys.executable
DR = str(Path(__file__).resolve().parent / "dr.py")
ROSTER = Path(((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())) / "roster.txt"

MDR = {"JAN": "jan", "FEB": "feb", "MAR": "mar", "APR": "apr", "MAY": "maj",
       "JUN": "jun", "JUL": "jul", "AUG": "aug", "SEP": "sep", "OCT": "okt",
       "NOV": "nov", "DEC": "dec"}


def dansk(gedcom):
    """'11 FEB 1887' -> '11. feb 1887' som registret skriver den."""
    m = re.match(r"^(\d{1,2}) ([A-Z]{3}) (\d{4})$", gedcom.strip())
    if not m:
        return None
    return "%d. %s %s" % (int(m.group(1)), MDR[m.group(2)], m.group(3))


for linje in ROSTER.read_text(encoding="utf-8").splitlines():
    d = linje.split("|")
    if len(d) < 7:
        continue
    x, navn, f, dd, steder, occu, priv = d[:7]
    if priv == "JA" or dd.strip():
        continue                                             # har allerede en doedsdato
    dato = dansk(f)
    if not dato:
        continue
    aar = int(f[-4:])
    if aar > 1950:
        continue                                             # nulevende slaegt
    efter = navn.split()[-1]
    try:
        t = subprocess.run([PY, DR, "--efter", efter,
                            "--fra", str(aar - 1), "--til", str(aar + 1)],
                           capture_output=True, timeout=600
                           ).stdout.decode("utf-8", "replace")
    except Exception as e:                                   # noqa: BLE001
        print("%-6s %-30s FEJL %s" % (x, navn[:30], e), flush=True)
        continue
    traf = [l.strip() for l in t.splitlines() if dato in l]
    if traf:
        print("\n>>> %-6s %-32s f. %s" % (x, navn[:32], dato), flush=True)
        for l in traf:
            print("      " + re.sub(r"\s+", " ", l)[:220], flush=True)
    else:
        print("    %-6s %-32s f. %-14s intet" % (x, navn[:32], dato), flush=True)
