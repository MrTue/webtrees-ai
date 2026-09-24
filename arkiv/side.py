# -*- coding: utf-8 -*-
"""side.py <pdf> <fra> <til> — udskriver hele tekstlaget for et sideinterval."""
import re
import sys

from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
r = PdfReader(sys.argv[1])
for i in range(int(sys.argv[2]), int(sys.argv[3]) + 1):
    t = r.pages[i - 1].extract_text() or ""
    t = re.sub(r"-\s*\n\s*", "", t)
    print("\n=============== SIDE %d ===============" % i)
    print(re.sub(r"\s+", " ", t))
