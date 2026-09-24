# -*- coding: utf-8 -*-
"""bogsoeg.py — henter lokalhistoriske boeger fra Slaegtsbiblioteket og soeger i dem.

    python bogsoeg.py <url> <soegeord> [<soegeord> ...]

Boegerne er store — en sognehistorie kan fylde 80 MB — og serveren taber
forbindelsen undervejs. Derfor hentes de i bidder med Range og genoptages, hvor
de slap. Filen caches, saa den kun hentes én gang.
"""
import tempfile
import os
import re
import ssl
import sys
import time
import urllib.request
from pathlib import Path

from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
CACHE = Path(((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH")) or tempfile.gettempdir())) / "boeger"


def stoerrelse(url):
    r = urllib.request.urlopen(urllib.request.Request(url, headers=UA, method="HEAD"),
                               timeout=120, context=CTX)
    return int(r.headers.get("Content-Length") or 0)


def hent(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    n = CACHE / url.rsplit("/", 1)[-1]
    maal = stoerrelse(url)
    for forsoeg in range(40):
        har = n.stat().st_size if n.exists() else 0
        if maal and har >= maal:
            return n
        h = dict(UA)
        if har:
            h["Range"] = "bytes=%d-" % har
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=h),
                                       timeout=300, context=CTX)
            with open(n, "ab" if har else "wb") as f:
                while True:
                    bid = r.read(1 << 20)
                    if not bid:
                        break
                    f.write(bid)
        except Exception as e:                               # noqa: BLE001
            print("   (afbrudt ved %d/%d — %s)" % (
                n.stat().st_size if n.exists() else 0, maal, type(e).__name__), flush=True)
            time.sleep(2)
    return n


url = sys.argv[1]
ord_ = sys.argv[2:]
sti = hent(url)
print("hentet: %s (%.1f MB)" % (sti.name, sti.stat().st_size / 1e6), flush=True)
r = PdfReader(str(sti))
print("%d sider" % len(r.pages), flush=True)

sider = []
for i, p in enumerate(r.pages, 1):
    try:
        t = p.extract_text() or ""
    except Exception:                                        # noqa: BLE001
        t = ""
    t = re.sub(r"-\s*\n\s*", "", t)
    sider.append(re.sub(r"\s+", " ", t))

for o in ord_:
    traf = 0
    print("\n########## %s" % o, flush=True)
    for i, t in enumerate(sider, 1):
        for m in re.finditer(o, t, re.I):
            traf += 1
            a, b = max(0, m.start() - 350), min(len(t), m.end() + 450)
            print("--- s.%d: %s" % (i, t[a:b]), flush=True)
            if traf >= 14:
                break
        if traf >= 14:
            print("(afbrudt ved 14)", flush=True)
            break
    print("== %d træf" % traf, flush=True)
