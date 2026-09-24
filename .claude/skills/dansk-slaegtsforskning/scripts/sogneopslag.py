# -*- coding: utf-8 -*-
"""sogneopslag.py — slaar danske sogne op i Sall Datas sognefortegnelse.

    python sogneopslag.py Fuglede Hvilsager        # delstreng, finder ogsaa "Store Fuglede"
    python sogneopslag.py =Nysted =Bogense         # '=' foran: kun sognenavnet selv

Svarer med   sogn | herred | amt   for hver traeffer.

Herredet staar aldrig i kirkebogen, og Arkivalieronlines egen sogneliste opgiver kun amt.
Derfor er denne tabel den eneste hurtige facitliste, der findes — gaet aldrig et herred.

To ting, der har kostet tid:
  * Siden er ren HTTP. En HTTPS-opgradering giver ECONNREFUSED.
  * Teksten er fuld af HTML-entiteter. Uden html.unescape matcher oe og ae ikke,
    og opslaget svarer fejlagtigt "ingen traeffere".
"""
import html
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

URL = "http://www.salldata.dk/sogne/index.php"


def hent():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read()
    # Kodningen er ikke deklareret paalideligt — vaelg den, der giver faerrest skraldtegn
    kandidater = []
    for enc in ("utf-8", "windows-1252", "iso-8859-1"):
        s = raw.decode(enc, "replace")
        kandidater.append((s.count("�") + s.count("Ã"), s))
    return min(kandidater, key=lambda x: x[0])[1]


def linjer(t):
    t = re.sub(r"(?i)</t[dr]>", " | ", t)
    t = re.sub(r"(?i)<tr[^>]*>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    ud = [re.sub(r"\s*\|\s*", " | ", l).strip(" |") for l in t.split("\n")]
    return [l for l in ud if l.strip() and "|" in l]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    alle = linjer(hent())
    for s in sys.argv[1:]:
        print("=== %s ===" % s)
        eksakt = s.startswith("=")
        naal = s[1:] if eksakt else s
        fundet = 0
        for l in alle:
            if eksakt:
                traf = l.split("|")[0].strip().lower() == naal.lower()
            else:
                traf = bool(re.search(re.escape(naal), l, re.I))
            if traf:
                print("   " + l[:120])
                fundet += 1
                if fundet >= 8:
                    print("   … (flere)")
                    break
        if not fundet:
            print("   ingen traeffere")


if __name__ == "__main__":
    main()
