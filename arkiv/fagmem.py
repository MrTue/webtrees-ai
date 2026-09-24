# -*- coding: utf-8 -*-
"""fagmem.py <id>/<slug> — henter EN Find a Grave-mindeside og viser dens tekst.

Soegesiden giver kun navn, aarstal og kirkegaard. Selve mindesiden har
foedested, doedssted, gravplads, biografi og — vigtigst — FAMILIELINKS til
foraeldre, aegtefaelle, boern og soeskende. Det er dér, en amerikansk gren
haenger sammen.

    python fagmem.py 123456789/anders-eksempelsen      # <id>/<slug> fra fag2.py

Scriptet sender en almindelig browser-User-Agent; uden den svarer siden 403. Hold
tempoet lavt: siden begraenser antallet af kald, saa vent mellem kaldene og hent kun
de mindesider, der faktisk skal bruges. Find a Grave forbyder masse-skrabning i sine
vilkaar — brug scriptet til enkeltopslag i personlig slaegtsforskning.
"""
import html
import re
import ssl
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/120 Safari/537.36"),
      "Accept": "text/html,application/xhtml+xml",
      "Accept-Language": "da,en;q=0.8"}

if len(sys.argv) < 2:
    print(__doc__)
    raise SystemExit(1)

u = "https://www.findagrave.com/memorial/" + sys.argv[1]
try:
    t = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                               timeout=90, context=CTX).read().decode("utf-8", "replace")
except urllib.error.HTTPError as e:
    print("AFVIST: HTTP %s — %s" % (e.code, u))
    raise SystemExit(2)

flad = re.sub(r"\s+", " ", html.unescape(
    re.sub(r"(?s)<script.*?</script>", " ", re.sub(r"<[^>]+>", " ", t))))

# familielinks staar som <a href="/memorial/ID/navn"> i afsnittet "Familiemedlemmer"
fam = []
for m in re.finditer(r'href="/memorial/(\d+)/([a-z0-9\-]+)"[^>]*>(?:<[^>]*>)*([^<]{2,60})', t):
    navn = m.group(3).strip()
    if navn and (m.group(1), navn) not in fam:
        fam.append((m.group(1), navn))

i = flad.find("Fødsel")
if i < 0:
    i = flad.find("Birth")
print(flad[max(0, i - 300):i + 2200])
print("\n--- LINKEDE MINDESIDER ---")
for mid, navn in fam[:25]:
    print("  %-12s %s" % (mid, navn))
