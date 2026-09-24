# -*- coding: utf-8 -*-
"""Prøver en række kandidatkilder og rapporterer, om de svarer maskinelt."""
import re
import sys
import urllib.request
import html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}

MAAL = [
    ("Wads Sedler", "https://sedler.dis-danmark.dk/wad/index.php"),
    ("DK-gravsten", "https://www.dk-gravsten.dk/"),
    ("Findengrav", "https://findengrav.dk/"),
    ("Afdøde (dødsannoncer)", "https://afdoede.dk/"),
    ("Aneguf (dødsboer)", "http://aneguf.dk/"),
    ("Weblager (byggesager)", "https://weblager.dk/"),
    ("DIGDAG", "https://digdag.dk/"),
    ("Krabsens stednavnebase", "https://www.krabsen.dk/stednavnebase/index.php"),
    ("Historiske kort", "https://hkpn.gst.dk/"),
    ("Slægtsbiblioteket", "https://slaegtsbibliotek.dk/"),
    ("Udvandrerarkivet", "https://www.udvandrerarkivet.dk/"),
    ("Danske Slægtsforskere", "https://slaegt.dk/"),
    ("Runeberg (DBL, Wiberg m.m.)", "https://runeberg.org/"),
    ("Trap Danmark", "https://trap.lex.dk/"),
    ("Digitalarkivet (NO)", "https://www.digitalarkivet.no/"),
]

for navn, u in MAAL:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=45)
        t = r.read().decode("utf-8", "replace")
        flad = re.sub(r"\s+", " ", H.unescape(re.sub(
            r"(?is)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", t))).strip()
        forms = len(re.findall(r"(?is)<form", t))
        print("%-30s %3s  %7d tegn  %d formularer" % (navn, r.status, len(t), forms))
        print("      " + flad[:150])
    except Exception as e:
        print("%-30s FEJL %s" % (navn, str(e)[:70]))
