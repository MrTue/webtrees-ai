# -*- coding: utf-8 -*-
"""sbib.py <soegeord> — finder digitaliserede boeger paa Slaegtsforskernes
Bibliotek (Danskernes Historie Online), hvis titel rummer soegeordet."""
import urllib.request, ssl, sys, re, html

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0"}
ord_ = sys.argv[1]

u = "https://slaegtsbibliotek.dk/online-lister/alle-online"
t = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                           timeout=180, context=CTX).read().decode("utf-8", "replace")

for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', t, re.S):
    titel = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))).strip()
    if titel and re.search(ord_, titel, re.I):
        print("%-70s  %s" % (m.group(1)[:70], titel[:120]))
