# -*- coding: utf-8 -*-
"""Lister de bind, AO faktisk viser for et sogn, med perioder."""
import urllib.request, re, json, sys, html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}


def hent(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode("utf-8", "replace")


for ngid, navn in [(int(sys.argv[1]), sys.argv[2])]:
    s = hent("https://arkivalieronline.rigsarkivet.dk/da/geo/archive-series/5/%d" % ngid)
    epids = re.findall(r'data-epid="(\d+)"', s)
    print(navn, "— epid'er:", epids)
    for ep in dict.fromkeys(epids):
        try:
            p = hent("https://arkivalieronline.rigsarkivet.dk/da/geo/picture-series/%s" % ep)
        except Exception as e:
            print("  epid", ep, "FEJL", e)
            continue
        txt = H.unescape(re.sub(r"<[^>]+>", "\n", re.sub(r"<script.*?</script>", " ", p, flags=re.S)))
        linjer = [l.strip() for l in txt.split("\n") if l.strip()]
        bsids = re.findall(r"bsid=(\d+)", p)
        print("  --- epid", ep, " bind:", len(dict.fromkeys(bsids)))
        for l in linjer:
            if re.search(r"(19[3-9]\d|20[0-2]\d)\s*[-–]\s*(19[3-9]\d|20[0-2]\d)", l) or re.search(r"19[5-9]\d", l):
                print("      ", l[:120])
