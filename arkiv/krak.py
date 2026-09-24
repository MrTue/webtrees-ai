# -*- coding: utf-8 -*-
"""krak.py — Kraks Vejviser for Koebenhavn 1770-1969, maskinlaest.

    python krak.py --side 1960 navneregister 200          vis én sides OCR
    python krak.py --hoved 1960 navneregister 200         kun sidehovedets opslagsord
    python krak.py --find 1960 navneregister NIELSEN      binaersoeg efter opslagsordet
    python krak.py --scan 1960 navneregister 430 470 "Aa. P"    laes et sidevindue efter et ord
    python krak.py --billede 1960 navneregister 200 ud.jpg      hent sidebilledet

KOEBENHAVNS BIBLIOTEKER har scannet hele raekken og lagt den paa FlippingBook
(`user-9y8ca5x.cld.bz/<publikation>/<side>/`). **Hver sides HTML baerer OCR-fuldteksten**
i `<div class="full-text">`, og sidehovedets opslagsord staar som et af de foerste
afsnit, spatieret: `H A N S`. Det er noeglen til at soege maskinelt i 2.000 sider.

PUBLIKATIONERNE hedder `Kraks-Vejviser-<aar>-<del>`, hvor `<del>` bl.a. er
`navneregister` (personer, ogsaa Frederiksberg og Gentofte) og `gaderegister`
(beboere gade for gade, husnummer for husnummer).

**GADEREGISTRET ER OFTE DEN HURTIGE VEJ.** Skal man finde én Nielsen blandt tusinder,
er navneregistret en naal i en hoestak — men kender man adressen, staar husstanden i
gaderegistret paa én side.

FORBEHOLD, DER SKAL MED I ENHVER NOTE:
  * **OCR'en er raa.** Tal og forkortelser forveksles, og et manglende traef beviser
    intet i sig selv. `--scan` laeser derfor hele vinduet, ikke kun det soegte ord.
  * **Krak er ikke et folkeregister.** Registret rummer husstandsoverhoveder,
    naeringsdrivende og telefonabonnenter — ikke alle indbyggere.
  * Fornavne er forkortede: «Carl J», «Aa. P», «Chr. J». Soeg paa den korte form.
"""
import io
import os
import re
import ssl
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
BASE = "https://user-9y8ca5x.cld.bz"


def pub(aar, del_="navneregister"):
    return "Kraks-Vejviser-%s-%s" % (aar, del_)


def raa(aar, del_, side, forsoeg=3):
    u = "%s/%s/%d/" % (BASE, pub(aar, del_), side)
    for i in range(forsoeg):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=90,
                context=CTX).read().decode("utf-8", "replace")
        except Exception:                                   # noqa: BLE001
            if i == forsoeg - 1:
                raise
            time.sleep(2 + 3 * i)


def afsnit(h):
    """OCR'en som en liste af afsnit."""
    m = re.search(r'(?s)class="full-text"[^>]*>(.*?)</div>', h)
    if not m:
        return []
    return [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", p)).strip()
            for p in re.findall(r"(?s)<p>(.*?)</p>", m.group(1))]


def tekst(aar, del_, side):
    return "\n".join(afsnit(raa(aar, del_, side)))


# Navneregistrets hoved staar spatieret, enten som ét ord («H A N S») eller som et
# spaend («T R A N - T R I P»). Samme side baerer ogsaa linjen «N A V N E - R E G . f.
# K Ø B E N H A V N O G O M E G N», som SKAL sorteres fra — ellers laeser
# binaersoegningen «NAVNE» paa hver eneste side og lander altid paa sidste side.
SPATIERET = re.compile(r"^[A-ZÆØÅ]{2,12}(?:-[A-ZÆØÅ]{2,12})?$")
IKKE_HOVED = {"NAVNE", "NAVNEREG", "NAVNEBEG", "KØBENHAVN", "OMEGN", "KRAK", "REG", "BEG"}
# Gaderegistrets hoved er et spaend: «Hørsholmsgade— Kildevældsgade»
SPAEND = re.compile(r"^([A-ZÆØÅ][\wÆØÅæøå.'\- ]{2,40}?)\s*[—–-]{1,2}\s*([A-ZÆØÅ][\wÆØÅæøå.'\- ]{2,40})$")


def noegle(s):
    """Sammenligningsnoegle: store bogstaver, uden mellemrum, aa/æ/ø/å sidst som i Krak."""
    return re.sub(r"[^A-ZÆØÅ]", "", s.upper())


def hoved(aar, del_, side, h=None):
    """Sidehovedets opslagsord. Navneregistret spatierer det («H A N S»);
    gaderegistret skriver et gadespaend, hvor FOERSTE gade er sidens begyndelse.
    Tom streng, naar hovedet ikke kan laeses."""
    a = afsnit(h if h is not None else raa(aar, del_, side))
    for p in a[:6]:
        u = re.sub(r"\s+", "", p.strip())
        if SPATIERET.match(u):
            f = u.split("-")[0]
            if len(f) >= 3 and f not in IKKE_HOVED and u not in IKKE_HOVED:
                return f
    for p in a[:6]:
        m = SPAEND.match(p.strip())
        if m and not re.search(r"\d", p):
            return noegle(m.group(1))
    return ""


def find(aar, del_, ord_, lav=1, hoej=None, log=print):
    """Binaersoegning paa sidehovedet. Returnerer (side, opslagsord)."""
    ord_ = noegle(ord_)
    if hoej is None:
        hoej = 1200
        while True:                                   # find bogens slutning
            try:
                if not raa(aar, del_, hoej):
                    raise ValueError
                afs = afsnit(raa(aar, del_, hoej))
                if not afs:
                    hoej //= 2
                    if hoej < 50:
                        break
                    continue
                break
            except Exception:                               # noqa: BLE001
                hoej //= 2
                if hoej < 50:
                    break
    bedst = (lav, "")
    while lav <= hoej:
        m = (lav + hoej) // 2
        # spring frem, til en side har et laeseligt hoved
        k, hv = m, ""
        while k <= min(m + 4, hoej) and not hv:
            hv = hoved(aar, del_, k)
            if not hv:
                k += 1
        if not hv:
            hoej = m - 1
            continue
        log("  s.%-5d %s" % (k, hv))
        if hv <= ord_:
            bedst = (k, hv)
            lav = k + 1
        else:
            hoej = m - 1
    return bedst


def scan(aar, del_, fra, til, monster, log=print):
    r = re.compile(monster, re.I)
    ud = []
    for s in range(fra, til + 1):
        try:
            t = tekst(aar, del_, s)
        except Exception:                                   # noqa: BLE001
            log("  s.%-5d — kunne ikke hentes" % s)
            continue
        hv = hoved(aar, del_, s) or "?"
        traf = [m for m in r.finditer(t)]
        log("  s.%-5d %-12s %s" % (s, hv, ("%d TRAEF" % len(traf)) if traf else ""))
        for m in traf:
            i, j = max(0, m.start() - 160), min(len(t), m.end() + 220)
            ud.append((s, t[i:j]))
    return ud


BILLEDE = re.compile(r'(https://[^"\']+page-html5-substrates/page\d+_\d\.jpg[^"\']*)')


def billede(aar, del_, side, ud):
    h = raa(aar, del_, side)
    k = BILLEDE.findall(h)
    if not k:
        return None
    u = max(k, key=lambda x: x)
    d = urllib.request.urlopen(urllib.request.Request(u.replace("&amp;", "&"), headers=UA),
                               timeout=180, context=CTX).read()
    io.open(ud, "wb").write(d)
    return ud, len(d)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        raise SystemExit(1)
    if a[0] == "--side":
        print(tekst(a[1], a[2], int(a[3])))
    elif a[0] == "--hoved":
        print(hoved(a[1], a[2], int(a[3])))
    elif a[0] == "--find":
        s, hv = find(a[1], a[2], a[3])
        print("\n=> s.%d  (%s)" % (s, hv))
    elif a[0] == "--scan":
        for s, k in scan(a[1], a[2], int(a[3]), int(a[4]), a[5]):
            print("\n--- s.%d\n%s" % (s, k))
    elif a[0] == "--billede":
        print(billede(a[1], a[2], int(a[3]), a[4]))
    else:
        print(__doc__)
