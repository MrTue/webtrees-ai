# -*- coding: utf-8 -*-
"""linktjek.py [xref ...] — finder [[...]]-henvisninger, der ikke peger på et
xref, som findes i traeet.

Uden argumenter gennemgaas HELE traeet (xref X1 og opefter, indtil tyve i
traek mangler). Med argumenter kun de naevnte poster.

HVORFOR: klienten erstatter `@ID@` med det skabte xref, men IKKE `[[ID]]`.
Skriver man `[[MINKILDE]]` i en jobfil, bliver det staaende som doed markup i
traeet. Det samme sker, hvis man skriver `[[X999]]` om en post, der aldrig
blev oprettet.

RETTES MED: arkiv/erstat.py <xref> "[[gammel]]" "[[ny]]" --goer
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import webtrees_klient as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
creds = K.load_creds(Path.home() / ".webtrees" / "login.json",
                     Path(__file__).resolve().parent.parent)
c = K.WebtreesClient(creds["base_url"], creds["tree"])
c.login(creds["username"], creds["password"])

FAK = re.compile(r'(?s)<textarea[^>]*name="fact\[\]"[^>]*>(.*?)</textarea>')
LINK = re.compile(r"\[\[([^\]]{1,60})\]\]")


def hent(x):
    s, _, t = c._request("GET", "/tree/%s/edit-raw/%s" % (c.tree, x))
    if s != 200:
        return None
    return [html.unescape(a).strip() for a in FAK.findall(t) if a.strip()]


if len(sys.argv) > 1:
    liste = sys.argv[1:]
else:
    liste, n, tomme = [], 0, 0
    while tomme < 20:
        n += 1
        liste.append("X%d" % n)
        if n > 2000:
            break
        tomme = 0  # selve proeven sker nedenfor

tekster, findes = {}, set()
tomme = 0
for x in liste:
    f = hent(x)
    if f is None:
        tomme += 1
        if len(sys.argv) == 1 and tomme >= 20:
            break
        continue
    tomme = 0
    findes.add(x)
    tekster[x] = f

print("laest: %d poster" % len(findes))
fejl = 0
for x in sorted(tekster, key=lambda s: int(s[1:])):
    for f in tekster[x]:
        for m in sorted(set(LINK.findall(f))):
            if re.fullmatch(r"X\d+", m):
                if m in findes:
                    continue
                if hent(m) is not None:
                    findes.add(m)
                    continue
                print("  DOED xref   %-7s -> [[%s]]" % (x, m))
                fejl += 1
            else:
                print("  IKKE-XREF   %-7s -> [[%s]]" % (x, m))
                fejl += 1
print("\n%d problematiske henvisninger" % fejl)
if fejl:
    print("ret dem med:  python arkiv\\erstat.py <xref> \"[[gammel]]\" "
          "\"[[ny]]\" --goer")
