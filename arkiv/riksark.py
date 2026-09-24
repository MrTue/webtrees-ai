# -*- coding: utf-8 -*-
"""riksark.py -- hent scannede svenske kirkebøger fra Riksarkivet.

    python arkiv\\riksark.py manifest C0012345
    python arkiv\\riksark.py hent C0012345 12                 # ét opslag i fuld bredde
    python arkiv\\riksark.py hent C0012345 12 2500            # ét opslag, 2500 px bredt
    python arkiv\\riksark.py gitter C0012345 8-19 0.0 0.5 0.0 1.0 1100
      # venstre halvdel af opslag 8-19 lagt side om side i ét kontaktark

**Riksarkivets scanninger er frit tilgængelige**, men billedserveren
`lbiiif.riksarkivet.se` forventer samme `Referer: https://sok.riksarkivet.se/` som
Riksarkivets egen billedviser sender; uden den svarer den 403. Scriptet sender derfor
den header. Samme opbygning som Wads Sedler.

Billed-id'et står øverst til højre på bindets omslagsside i billedviseren og i titlen:
fx `SE/XXA/12345/B/1` med **C0012345**, og opslagene er `C0012345_00001`, `_00002`, …
Opslag 1 er altid Riksarkivets eget omslagsblad, så **bogens side 1 er opslag 2**.

IIIF-størrelser: `full/max/0/default.jpg` er fuld opløsning (ofte 5-6000 px bredt og
tungt), `full/2000,/0/default.jpg` skalerer til 2000 px bredde. Udsnit tages som
`<x>,<y>,<b>,<h>/<bredde>,/0/default.jpg` i billedets egne pixels.
"""
import io
import json
import os
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

IIIF = "https://lbiiif.riksarkivet.se/arkis!%s"
REFERER = "https://sok.riksarkivet.se/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
UD = (os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or os.path.join(os.environ.get("TEMP", "."), "riksark")


def _hent(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": REFERER})
    return urllib.request.urlopen(req, timeout=timeout).read()


def opslag_id(vol, nr):
    return "%s_%05d" % (vol, nr)


def info(vol, nr):
    """Billedets egne mål -- (bredde, højde). Rejser HTTPError, hvis opslaget ikke findes."""
    d = json.loads(_hent((IIIF % opslag_id(vol, nr)) + "/info.json").decode("utf-8"))
    return d["width"], d["height"]


def antal(vol, loft=800):
    """Antal opslag i bindet, fundet ved halvering. Koster ca. ti forespørgsler."""
    lav, hoej = 1, loft
    try:
        info(vol, 1)
    except urllib.error.HTTPError:
        return 0
    while lav < hoej:
        m = (lav + hoej + 1) // 2
        try:
            info(vol, m)
            lav = m
        except urllib.error.HTTPError:
            hoej = m - 1
    return lav


def billede(vol, nr, bredde=None, udsnit=None):
    """Rå JPEG. `udsnit` er (x0, y0, x1, y1) som brøkdele af billedet."""
    omr = "full"
    if udsnit:
        b, h = info(vol, nr)
        x0, y0, x1, y1 = udsnit
        omr = "%d,%d,%d,%d" % (int(x0 * b), int(y0 * h), int((x1 - x0) * b), int((y1 - y0) * h))
    st = ("%d," % bredde) if bredde else "max"
    return _hent("%s/%s/%s/0/default.jpg" % (IIIF % opslag_id(vol, nr), omr, st))


def gem(vol, nr, bredde=None, udsnit=None, sti=None):
    data = billede(vol, nr, bredde, udsnit)
    sti = sti or os.path.join(UD, opslag_id(vol, nr) + ".jpg")
    os.makedirs(os.path.dirname(sti), exist_ok=True)
    with open(sti, "wb") as f:
        f.write(data)
    return sti


def gitter(vol, fra, til, udsnit, bredde=1100, kol=None, sti=None):
    """Læg samme udsnit af flere opslag side om side i ét billede."""
    from PIL import Image
    bil = []
    for nr in range(fra, til + 1):
        try:
            bil.append((nr, Image.open(io.BytesIO(billede(vol, nr, bredde, udsnit)))))
        except urllib.error.HTTPError:
            break
    if not bil:
        raise SystemExit("ingen opslag hentet")
    kol = kol or min(len(bil), 4)
    raekker = (len(bil) + kol - 1) // kol
    b = max(i.width for _, i in bil)
    h = max(i.height for _, i in bil)
    ark = Image.new("RGB", (b * kol, h * raekker), "white")
    for i, (_, im) in enumerate(bil):
        ark.paste(im, ((i % kol) * b, (i // kol) * h))
    sti = sti or os.path.join(UD, "%s_%d-%d_gitter.jpg" % (vol, fra, bil[-1][0]))
    os.makedirs(os.path.dirname(sti), exist_ok=True)
    ark.save(sti, quality=88)
    return sti, [nr for nr, _ in bil]


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "manifest":
        vol = a[1]
        n = antal(vol)
        b, h = info(vol, 1)
        print("%s: %d opslag, opslag 1 er %d x %d px" % (vol, n, b, h))
    elif a[0] == "hent":
        vol, nr = a[1], int(a[2])
        bredde = int(a[3]) if len(a) > 3 else None
        print(gem(vol, nr, bredde))
    elif a[0] == "gitter":
        vol = a[1]
        fra, til = (int(x) for x in a[2].split("-"))
        x0, x1, y0, y1 = (float(x) for x in a[3:7])
        bredde = int(a[7]) if len(a) > 7 else 1100
        sti, nrs = gitter(vol, fra, til, (x0, y0, x1, y1), bredde)
        print(sti, "opslag", nrs[0], "-", nrs[-1])
    else:
        sys.exit(__doc__)
