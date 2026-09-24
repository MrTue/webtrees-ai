# -*- coding: utf-8 -*-
"""fag2.py <n=v> [n=v ...] — Find a Grave med FRIE soegeparametre.

`findagrave.py` kan kun efternavn, fornavn og land. Denne tager alle sidens egne
parametre — og navnlig de FILTRE, der goer et fordansket navn soegbart:

    firstname lastname
    firstnamefilter / lastnamefilter =  exact | starts-with | contains | sounds-like
    birthyear birthyearfilter   deathyear deathyearfilter   (filter = aar +/- N)
    location  locationId  cemeteryName  memorialid  page

    python fag2.py lastname=eksemp lastnamefilter=contains
    python fag2.py firstname=Karen birthyear=1895 birthyearfilter=3
    python fag2.py lastname=Eksempelsen lastnamefilter=sounds-like

FAELDE: siden svarer 200 med en tom liste, naar der intet er — men den svarer
ogsaa 403/429, naar den er blevet hamret. Derfor skelner denne mellem
«INGEN TRAEF» og «AFVIST» og siger det ligeud.

BRUG DET TIL ENKELTOPSLAG. Find a Grave forbyder masse-skrabning i sine vilkaar: kald
scriptet for de faa personer, du faktisk leder efter, til personlig slaegtsforskning,
og hold pause mellem kaldene.
"""
import html
import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/120 Safari/537.36"),
      "Accept": "text/html,application/xhtml+xml",
      "Accept-Language": "da,en;q=0.8"}

par = dict(x.split("=", 1) for x in sys.argv[1:] if "=" in x)
if not par:
    print(__doc__)
    raise SystemExit(1)

u = "https://www.findagrave.com/memorial/search?" + urllib.parse.urlencode(par)
try:
    t = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                               timeout=90, context=CTX).read().decode("utf-8", "replace")
except urllib.error.HTTPError as e:
    print("AFVIST: HTTP %s — %s" % (e.code, u))
    print("Find a Grave spaerrer efter for mange kald. Vent og proev igen.")
    raise SystemExit(2)
except Exception as e:                                   # noqa: BLE001
    print("AFVIST: %s — %s" % (e, u))
    raise SystemExit(2)

print("hentet %d tegn — %s" % (len(t), u))

# Resultaterne ligger baade i en JSON-blok og i listen; proev JSON foerst.
m = re.search(r'"memorials"\s*:\s*(\[.*?\])\s*,\s*"', t, re.S)
if m:
    try:
        raekker = json.loads(m.group(1))
        print("ANTAL:", len(raekker))
        for x in raekker:
            print("  %-32s %-6s %-6s %s" % (
                (x.get("fullName") or "")[:32], x.get("birthYear") or "—",
                x.get("deathYear") or "—", (x.get("cemeteryName") or "")[:46]))
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception:                                    # noqa: BLE001
        pass

flad = re.sub(r"\s+", " ", html.unescape(
    re.sub(r"(?s)<script.*?</script>", " ", re.sub(r"<[^>]+>", " ", t))))
m = re.search(r"([\d,]+)\s+matching", flad)
antal = m.group(1) if m else None

ider = []
for m in re.finditer(r'href="/memorial/(\d+)/([a-z0-9\-]+)"', t):
    if m.group(1) not in [i for i, _ in ider]:
        ider.append((m.group(1), m.group(2)))

blok = re.findall(r'(?s)<div class="memorial-item.*?</div>\s*</div>', t)
if not blok:
    blok = re.findall(r'(?s)<a[^>]+href="/memorial/\d+[^"]*"[^>]*>(.{0,700}?)</a>', t)
vist = 0
for b in blok[:40]:
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", b))).strip()
    if txt and not txt.lower().startswith(("log", "sign", "add", "search", "famous")):
        vist += 1
        print("  " + txt[:170])

if ider:
    print("--- MINDESMAERKE-ID (til fagmem.py) ---")
    for i, n in ider[:20]:
        print("  %s/%s" % (i, n))

if vist:
    print("ANTAL:", antal or vist)
elif antal and antal not in ("0", "0,0"):
    print("ANTAL: %s — men ingen raekker kunne laeses ud af siden" % antal)
else:
    print("INGEN TRAEF.")
