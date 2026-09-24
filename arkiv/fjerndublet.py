# -*- coding: utf-8 -*-
"""fjerndublet.py -- fjerner en kendsgerning, der står ORDRET to gange på samme post.

    python arkiv\\fjerndublet.py X101 X202 X303             # tørkørsel
    python arkiv\\fjerndublet.py X101 X202 X303 --gør       # gennemfør

`fjernnoter2.py` kan ikke bruges til det her: den kræver, at teksten rammer
**præcis én** kendsgerning, og to ens gør per definition ikke det. Derfor dette
værktøj, som vender kravet om — **den fjerner kun, når to kendsgerninger er ens
tegn for tegn** (efter sammentrækning af mellemrum), og den beholder altid den
første. Er teksterne bare en smule forskellige, er det to udsagn med hver sin
kilde, og så er det ikke en dublet; brug `fjernnoter2.py` og vælg selv.

Dubletterne opstår, når en dåb tilføjes med `add-fact` efter et `add-child`,
som allerede havde taget `1 CHR` med. Se afsnittet om `1 CHR` i AGENTS.md.

Teksten skrives i `arkiv/FJERNEDE-NOTER.md`, før posten sendes -- men i dette
tilfælde går intet tabt, for tvillingen bliver stående.
"""
import io
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

import webtrees_klient as wk  # noqa: E402
from fjernnoter2 import hent_fakta, norm, JOURNAL  # noqa: E402


def main():
    goer = "--goer" in sys.argv or "--g\u00f8r" in sys.argv
    xrefs = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not xrefs:
        sys.exit(__doc__)

    creds = wk.load_creds(Path.home() / ".webtrees" / "login.json", Path(__file__).resolve().parent.parent)
    c = wk.WebtreesClient(creds["base_url"], creds["tree"])
    c.login(creds["username"], creds["password"])
    print("*** T\u00d8RK\u00d8RSEL -- intet sendes ***\n" if not goer else "*** GENNEMF\u00d8RER ***\n")

    ialt = 0
    for xref in xrefs:
        level0, fakta = hent_fakta(c, xref)
        set_, fjernes = {}, set()
        for i, (fid, t) in enumerate(fakta):
            n = norm(t)
            if n in set_:
                fjernes.add(i)
                print("%s: kendsgerning %d er ordret mage til %d -- fjernes" % (xref, i, set_[n]))
                for linje in t.split("\n")[:4]:
                    print("      %s" % linje[:120])
            else:
                set_[n] = i
        if not fjernes:
            print("%s: ingen ordrette dubletter" % xref)
            continue
        ialt += len(fjernes)
        if goer:
            with io.open(JOURNAL, "a", encoding="utf-8", newline="") as f:
                for i in sorted(fjernes):
                    fid, t = fakta[i]
                    f.write("### %s  *(fact_id %s, ordret dublet fjernet %s -- mage til "
                            "en kendsgerning, der bliver st\u00e5ende)*\n\n```\n%s\n```\n\n"
                            % (xref, fid, datetime.now().strftime("%d.%m.%Y %H.%M"), t))
            pairs = [("level0", level0)]
            for i, (fid, t) in enumerate(fakta):
                pairs.append(("fact_id[]", fid))
                pairs.append(("fact[]", "" if i in fjernes else t))
            st, hd, tx = c._post("/tree/%s/edit-raw/%s" % (c.tree, xref), pairs)
            if st not in (200, 302, 303):
                raise SystemExit("%s: uventet svar %s -- STOPPER" % (xref, st))
            _, efter = hent_fakta(c, xref)
            if len(efter) != len(fakta) - len(fjernes):
                raise SystemExit("%s: %d kendsgerninger efter, ventet %d -- STOPPER"
                                 % (xref, len(efter), len(fakta) - len(fjernes)))
            print("    %s: %d kendsgerninger tilbage" % (xref, len(efter)))
    print("\nI ALT %d%s" % (ialt, "" if goer else " ville blive fjernet"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
