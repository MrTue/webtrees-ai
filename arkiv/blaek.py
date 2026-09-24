# -*- coding: utf-8 -*-
"""blaek.py <grundtal> <fra> <til> [x0 x1 y0 y1]
Maaler blaekmaengden i et udsnit af hvert opslag. Bruges til at finde de sider
i et bind, der faktisk er beskrevet — fx navnesiderne i en 1855-folketaelling,
hvor hvert skema fylder fire opslag og fasen forskyder sig undervejs.

Navnesider ligger typisk paa 0,04-0,11; blanke sider og trykte hoveder paa
0,005-0,03.
"""
import sys, os
import numpy as np
from PIL import ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hent import hent                                          # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
g, fra, til = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
x0, x1, y0, y1 = ([float(v) for v in sys.argv[4:8]] if len(sys.argv) > 7
                  else [0.10, 0.36, 0.28, 0.90])

for n in range(fra, til + 1):
    try:
        im = hent(g + n).convert("L")
    except Exception as e:                                     # noqa: BLE001
        print("%3d  FEJL %s" % (n, e))
        continue
    w, h = im.size
    a = np.asarray(ImageOps.autocontrast(
        im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))))
    v = float((a < 110).mean())
    print("%3d  %.4f  %s" % (n, v, "#" * int(v * 400)))
