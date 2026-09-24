# -*- coding: utf-8 -*-
"""familie.py <person-xref> [FAMS|FAMC] — find familie-xref for en person i traeet.

`webtrees_klient.py` kan kun slaa @ID.FAMS@ op for ops i det SAMME job. Skal en
allerede eksisterende person have et barn eller en aegtefaelle hae­ftet paa, skal
familiens xref kendes paa forhaand — og det er det, denne giver.

    python familie.py X123         -> FAMS (den familie, personen er GIFT ind i)
    python familie.py X123 FAMC    -> FAMC (den familie, personen er BARN i)

Loginfilen laeses af klienten selv; kodeordet passerer aldrig herigennem.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import webtrees_klient as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

if len(sys.argv) < 2:
    print(__doc__)
    raise SystemExit(1)

xref = sys.argv[1]
tag = sys.argv[2].upper() if len(sys.argv) > 2 else "FAMS"

creds = K.load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).parent.parent)
c = K.WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])
print("%s %s = %s" % (xref, tag, c.get_family_link(xref, tag)))
