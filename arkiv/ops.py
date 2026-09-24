# -*- coding: utf-8 -*-
"""ops.py <billedid> <navn> [x0 x1 y0 y1] [maxbredde] — henter et AO-opslag og beskaerer."""
import tempfile
import os
import io
import sys
import urllib.request

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
UD = ((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())

bid = int(sys.argv[1])
navn = sys.argv[2]
x0, x1, y0, y1 = (float(sys.argv[3]), float(sys.argv[4]),
                  float(sys.argv[5]), float(sys.argv[6])) if len(sys.argv) > 6 else (0, 1, 0, 1)
maks = int(sys.argv[7]) if len(sys.argv) > 7 else 1700

for i in range(5):
    try:
        req = urllib.request.Request(
            "https://api.rigsarkivet.dk/ao/v1/images/%d" % bid,
            headers={"User-Agent": "slaegtsforskning/1.0"})
        im = Image.open(io.BytesIO(
            urllib.request.urlopen(req, timeout=180).read())).convert("RGB")
        break
    except Exception as e:                                   # noqa: BLE001
        sidste = e
else:
    raise SystemExit("kunne ikke hente %d" % bid)

b, h = im.size
ud = im.crop((int(b * x0), int(h * y0), int(b * x1), int(h * y1)))
if ud.size[0] > maks:
    ud = ud.resize((maks, int(ud.size[1] * maks / ud.size[0])))
sti = UD + "\\" + navn + ".jpg"
ud.save(sti, quality=90)
print("%dx%d -> %s (%dx%d)" % (b, h, sti, ud.size[0], ud.size[1]))
