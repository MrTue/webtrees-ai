# -*- coding: utf-8 -*-
"""kbhsweep.py [maks-xref] — koerer hele traeet gennem Koebenhavns Stadsarkivs Solr.

Fire samlinger paa en gang:
     1 = Begravelsesprotokoller
    17 = Politiets registerblade 1890-1923
    18 = Erindringer
    19 = Politiets efterretninger   (efterlyste, undvegne, straffede)

STRATEGIEN er efternavn + foedselsaar med to aars slup, for registerblade og
begravelsesprotokoller foerer begge dele. Personer uden foedselsaar soeges paa
det fulde navn i fritekst. Nulevende springes over.

Registerbladene er guld: hvert blad har aegtefaelle og hjemmeboende boern med
fulde navne og foedselsdatoer, og en adresseliste, der foelger familien rundt i
byen aar for aar.
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
SAML = {1: "begravelse", 17: "registerblad", 18: "erindring", 19: "efterretning"}
PAUSE = 0.4
UD = Path(((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())) / "kbhsweep.md"

creds = load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
c = WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])


def facts(x):
    st, hd, tx = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, x))
    if st != 200:
        return None
    return [html.unescape(t).strip() for t in re.findall(
        r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', tx)]


def solr(q, rows=25):
    p = {"wt": "json", "q": q, "rows": str(rows), "sort": "lastname asc"}
    u = BASE + "?" + urllib.parse.urlencode(p)
    d = json.loads(urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=90).read().decode("utf-8"))
    return d["response"]["numFound"], d["response"]["docs"]


def dato(s):
    return (s or "")[:10]


def vis(doc):
    """En traeflinje plus det, registerbladet ellers gemmer."""
    ud = []
    saml = SAML.get(doc.get("collection_id"), str(doc.get("collection_id")))
    ud.append("    **%s** · %s %s · f. %s %s · %s" % (
        saml, doc.get("firstnames", ""), doc.get("lastname", ""),
        dato(doc.get("dateOfBirth")) or doc.get("yearOfBirth", ""),
        doc.get("birthplace", "") or "", doc.get("positions", "") or ""))
    if doc.get("addresses"):
        a = doc["addresses"]
        ud.append("        adresser: %s" % (
            " | ".join(a[:6]) if isinstance(a, list) else a))
    try:
        o = json.loads(doc.get("jsonObj", "{}"))
    except Exception:                                        # noqa: BLE001
        return ud
    for s in o.get("spouses") or []:
        ud.append("        ÆGTEFÆLLE %s %s f. %s %s" % (
            s.get("firstnames", ""), s.get("lastname", ""),
            dato(s.get("dateOfBirth")), s.get("birthplace") or ""))
    for b in o.get("children") or []:
        ud.append("        BARN %s %s f. %s (alder %s)" % (
            b.get("firstnames", ""), b.get("lastname", "") or "",
            dato(b.get("dateOfBirth")), b.get("age", "")))
    return ud


maks = int(sys.argv[1]) if len(sys.argv) > 1 else 350
linjer = ["# Københavns Stadsarkiv — hele træet gennem fire samlinger", "",
          "Begravelsesprotokoller · politiets registerblade 1890-1923 · erindringer ·",
          "**politiets efterretninger**. Søgt på efternavn + fødselsår (±2) og, hvor",
          "fødselsåret mangler, på det fulde navn i fritekst.", ""]
sogt = sprunget = medtraf = 0

for n in range(1, maks + 1):
    x = "X%d" % n
    try:
        f = facts(x)
    except Exception:                                        # noqa: BLE001
        continue
    if not f:
        continue
    if any(t.startswith("1 RESN privacy") for t in f):
        sprunget += 1
        continue
    navn = ""
    for t in f:
        m = re.search(r"^1 NAME (.+)$", t, re.M)
        if m and "2 TYPE AKA" not in t and "2 TYPE MARRIED" not in t:
            navn = m.group(1).strip()
            break
    if not navn:
        continue
    efter = ""
    me = re.search(r"/([^/]*)/", navn)
    if me:
        efter = me.group(1).strip()
    rent = navn.replace("/", "").strip()
    aar = ""
    for t in f:
        if re.match(r"^1 BIRT\b", t):
            d = re.search(r"^2 DATE (.+)$", t, re.M)
            if d:
                y = re.findall(r"\b(1[6-9]\d\d|20\d\d)\b", d.group(1))
                if y:
                    aar = y[-1]
            break
    if aar and int(aar) > 1930:
        sprunget += 1
        continue
    if efter and aar:
        q = 'lastname:"%s" AND yearOfBirth:[%d TO %d]' % (efter, int(aar) - 2, int(aar) + 2)
    elif efter and len(rent.split()) >= 3:
        q = 'fullname:"%s"' % rent
    else:
        sprunget += 1
        continue
    try:
        antal, docs = solr(q)
    except Exception as e:                                   # noqa: BLE001
        linjer.append("- %s **%s** — fejl: %s" % (x, rent, e))
        continue
    sogt += 1
    time.sleep(PAUSE)
    print("%-6s %-38s %-46s %4d" % (x, rent[:38], q[:46], antal))
    if not antal:
        continue
    medtraf += 1
    linjer.append("")
    linjer.append("### %s — %s  (%d træf)" % (x, rent, antal))
    linjer.append("    søgning: `%s`" % q)
    for doc in docs[:12]:
        linjer += vis(doc)

linjer += ["", "---", "",
           "Søgt: %d personer. Sprunget over (nulevende, født efter 1930 eller "
           "uden brugbart navn): %d. Med træf: %d." % (sogt, sprunget, medtraf)]
UD.write_text("\n".join(linjer), encoding="utf-8")
print("\nrapport:", UD)
