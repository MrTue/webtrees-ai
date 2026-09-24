# -*- coding: utf-8 -*-
"""findagrave.py --efter <efternavn> [--for <fornavn>] [--land <landekode>]

Find a Grave har en almindelig HTML-soegeside, som kan hentes uden konto:

    https://www.findagrave.com/memorial/search?lastname=X&firstname=Y

Bruges naar sporet gaar til udlandet — fx udvandrere til USA, som ikke staar i
danske doedsregistre.

BRUG DET TIL ENKELTOPSLAG. Find a Grave forbyder masse-skrabning i sine vilkaar: kald
scriptet for de faa personer, du faktisk leder efter, til personlig slaegtsforskning,
og hold pause mellem kaldene."""
import urllib.request, urllib.parse, ssl, sys, re, html, json

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/120 Safari/537.36"),
      "Accept": "text/html,application/xhtml+xml", "Accept-Language": "da,en;q=0.8"}

a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
par = {"lastname": a.get("--efter", "")}
if "--for" in a:
    par["firstname"] = a["--for"]
if "--land" in a:
    par["location"] = a["--land"]
u = "https://www.findagrave.com/memorial/search?" + urllib.parse.urlencode(par)
t = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                           timeout=90, context=CTX).read().decode("utf-8", "replace")
print("hentet %d tegn — %s" % (len(t), u))

# siden lægger resultaterne i et JSON-objekt
m = re.search(r'"memorials"\s*:\s*(\[.*?\])\s*,\s*"', t, re.S)
if m:
    try:
        for x in json.loads(m.group(1)):
            print("  %-30s %-12s %-12s %s" % (
                (x.get("fullName") or "")[:30], x.get("birthYear") or "—",
                x.get("deathYear") or "—", (x.get("cemeteryName") or "")[:50]))
        sys.exit()
    except Exception:
        pass

# ellers: træk navn, datoer og kirkegård ud af listen
blok = re.findall(r'(?s)<div class="memorial-item.*?</div>\s*</div>', t)
if not blok:
    blok = re.findall(r'(?s)<a[^>]+href="/memorial/\d+[^"]*"[^>]*>(.{0,700}?)</a>', t)
n = 0
for b in blok[:40]:
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", b))).strip()
    if txt:
        n += 1
        print("  " + txt[:180])
if not n:
    flad = re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<script.*?</script>", " ",
                                                    re.sub(r"<[^>]+>", " ", t))))
    i = flad.lower().find("matching")
    print("--- ingen poster fundet; udsnit ---")
    print(flad[max(0, i - 200):i + 700] if i > 0 else flad[:700])
