# -*- coding: utf-8 -*-
"""gkasse.py <grundtal> <opslag,...> <navn> <x0> <x1> <y0> <y1> [bredde] [vandret]
Beskaerer samme rektangel ud af flere opslag og stabler dem (eller side om side)."""
import io
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageOps

# Uddata lander der, hvor SLAEGT_ARBEJDSMAPPE peger hen, ellers i den aktuelle
# arbejdsmappe.
import os
D = (os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or os.getcwd()

BASE = int(sys.argv[1])
NUMRE = [int(n) for n in sys.argv[2].split(",")]
TAG = sys.argv[3]
X0, X1, Y0, Y1 = (float(a) for a in sys.argv[4:8])
BREDDE = int(sys.argv[8]) if len(sys.argv) > 8 else 1600
VANDRET = "vandret" in sys.argv[9:]
# --kontrast straekker graatonerne; noedvendigt paa mikrofilm (FT1845, FT1850),
# hvor blaekket er graat og papiret graat. Klipper 2 % i hver ende.
KONTRAST = "--kontrast" in sys.argv[9:]

sys.stdout.reconfigure(encoding="utf-8")
dele = []
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
    ud = im.crop((int(w * X0), int(h * Y0), int(w * X1), int(h * Y1)))
    if KONTRAST:
        ud = ImageOps.autocontrast(ud.convert("L"), cutoff=2).convert("RGB")
    dele.append((n, ud))
    print("opslag %d: udsnit %dx%d" % (n, ud.width, ud.height))

if not dele:
    raise SystemExit("intet hentet")

if VANDRET:
    b = BREDDE // len(dele)
    sk = [(n, d.resize((b, int(d.height * b / d.width)), Image.LANCZOS))
          for n, d in dele]
    H = max(d.height for _, d in sk) + 28
    ark = Image.new("RGB", (BREDDE, H), "white")
    x = 0
    for n, d in sk:
        ark.paste(d, (x, 28))
        ImageDraw.Draw(ark).text((x + 6, 6), "opslag %d" % n, fill="black")
        x += b
else:
    sk = [(n, d.resize((BREDDE, int(d.height * BREDDE / d.width)), Image.LANCZOS))
          for n, d in dele]
    H = sum(d.height + 28 for _, d in sk)
    ark = Image.new("RGB", (BREDDE, H), "white")
    y = 0
    for n, d in sk:
        ImageDraw.Draw(ark).text((6, y + 6), "opslag %d" % n, fill="black")
        ark.paste(d, (0, y + 28))
        y += d.height + 28

sti = "%s\\%s.jpg" % (D, TAG)
ark.save(sti, quality=90)
print("gemt: %s  (%dx%d)" % (sti, ark.width, ark.height))
