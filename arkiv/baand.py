# -*- coding: utf-8 -*-
"""baand.py <grundtal> <opslag,...> <navn> <b1x0> <b1x1> <b2x0> <b2x1> <bredde>

Skaerer TO lodrette baand ud af hvert opslag (venstre og hoejre sides
navnekolonner) og stiller dem side om side. Saa kan et helt opslag laeses
i én visning uden at spilde plads paa de trykte overskrifter.
"""
import sys

from PIL import Image, ImageDraw
from hent import hent

sys.stdout.reconfigure(encoding="utf-8")


g = sys.argv[1]
opsl = [int(x) for x in sys.argv[2].split(",")]
navn = sys.argv[3]
a0, a1, b0, b1 = (float(x) for x in sys.argv[4:8])
bredde = int(sys.argv[8])

dele = []
for o in opsl:
    im = hent(int(g) + o)
    w, h = im.size
    for x0, x1 in ((a0, a1), (b0, b1)):
        c = im.crop((int(w * x0), int(h * 0.10), int(w * x1), h))
        ny = int(c.height * bredde / c.width)
        r = c.resize((bredde, ny), Image.LANCZOS)
        k = Image.new("RGB", (bredde, r.height + 26), "white")
        k.paste(r, (0, 26))
        ImageDraw.Draw(k).text((4, 7), "OPSL %d %s" % (o, "V" if x0 == a0 else "H"), fill="black")
        dele.append((o, k))

H = max(d.height for _, d in dele)
ud = Image.new("RGB", (bredde * len(dele), H), "white")
for i, (o, d) in enumerate(dele):
    ud.paste(d, (i * bredde, 0))
sti = navn if navn.endswith(".png") else navn + ".png"
ud.save(sti)
print("gemt:", sti, ud.size, "%d baand" % len(dele))
