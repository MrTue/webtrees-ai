# -*- coding: utf-8 -*-
"""sospg.py <soegeord> [aar ...] — soeger i de hentede soeulykke-PDF'er."""
import sys, os, re
from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.dirname(os.path.abspath(__file__))
ord_ = sys.argv[1]
aar = sys.argv[2:] or ["1940", "1941", "1942", "1943", "1944", "1945"]

for a in aar:
    sti = os.path.join(D, "soeulykke_%s.pdf" % a)
    if not os.path.exists(sti):
        print(a, "mangler"); continue
    try:
        r = PdfReader(sti)
    except Exception as e:                                    # noqa: BLE001
        print(a, "kan ikke laeses:", e); continue
    fundet = 0
    for i, p in enumerate(r.pages, 1):
        t = p.extract_text() or ""
        for m in re.finditer(ord_, t, re.I):
            fundet += 1
            s = max(0, m.start() - 260)
            uddrag = re.sub(r"\s+", " ", t[s:m.end() + 320])
            print("--- %s s.%d: %s" % (a, i, uddrag))
            if fundet > 12:
                break
        if fundet > 12:
            break
    print("== %s: %d sider, %d traef paa %r" % (a, len(r.pages), fundet, ord_))
