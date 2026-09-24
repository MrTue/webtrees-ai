# -*- coding: utf-8 -*-
"""pdfhent.py <url> <filnavn> — henter en PDF med genforsoeg og
genoptagelse (Range), fordi Slaegtsbiblioteket taber forbindelsen paa
store boeger."""
import os
import ssl
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}

url, ud = sys.argv[1], sys.argv[2]
for forsoeg in range(1, 13):
    haves = os.path.getsize(ud) if os.path.exists(ud) else 0
    h = dict(UA)
    if haves:
        h["Range"] = "bytes=%d-" % haves
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers=h), timeout=120, context=CTX)
        with open(ud, "ab" if haves else "wb") as f:
            while True:
                b = r.read(65536)
                if not b:
                    break
                f.write(b)
        n = os.path.getsize(ud)
        with open(ud, "rb") as f:
            slut = f.read(2048) if n < 2048 else (f.seek(-2048, 2), f.read())[1]
        if b"%%EOF" in slut:
            print("faerdig: %s  (%d bytes, %d forsoeg)" % (ud, n, forsoeg))
            break
        print("  ... %d bytes indtil nu, forsoeg %d" % (n, forsoeg))
    except Exception as e:
        print("  fejl (%s), forsoeg %d" % (e, forsoeg))
    time.sleep(2)
else:
    print("gav op: %s" % ud)
