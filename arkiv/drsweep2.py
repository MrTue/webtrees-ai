# -*- coding: utf-8 -*-
"""drsweep2.py — som drsweep, men proever OGSAA aegtefaellens efternavn.

Doedsregistret foerer gifte kvinder under GIFTENAVN. En «Maren Prøvesdatter», der
blev gift Eksempelsen, staar der som «EKSEMPELSEN» og findes derfor ikke i foerste runde. Scriptet
henter derfor aegtefaellens efternavn ud af traeet og soeger paa begge.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from webtrees_klient import WebtreesClient, load_creds  # noqa: E402

PY = sys.executable
DR = str(Path(__file__).resolve().parent / "dr.py")
MDR = {"JAN": "jan", "FEB": "feb", "MAR": "mar", "APR": "apr", "MAY": "maj",
       "JUN": "jun", "JUL": "jul", "AUG": "aug", "SEP": "sep", "OCT": "okt",
       "NOV": "nov", "DEC": "dec"}

creds = load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
c = WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])
BUF = {}


def facts(x):
    if x in BUF:
        return BUF[x]
    st, hd, tx = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, x))
    f = [] if st != 200 else [html.unescape(t).strip() for t in re.findall(
        r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', tx)]
    BUF[x] = f
    return f


def dansk(g):
    m = re.match(r"^(\d{1,2}) ([A-Z]{3}) (\d{4})$", g.strip())
    return None if not m else "%d. %s %s" % (int(m.group(1)), MDR[m.group(2)], m.group(3))


def efternavne(x, blob):
    """Eget efternavn plus enhver aegtefaelles."""
    ud = []
    for nv in re.findall(r"^1 NAME .*?/([^/]+)/", blob, re.M):
        if nv and nv not in ud:
            ud.append(nv)
    for fam in re.findall(r"^1 FAMS @([^@]+)@", blob, re.M):
        fb = "\n".join(facts(fam))
        for p in re.findall(r"^1 (?:HUSB|WIFE) @([^@]+)@", fb, re.M):
            if p == x:
                continue
            for nv in re.findall(r"^1 NAME .*?/([^/]+)/", "\n".join(facts(p)), re.M):
                if nv and nv not in ud:
                    ud.append(nv)
    return ud


for n in range(1, 480):
    x = "X%d" % n
    f = facts(x)
    if not f:
        continue
    blob = "\n".join(f)
    if not re.search(r"^1 NAME", blob, re.M) or re.search(r"^1 RESN privacy", blob, re.M):
        continue
    if re.search(r"^1 DEAT", blob, re.M) and re.search(r"(?s)^1 DEAT.*?\n2 DATE", blob, re.M):
        continue
    m = re.search(r"(?s)^1 BIRT\n(?:2 (?!DATE)[^\n]*\n)*2 DATE ([^\n]+)", blob, re.M)
    if not m:
        continue
    dato = dansk(m.group(1))
    if not dato or int(m.group(1)[-4:]) > 1950:
        continue
    navn = re.search(r"^1 NAME ([^\n]+)", blob, re.M).group(1).replace("/", "").strip()
    for efter in efternavne(x, blob):
        aar = int(m.group(1)[-4:])
        try:
            t = subprocess.run([PY, DR, "--efter", efter, "--fra", str(aar - 1),
                                "--til", str(aar + 1)], capture_output=True,
                               timeout=600).stdout.decode("utf-8", "replace")
        except Exception:                                    # noqa: BLE001
            continue
        traf = [l.strip() for l in t.splitlines() if dato in l]
        if traf:
            print("\n>>> %-6s %-30s f. %-14s som «%s»" % (x, navn[:30], dato, efter), flush=True)
            for l in traf:
                print("      " + re.sub(r"\s+", " ", l)[:220], flush=True)
