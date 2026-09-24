# -*- coding: utf-8 -*-
"""gbaand.py <grundtal> <opslag,opslag,...> <navn> [y0] [y1] [bredde]
Stabler et vandret baand fra flere opslag, saa aarstallene kan findes i eet billede."""
import io
import sys
import urllib.request

from PIL import Image, ImageDraw

# Uddata lander der, hvor SLAEGT_ARBEJDSMAPPE peger hen, ellers i den aktuelle
# arbejdsmappe.
import os
D = (os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or os.getcwd()

BASE = int(sys.argv[1])
NUMRE = [int(n) for n in sys.argv[2].split(",")]
TAG = sys.argv[3]
Y0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.00
Y1 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.12
BREDDE = int(sys.argv[6]) if len(sys.argv) > 6 else 1600

sys.stdout.reconfigure(encoding="utf-8")
baand = []
for n in NUMRE:
    try:
        data = urllib.request.urlopen(
            "https://api.rigsarkivet.dk/ao/v1/images/%d" % (BASE + n),
            timeout=60).read()
        im = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:                                   # noqa: BLE001
        print("opslag %d: FEJL %s" % (n, e))
        continue
    if im.size == (1920, 1080):
        print("opslag %d: SPLASH-billede, forkert id" % n)
        continue
    w, h = im.size
    ud = im.crop((0, int(h * Y0), w, int(h * Y1)))
    ny = int(ud.height * BREDDE / ud.width)
    ud = ud.resize((BREDDE, ny), Image.LANCZOS)
    m = Image.new("RGB", (BREDDE, ny + 28), "white")
    m.paste(ud, (0, 28))
    ImageDraw.Draw(m).text((8, 6), "opslag %d  (%dx%d)" % (n, w, h), fill="black")
    baand.append(m)
    print("opslag %d: %dx%d" % (n, w, h))

if not baand:
    raise SystemExit("intet hentet")
H = sum(b.height for b in baand)
ark = Image.new("RGB", (BREDDE, H), "white")
y = 0
for b in baand:
    ark.paste(b, (0, y))
    y += b.height
sti = "%s\\%s.jpg" % (D, TAG)
ark.save(sti, quality=88)
print("gemt: %s  (%dx%d)" % (sti, ark.width, ark.height))
