# -*- coding: utf-8 -*-
"""haeftbarn.py <barn-xref> <familie-xref> [PEDI] — knytter en EKSISTERENDE person
til en familie som barn.

webtrees har ruten /tree/<tree>/link-child-to-family/<xref> med felterne `famid`
og `PEDI`. Tom PEDI betyder biologisk barn. Klienten kan ellers kun oprette nye
personer i en familie; det her lukker hullet.

Viser foerst, hvad der ville blive sendt, og kraever et --gør for at sende.
"""
import html
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from webtrees_klient import WebtreesClient, load_creds  # noqa: E402

barn = sys.argv[1]
familie = sys.argv[2]
pedi = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else ""
goer = "--gør" in sys.argv or "--goer" in sys.argv

creds = load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
c = WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])

sti = "/tree/%s/link-child-to-family/%s" % (c.tree, barn)
st, hd, tx = c._request("GET", sti)
if st != 200:
    raise SystemExit("Kunne ikke åbne %s (svar %s)" % (sti, st))

# famid er en tom-select, der hentes over AJAX — HTML'en har en tom liste.
# Familien efterproeves derfor direkte i traeet i stedet.
stf, hdf, txf = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, familie))
if stf != 200:
    raise SystemExit("Familien %s findes ikke (svar %s)" % (familie, stf))
famfakta = [html.unescape(t).strip() for t in re.findall(
    r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', txf)]
parter = [f for f in famfakta if re.match(r"1 (HUSB|WIFE|CHIL)", f)]
print("Barn:    %s" % barn)
print("Familie: %s  —  %s" % (familie, " · ".join(p.replace("\n", " ") for p in parter)))
print("PEDI:    %r  (tom = biologisk barn)" % pedi)
print("Sender:  POST %s   famid=%s  PEDI=%s" % (sti, familie, pedi or "(tom)"))

if not goer:
    print("\nIntet sendt. Kør igen med --gør for at gennemføre.")
    raise SystemExit(0)

st, hd, tx = c._post(sti, [("famid", familie), ("PEDI", pedi)])
print("\nSvar: %s  %s" % (st, hd.get("location", "")[:100]))

# Efterprøv
st2, hd2, tx2 = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, barn))
fakta = [html.unescape(t).strip() for t in re.findall(
    r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', tx2)]
famc = [f for f in fakta if f.startswith("1 FAMC")]
print("FAMC på %s nu: %s" % (barn, famc or "(ingen)"))
