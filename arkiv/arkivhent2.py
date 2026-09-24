# -*- coding: utf-8 -*-
"""arkivhent2.py <arkiv.dk-id> <filnavn> — henter selve billedfilen fra en post.

arkiv.dk leverer billederne fra et mediedomaene; URL'en staar i sidens HTML som
et <img>- eller og:image-felt. Filerne er ofte AVIF og konverteres her til JPEG,
som webtrees kan vise.
"""
from pathlib import Path
import re
import ssl
import sys
import urllib.request
from io import BytesIO

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://arkiv.dk/"}
B = str(Path(__file__).resolve().parent.parent / "billeder")

vis_id, navn = sys.argv[1], sys.argv[2]
t = urllib.request.urlopen(urllib.request.Request(
    "https://arkiv.dk/vis/" + vis_id, headers=UA),
    timeout=90, context=CTX).read().decode("utf-8", "replace")

kandidater = []
# Billedet indlaeses af JavaScript, men adressen staar i og:image-metatagget —
# og den har INGEN filendelse: .../filer/visning/<guid>
for m in re.finditer(r'property="og:image"[^>]*content="([^"]+)"', t, re.I):
    kandidater.append(m.group(1))
for m in re.finditer(r'content="([^"]+)"[^>]*property="og:image"', t, re.I):
    kandidater.append(m.group(1))
for m in re.finditer(r'"(https?://arkibasapi[^"]+)"', t, re.I):
    kandidater.append(m.group(1))
for m in re.finditer(r'(?:content|src|href|data-src)="(https?://[^"]+?\.(?:jpe?g|png|avif|webp)[^"]*)"', t, re.I):
    kandidater.append(m.group(1))

kandidater = list(dict.fromkeys(kandidater))
print("kandidat-URL'er:")
for k in kandidater[:12]:
    print("   " + k)

if not kandidater:
    raise SystemExit("ingen billed-URL fundet")

for k in kandidater:
    if "logo" in k.lower() or "icon" in k.lower():
        continue
    try:
        raa = urllib.request.urlopen(urllib.request.Request(k, headers=UA),
                                     timeout=120, context=CTX).read()
    except Exception as e:                                   # noqa: BLE001
        print("   kunne ikke hente %s: %s" % (k[:70], e))
        continue
    if len(raa) < 8000:
        continue
    try:
        from PIL import Image
        im = Image.open(BytesIO(raa)).convert("RGB")
    except Exception as e:                                   # noqa: BLE001
        print("   kunne ikke aabne %s: %s" % (k[:70], e))
        continue
    sti = B + "\\" + navn
    im.save(sti, quality=90)
    print("GEMT %s  (%dx%d, %d bytes kilde)" % (sti, im.width, im.height, len(raa)))
    print("KILDE-URL " + k)
    break
