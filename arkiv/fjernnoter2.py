# -*- coding: utf-8 -*-
"""fjernnoter2.py -- fjerner navngivne kendsgerninger ud fra en opgavefil.

    python arkiv\\fjernnoter2.py opgaver.json            # toerkoersel
    python arkiv\\fjernnoter2.py opgaver.json --goer     # gennemfoer

Opgaverne ligger i en JSON-fil
({"X123": ["1 NOTE FT1845 FOR EKSEMPELSOGN", ...], ...}), og en kendsgerning
udpeges ved at dens tekst BEGYNDER med den angivne streng. Selvdeklarationen
«KAN SLETTES» kraeves ikke -- listen er gennemgaaet note for note og godkendt
af brugeren, foer den koeres.

SIKKERHEDSNET:
 * Toerkoersel er standard. Uden --goer sendes intet.
 * Hver streng skal ramme PRAECIS EN kendsgerning; ellers springes hele posten over.
 * Hele teksten skrives i arkiv/FJERNEDE-NOTER.md, FOER posten sendes.
 * Alle oevrige felter sendes ordret tilbage.
"""
import html
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

import webtrees_klient as wk  # noqa: E402

JOURNAL = Path(__file__).resolve().parent / "FJERNEDE-NOTER.md"


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def hent_fakta(c, xref):
    st, hd, tx = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, xref))
    if st != 200:
        raise SystemExit("%s: edit-raw svarede %s" % (xref, st))
    fakta = [html.unescape(t).strip() for t in re.findall(
        r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>', tx)]
    ids = re.findall(r'<input[^>]*name="fact_id\[\]"[^>]*value="([^"]*)"', tx)
    if not ids:
        ids = re.findall(r'<input[^>]*value="([^"]*)"[^>]*name="fact_id\[\]"', tx)
    m = re.search(r'(?s)<textarea[^>]*name="level0"[^>]*>(.*?)</textarea>', tx)
    level0 = html.unescape(m.group(1)).strip() if m else ""
    if len(ids) != len(fakta):
        raise SystemExit("%s: %d fact_id men %d tekstfelter -- stop" % (xref, len(ids), len(fakta)))
    return level0, list(zip(ids, fakta))


def main():
    goer = "--goer" in sys.argv or "--g\u00f8r" in sys.argv
    opgfil = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    opgaver = json.load(io.open(opgfil, encoding="utf-8"))

    creds = wk.load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
    c = wk.WebtreesClient(creds["base_url"], creds["tree"])
    c.login(creds["username"], creds["password"])
    print("*** T\u00d8RK\u00d8RSEL -- intet sendes ***\n" if not goer else "*** GENNEMF\u00d8RER ***\n")

    ialt, sprunget = 0, []
    for xref in sorted(opgaver, key=lambda s: int(s[1:])):
        level0, fakta = hent_fakta(c, xref)
        fjernes, ok = set(), True
        for start in opgaver[xref]:
            traf = [i for i, (fid, t) in enumerate(fakta) if norm(t).startswith(norm(start))]
            if len(traf) != 1:
                print("!! %s: «%s» ramte %d felter -- POSTEN SPRINGES OVER" % (xref, start[:50], len(traf)))
                ok = False
                break
            fjernes.add(traf[0])
        if not ok:
            sprunget.append(xref)
            continue
        print("%s: %d af %d kendsgerninger fjernes" % (xref, len(fjernes), len(fakta)))
        for i in sorted(fjernes):
            print("    - %s" % fakta[i][1].split("\n")[0][:100])
        ialt += len(fjernes)
        if goer:
            with io.open(JOURNAL, "a", encoding="utf-8", newline="") as f:
                for i in sorted(fjernes):
                    fid, t = fakta[i]
                    f.write("### %s  *(fact_id %s, fjernet %s)*\n\n```\n%s\n```\n\n"
                            % (xref, fid, datetime.now().strftime("%d.%m.%Y %H.%M"), t))
            pairs = [("level0", level0)]
            for i, (fid, t) in enumerate(fakta):
                pairs.append(("fact_id[]", fid))
                pairs.append(("fact[]", "" if i in fjernes else t))
            st, hd, tx = c._post("/tree/%s/edit-raw/%s" % (c.tree, xref), pairs)
            if st not in (200, 302, 303):
                raise SystemExit("%s: uventet svar %s -- STOPPER" % (xref, st))
            # efterproev
            _, efter = hent_fakta(c, xref)
            if len(efter) != len(fakta) - len(fjernes):
                raise SystemExit("%s: %d kendsgerninger efter, ventet %d -- STOPPER"
                                 % (xref, len(efter), len(fakta) - len(fjernes)))
    print("\nI ALT %d kendsgerninger%s" % (ialt, "" if goer else " ville blive fjernet"))
    if sprunget:
        print("SPRUNGET OVER: %s" % ", ".join(sprunget))
    return 0


if __name__ == "__main__":
    sys.exit(main())
