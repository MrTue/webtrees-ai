# -*- coding: utf-8 -*-
"""Henter Dansk Soeulykke-Statistik fra sbib.dk for en raekke aar."""
import urllib.request, ssl, sys, os

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0"}
D = os.path.dirname(os.path.abspath(__file__))

for aar in sys.argv[1:]:
    u = "https://www.sbib.dk/files/bibliotek/statistik/%s.pdf" % aar
    sti = os.path.join(D, "soeulykke_%s.pdf" % aar)
    if os.path.exists(sti) and os.path.getsize(sti) > 10000:
        print("%s allerede hentet (%d bytes)" % (aar, os.path.getsize(sti)))
        continue
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                                   timeout=180, context=CTX).read()
        open(sti, "wb").write(d)
        print("%s ok  %d bytes" % (aar, len(d)))
    except Exception as e:                                    # noqa: BLE001
        print("%s FEJL %s" % (aar, e))
