# -*- coding: utf-8 -*-
"""bandsweep.py — hele slaegten gennem fangeprotokollerne paa banditter.dk.

Soeger paa EFTERNAVN + et vindue om foedselsaaret, og viser kun de raekker, hvor
fornavnet ogsaa ligner. Uden aarsvinduet drukner Nielsen og Jensen.
"""
import tempfile
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
PY = sys.executable
BAND = str(Path(__file__).resolve().parent / "banditter.py")
ROSTER = Path(((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())) / "roster.txt"

AAR = re.compile(r"(1[6-9]\d\d)")


def koer(*arg):
    r = subprocess.run([PY, BAND] + list(arg), capture_output=True, timeout=600)
    return r.stdout.decode("utf-8", "replace")


for linje in ROSTER.read_text(encoding="utf-8").splitlines():
    d = linje.split("|")
    if len(d) < 7:
        continue
    x, navn, f, dd, steder, occu, priv = d[:7]
    if priv == "JA":
        continue
    dele = navn.split()
    if len(dele) < 2:
        continue
    efter = dele[-1]
    fornavn = dele[0]
    m = AAR.search(f)
    arg = ["--efternavn=%s" % efter]
    if m:
        aar = int(m.group(1))
        arg.append("--faar=%d-%d" % (aar - 3, aar + 3))
    elif AAR.search(dd):
        aar = int(AAR.search(dd).group(1))
        arg.append("--faar=%d-%d" % (aar - 90, aar - 15))
    else:
        continue                                             # uden aar er det stoej
    try:
        t = koer(*arg)
    except Exception as e:                                   # noqa: BLE001
        print("%-6s %-32s FEJL %s" % (x, navn[:32], e), flush=True)
        continue
    n = re.search(r"(\d+) raekker", t)
    antal = int(n.group(1)) if n else 0
    if not antal:
        continue
    traf = fornavn.lower() in t.lower()
    print("%-6s %-32s %-14s %3d rækker %s" % (
        x, navn[:32], " ".join(arg[1:]), antal,
        "<<< FORNAVNET GÅR IGEN" if traf else ""), flush=True)
    if traf:
        for l in t.splitlines():
            if fornavn.lower() in l.lower():
                print("        " + l.strip()[:300], flush=True)
