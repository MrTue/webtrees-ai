# -*- coding: utf-8 -*-
"""arkivdk.py <soegeord> [antal] — soeger paa arkiv.dk.

Soegefeltet hedder `searchstring`, og resultaterne kommer som almindelig HTML.
Hver post har et /vis/<id>-link. Selve billedbeskrivelsen ligger i en
efterfoelgende JavaScript-indlaesning og skal hentes med WebFetch."""
import urllib.request, urllib.parse, ssl, sys, re, html

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/xhtml+xml"}

q = urllib.parse.quote(sys.argv[1])
maks = int(sys.argv[2]) if len(sys.argv) > 2 else 12
u = "https://arkiv.dk/soeg?searchstring=" + q
t = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                           timeout=60, context=CTX).read().decode("utf-8", "replace")

flad = re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<script.*?</script>", " ", t)))
m = re.search(r"([\d.]+)\s*resultater", flad, re.I)
print("ANTAL:", m.group(1) if m else "?", "|", sys.argv[1])

# hver post er et /vis/-link; teksten indtil naeste /vis/-link hoerer til den
dele = re.split(r'href="(/vis/\d+)"', t)
vist = 0
for i in range(1, len(dele) - 1, 2):
    sti = dele[i]
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", dele[i + 1]))).strip()
    if not txt:
        continue
    vist += 1
    print("  arkiv.dk%-12s %s" % (sti, txt[:150]))
    if vist >= maks:
        break
