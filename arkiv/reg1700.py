# -*- coding: utf-8 -*-
"""reg1700.py <pdf> [fra] [til] -- traekker registerlinjer med aarstal foer 1700 ud."""
import re
import sys

from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
r = PdfReader(sys.argv[1])
a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
b = int(sys.argv[3]) if len(sys.argv) > 3 else len(r.pages)

pat = re.compile(r"\b1[0-6]\d\d\b")
n = 0
for i in range(a, min(b, len(r.pages)) + 1):
    t = r.pages[i - 1].extract_text() or ""
    for linje in t.split("\n"):
        if pat.search(linje):
            ren = re.sub(r"\.{3,}", " ... ", linje)
            ren = re.sub(r"\s+", " ", ren).strip()
            if len(ren) > 8:
                print("s.%-4d %s" % (i, ren[:190]))
                n += 1
print("\n%d linjer med aarstal foer 1700" % n)
