# -*- coding: utf-8 -*-
"""pdfside.py <pdf> <foerste> [sidste] — skriver en PDF's tekstlag ud side for side."""
import sys
from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
r = PdfReader(sys.argv[1])
a = int(sys.argv[2])
b = int(sys.argv[3]) if len(sys.argv) > 3 else a
for i in range(a, min(b, len(r.pages)) + 1):
    print("\n########## side %d ##########" % i)
    print(r.pages[i - 1].extract_text())
