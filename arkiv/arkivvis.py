# -*- coding: utf-8 -*-
"""arkivvis.py <id> [id ...] — viser en arkiv.dk-post i fuld laengde.
Beskrivelsen ligger i den raa HTML paa /vis/<id>."""
import urllib.request, ssl, sys, re, html

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0"}
FELTER = ["Nummer", "Type", "Beskrivelse", "Bemærkning", "Periode", "Fotograf", "Arkiv"]

for i in sys.argv[1:]:
    t = urllib.request.urlopen(
        urllib.request.Request("https://arkiv.dk/vis/" + i, headers=UA),
        timeout=90, context=CTX).read().decode("utf-8", "replace")
    f = re.sub(r"\s+", " ", html.unescape(
        re.sub(r"(?s)<script.*?</script>", " ", re.sub(r"<[^>]+>", " ", t))))
    print("=" * 72)
    print("arkiv.dk/vis/" + i)
    for k, navn in enumerate(FELTER):
        m = re.search(re.escape(navn) + r" (.*?) (?=" +
                      "|".join(re.escape(x) for x in FELTER[k + 1:] + ["Tags", "Kontakt arkivet"]) +
                      ")", f)
        if m:
            print("  %-12s %s" % (navn, m.group(1).strip()))
