# -*- coding: utf-8 -*-
"""omkomne.py <navnestump> — henter alle 'De omkomne er:'-lister i
soeulykkestatistikkerne og viser dem, der rummer navnestumpen."""
import sys, os, re
from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.dirname(os.path.abspath(__file__))
stump = sys.argv[1]
aar = sys.argv[2:] or ["1939", "1940", "1941", "1942", "1943",
                       "1944", "1945", "1946", "1947", "1948"]
i_alt = traf = 0
for a in aar:
    sti = os.path.join(D, "soeulykke_%s.pdf" % a)
    if not os.path.exists(sti):
        continue
    r = PdfReader(sti)
    tekst = "\n".join((p.extract_text() or "") for p in r.pages)
    tekst = re.sub(r"-\s*\n\s*", "", tekst)          # ordelinger
    tekst = re.sub(r"\s+", " ", tekst)
    for m in re.finditer(r"(?:De omkomne er|Den omkomne er|Den forulykkede er)\s*:?(.{0,400}?)(?:Anm\.|\d{1,3}\.\s+(?:S/S|M/S|Ff\.|M/Gl|D/S))", tekst):
        i_alt += 1
        if re.search(stump, m.group(1), re.I):
            traf += 1
            print("%s: %s" % (a, m.group(1).strip()[:330]))
print("== %d navnelister gennemset, %d med %r" % (i_alt, traf, stump))
