# -*- coding: utf-8 -*-
"""arkivsweep.py [maks-xref] — soeger hver person i traeet paa arkiv.dk.

Skriver en rapport til arbejdsmappen (SLAEGT_ARBEJDSMAPPE), arkivsweep.md, med de traef, der er vaerd at se
paa. Filtrene er det vigtigste ved scriptet: uden dem drukner alt i de almindelige -sen-navne.

  * Nulevende (RESN privacy) springes over — de skal ikke soeges op.
  * Navne paa faerre end tre ord springes over. Et fornavn plus et -sen-navn giver
    tusinder; «Anne Kirstine Eksempelsen» giver en haandfuld.
  * Traef over GRAENSE regnes for stoej og rapporteres kun som et tal.
  * Personens egne stednavne bruges som fingerpeg: et traef, der naevner et af
    dem, markeres med >>> og staar oeverst.
"""
import tempfile
import os
import html
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from webtrees_klient import WebtreesClient, load_creds  # noqa: E402

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/xhtml+xml"}
GRAENSE = 60          # flere traef end dette = for almindeligt navn
PAUSE = 1.2           # hoeflighed over for arkiv.dk
UD = Path(((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())) / "arkivsweep.md"

creds = load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
c = WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])


def facts(x):
    st, hd, tx = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, x))
    if st != 200:
        return None
    return [html.unescape(t).strip() for t in re.findall(
        r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', tx)]


def soeg(navn):
    u = "https://arkiv.dk/soeg?searchstring=" + urllib.parse.quote(navn)
    t = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                               timeout=60, context=CTX).read().decode("utf-8", "replace")
    flad = re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<script.*?</script>", " ", t)))
    m = re.search(r"([\d.]+)\s*resultater", flad, re.I)
    antal = int(m.group(1).replace(".", "")) if m else -1
    poster, dele = [], re.split(r'href="(/vis/\d+)"', t)
    for i in range(1, len(dele) - 1, 2):
        txt = re.sub(r"\s+", " ", html.unescape(
            re.sub(r"<[^>]+>", " ", dele[i + 1]))).strip()
        if txt:
            poster.append((dele[i], txt[:200]))
    return antal, poster


maks = int(sys.argv[1]) if len(sys.argv) > 1 else 340
linjer = ["# arkiv.dk-gennemløb af slægtstræet", "",
          "Hver person med mindst tre navneord er søgt på arkiv.dk. Træf, der nævner",
          "et af personens egne stednavne, er markeret med **>>>**.", ""]
antal_sogt = sprunget = fundet = 0

for n in range(1, maks + 1):
    x = "X%d" % n
    try:
        f = facts(x)
    except Exception:                                        # noqa: BLE001
        continue
    if not f:
        continue
    if any(t.startswith("1 RESN privacy") for t in f):
        continue
    m = None
    for t in f:
        mm = re.search(r"^1 NAME (.+)$", t, re.M)
        if mm and "2 TYPE AKA" not in t:
            m = mm
            break
    if not m:
        continue
    navn = m.group(1).replace("/", "").strip()
    if len(navn.split()) < 3:
        sprunget += 1
        continue
    steder = set()
    for t in f:
        for p in re.findall(r"^2 (?:PLAC|ADDR) (.+)$", t, re.M):
            for d in re.split(r"[,;]", p):
                d = d.strip()
                if len(d) > 3 and d not in ("Danmark", "Sverige", "Tyskland"):
                    steder.add(d)
    try:
        antal, poster = soeg(navn)
    except Exception as e:                                   # noqa: BLE001
        linjer.append("- %s **%s** — fejl: %s" % (x, navn, e))
        continue
    antal_sogt += 1
    time.sleep(PAUSE)
    if antal <= 0:
        continue
    if antal > GRAENSE:
        linjer.append("- %s **%s** — %d træf, for almindeligt navn" % (x, navn, antal))
        continue
    traf = []
    for sti, txt in poster[:12]:
        mark = ">>>" if any(s.lower() in txt.lower() for s in steder) else "   "
        traf.append("    %s arkiv.dk%s  %s" % (mark, sti, txt))
    if traf:
        fundet += 1
        linjer.append("")
        linjer.append("### %s — %s  (%d træf)" % (x, navn, antal))
        if steder:
            linjer.append("    steder: %s" % ", ".join(sorted(steder)[:8]))
        linjer += traf
    print("%-6s %-42s %5d" % (x, navn[:42], antal))

linjer += ["", "---", "",
           "Søgt: %d personer. Sprunget over (under tre navneord): %d. "
           "Med træf: %d." % (antal_sogt, sprunget, fundet)]
UD.write_text("\n".join(linjer), encoding="utf-8")
print("\nrapport:", UD)
