# -*- coding: utf-8 -*-
"""roster.py [maks] — hele traeet paa én linje per person: xref, navn, f/d, steder, levende?"""
import html
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from webtrees_klient import WebtreesClient, load_creds  # noqa: E402

creds = load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
c = WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])

maks = int(sys.argv[1]) if len(sys.argv) > 1 else 420
for n in range(1, maks + 1):
    x = "X%d" % n
    try:
        st, hd, tx = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, x))
    except Exception:                                        # noqa: BLE001
        continue
    if st != 200:
        continue
    f = [html.unescape(t).strip() for t in re.findall(
        r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', tx)]
    if not f:
        continue
    blob = "\n".join(f)
    navn = re.search(r"^1 NAME (.+)$", blob, re.M)
    if not navn:
        continue                                             # familie, kilde, medie
    priv = "JA" if re.search(r"^1 RESN privacy", blob, re.M) else "-"
    b = re.search(r"(?s)^1 BIRT.*?^2 DATE (.+?)$", blob, re.M)
    d = re.search(r"(?s)^1 DEAT.*?^2 DATE (.+?)$", blob, re.M)
    occu = "; ".join(re.findall(r"^1 OCCU (.+)$", blob, re.M))
    steder = []
    for p in re.findall(r"^2 PLAC (.+)$", blob, re.M):
        s = p.split(",")[0].strip()
        if s and s not in steder:
            steder.append(s)
    print("%s|%s|%s|%s|%s|%s|%s" % (
        x, navn.group(1).replace("/", "").strip(),
        b.group(1) if b else "", d.group(1) if d else "",
        ", ".join(steder), occu, priv))
