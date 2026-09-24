# -*- coding: utf-8 -*-
"""pdfsoeg.py <pdf> <soegeord> [kontekst] — soeger i en PDF's tekstlag."""
import sys, re, os
from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
sti = sys.argv[1]
ord_ = sys.argv[2]
k = int(sys.argv[3]) if len(sys.argv) > 3 else 300

r = PdfReader(sti)
print("%s: %d sider" % (os.path.basename(sti), len(r.pages)))
traf = 0
for i, p in enumerate(r.pages, 1):
    t = p.extract_text() or ""
    t = re.sub(r"-\s*\n\s*", "", t)
    t = re.sub(r"\s+", " ", t)
    for m in re.finditer(ord_, t, re.I):
        traf += 1
        s = max(0, m.start() - k)
        print("--- s.%d: %s" % (i, t[s:m.end() + k]))
        if traf >= 25:
            print("(afbrudt ved 25 traef)")
            sys.exit()
print("== %d traef paa %r" % (traf, ord_))
