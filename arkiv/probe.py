# -*- coding: utf-8 -*-
"""probe.py <grundtal> <opslag,...> <navn> [maxbredde] [x0 x1 y0 y1]
Henter opslag og gemmer dem som JPEG, evt. beskaaret til et udsnit (0-1)."""
import sys, os
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hent import hent

sys.stdout.reconfigure(encoding="utf-8")
MAPPE = os.path.dirname(os.path.abspath(__file__))

grundtal = int(sys.argv[1])
opslag = [int(x) for x in sys.argv[2].split(",")]
navn = sys.argv[3]
maxb = int(sys.argv[4]) if len(sys.argv) > 4 else 1600
box = [float(x) for x in sys.argv[5:9]] if len(sys.argv) > 8 else None

for o in opslag:
    im = hent(grundtal + o)
    w, h = im.size
    if box:
        im = im.crop((int(box[0] * w), int(box[2] * h), int(box[1] * w), int(box[3] * h)))
    if im.width > maxb:
        im = im.resize((maxb, int(im.height * maxb / im.width)), Image.LANCZOS)
    sti = os.path.join(MAPPE, "%s_%d.jpg" % (navn, o))
    im.save(sti, "JPEG", quality=88)
    print("%s  opslag %-4d org %dx%d -> %dx%d" % (sti, o, w, h, im.width, im.height))
