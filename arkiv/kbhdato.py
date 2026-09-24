# -*- coding: utf-8 -*-
"""kbhdato.py — soeger Koebenhavns Stadsarkiv paa FOEDSELSDATO i stedet for navn.

Begravelsesprotokollerne, registerbladene og folkeregisterkortene indekserer alle
`dateOfBirth` og `birthplace`. Det goer en soegning paa den eksakte foedselsdato
langt skarpere end en navnesoegning:

  * giftenavne og stavevarianter er ligegyldige — «Anne Marie Eksempelsen» kan staa som
    «Marie Prøvesen», men foedselsdagen 4. maj 1903 er den samme;
  * de umulige navne bliver mulige — et fornavn plus et -sen-navn er der tusinder af,
    men kun en haandfuld er foedt 3. marts 1880;
  * og begravelsesprotokollen fortaeller FOEDESTEDET, som er det, der mangler.

Datoerne hentes fra traeet: hver ikke-nulevende person med en fuld foedselsdato.
"""
import tempfile
import os
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from webtrees_klient import WebtreesClient, load_creds  # noqa: E402

BASE = "https://solr.kbharkiv.dk/solr/apacs_core/select"
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://kbharkiv.dk/"}
SAML = {1: "begravelse", 17: "registerblad", 18: "erindring",
        19: "efterretning", 10: "borgerlig vielse", 150: "folkeregisterkort"}
MDR = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
       "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
UD = Path(((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())) / "kbhdato.md"

creds = load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
c = WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])


def facts(x):
    st, hd, tx = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, x))
    if st != 200:
        return None
    return [html.unescape(t).strip() for t in re.findall(
        r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', tx)]


def solr(q, rows=20):
    p = {"wt": "json", "q": q, "rows": str(rows)}
    d = json.loads(urllib.request.urlopen(urllib.request.Request(
        BASE + "?" + urllib.parse.urlencode(p), headers=UA),
        timeout=90).read().decode("utf-8"))
    return d["response"]["numFound"], d["response"]["docs"]


linjer = ["# Københavns Stadsarkiv — søgt på fødselsdato", "",
          "Navnesøgning drukner i «Nielsen». Fødselsdatoen er derimod entydig, og",
          "begravelsesprotokollerne oplyser **fødested** — netop det, der mangler på",
          "flere af personerne.", ""]
fundet = sogt = 0

for n in range(1, 360):
    x = "X%d" % n
    try:
        f = facts(x)
    except Exception:                                        # noqa: BLE001
        continue
    if not f or any(t.startswith("1 RESN privacy") for t in f):
        continue
    navn = ""
    for t in f:
        m = re.search(r"^1 NAME (.+)$", t, re.M)
        if m and "2 TYPE AKA" not in t and "2 TYPE MARRIED" not in t:
            navn = m.group(1).replace("/", "").strip()
            break
    dato = None
    for t in f:
        if re.match(r"^1 BIRT\b", t):
            d = re.search(r"^2 DATE (\d{1,2}) ([A-Z]{3}) (\d{4})$", t, re.M)
            if d:
                dato = "%s-%02d-%02dT00:00:00Z" % (
                    d.group(3), MDR[d.group(2)], int(d.group(1)))
            break
    if not dato or not navn:
        continue
    q = 'dateOfBirth:"%s"' % dato
    try:
        antal, docs = solr(q)
    except Exception as e:                                   # noqa: BLE001
        print("%-6s %-34s FEJL %s" % (x, navn[:34], e))
        continue
    sogt += 1
    time.sleep(0.35)
    print("%-6s %-34s %s  %3d" % (x, navn[:34], dato[:10], antal))
    if not antal:
        continue
    fundet += 1
    linjer.append("")
    linjer.append("### %s — %s, født %s  (%d træf)" % (x, navn, dato[:10], antal))
    for d in docs[:10]:
        linjer.append("    **%s** · %s %s · fødested: %s · %s · %s" % (
            SAML.get(d.get("collection_id"), d.get("collection_id")),
            d.get("firstnames", ""), d.get("lastname", ""),
            d.get("birthplace", "") or "—",
            d.get("positions", "") or "",
            (d.get("addresses") if isinstance(d.get("addresses"), str)
             else " | ".join(d.get("addresses") or []))[:120]))

linjer += ["", "---", "", "Søgt: %d personer med fuld fødselsdato. Med træf: %d."
           % (sogt, fundet)]
UD.write_text("\n".join(linjer), encoding="utf-8")
print("\nrapport:", UD)
