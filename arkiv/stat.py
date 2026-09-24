# -*- coding: utf-8 -*-
"""stat.py <soegeord> [...] — Statstidende, Civilstyrelsens kundgoerelser.

    python arkiv\\stat.py "Karen Eksempelsen"
    python arkiv\\stat.py --vis Eksempelsen        # ogsaa de enkelte meddelelser
    python arkiv\\stat.py --rubrik Doedsboer Proevesen

APPENS EGET ENDEPUNKT, som det ses i browserens netvaerksfane:

    GET https://www.statstidende.dk/api/messagesearch?t=<fritekst>&page=0&ps=25&o=40

**FRITEKSTFELTET HEDDER `t`, ikke `q`.** Med `q` svarer serveren med HELE registret
(367.175 meddelelser) og ser fuldstaendig ud som et vellykket opslag — den vaerste slags
fejl. **Efterproev altid paa et navn, du ved findes.**

DAEKNING: bekendtgoerelser fra omkring midten af 2001. Et doedsbo bekendtgoeres ved
**proklama**, som baerer navn, doedsdato og retskreds — men **et bo, der afsluttes som
boudlaeg eller uskiftet bo, bekendtgoeres aldrig.** Et nul betyder derfor ikke, at
personen lever; det kan lige saa godt betyde, at enken sad i uskiftet bo.
Kirkegaardsregistret (`gravsted.py`) er uafhaengigt af skifteretten og fanger flere.

**CPR-NUMRE STAAR I SVARET.** De maskeres her og maa hverken vises, gemmes eller
skrives i traeet.
"""
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
API = "https://www.statstidende.dk/api/messagesearch"
CPR = re.compile(r"\b\d{6}-?\d{4}\b")


def soeg(tekst, side=0, pr=25, rubrik=""):
    p = {"d": "false", "o": "40", "page": side, "ps": pr,
         "userOnly": "false", "t": tekst}
    if rubrik:
        p["s"] = rubrik
    u = API + "?" + urllib.parse.urlencode(p)
    d = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                               timeout=90, context=CTX).read().decode("utf-8", "replace")
    return json.loads(d)


def vis(m):
    felt = {x["name"]: x["value"] for x in m.get("summary", [])}
    felt.pop("CPR-nr.", None)                    # maskeres — maa ikke gemmes
    return "%-14s %-12s %-22s %-34s %s" % (
        m.get("messageNumber", ""), m.get("published", ""),
        m.get("sectionName", "") + "/" + m.get("messageTypeName", ""),
        CPR.sub("******-****", m.get("title", ""))[:34],
        " · ".join("%s %s" % (k, v) for k, v in felt.items()))


if __name__ == "__main__":
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not arg:
        print(__doc__)
        raise SystemExit(1)
    for q in arg:
        d = soeg(q)
        print("%-24s %d meddelelser" % (q, d.get("resultCount", 0)))
        for m in d.get("results", [])[:25]:
            print("   ", vis(m))
