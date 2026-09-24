# -*- coding: utf-8 -*-
"""Beskærer en enkelt indførsel ud af en AO-skanning og forstørrer den."""
import tempfile
import os
import sys, io, urllib.request
from PIL import Image

D = ((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())

img_id, tag = sys.argv[1], sys.argv[2]
x0, x1, y0, y1 = (float(v) for v in sys.argv[3:7])
scale = float(sys.argv[7]) if len(sys.argv) > 7 else 2.6

data = urllib.request.urlopen("https://api.rigsarkivet.dk/ao/v1/images/%s" % img_id, timeout=30).read()
im = Image.open(io.BytesIO(data)).convert("RGB")
w, h = im.size
c = im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
p = D + "\\" + tag + ".png"
c.save(p)
print("gemt:", p, c.size, "(original %dx%d)" % (w, h))
