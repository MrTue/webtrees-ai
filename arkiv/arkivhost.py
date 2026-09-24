# -*- coding: utf-8 -*-
"""arkivhost.py <udfil> <soegeord> [soegeord ...]

Hoester poster fra arkiv.dk: soeger paa hvert ord, samler /vis/-id'erne,
henter hver post og trækker Nummer, Type, Beskrivelse, Bemaerkning, Periode og
Arkiv ud. Beskrivelsen ligger i den raa HTML — ingen grund til WebFetch.

Soegningen er «eller»-baseret, saa giv ét saerpraeget ord ad gangen.
"""
import urllib.request, urllib.parse, ssl, sys, re, html, json, time

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/xhtml+xml"}

udfil = sys.argv[1]
ord_ = sys.argv[2:]


def hent(u, forsoeg=3):
    for i in range(forsoeg):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                                          timeout=90, context=CTX).read().decode("utf-8", "replace")
        except Exception as e:                                 # noqa: BLE001
            if i == forsoeg - 1:
                raise
            time.sleep(2 + 3 * i)


FELTER = ["Nummer", "Type", "Beskrivelse", "Bemærkning", "Periode", "Fotograf", "Arkiv"]


def parse(t):
    f = re.sub(r"\s+", " ", html.unescape(
        re.sub(r"(?s)<script.*?</script>", " ", re.sub(r"<[^>]+>", " ", t))))
    ud = {}
    for i, navn in enumerate(FELTER):
        m = re.search(re.escape(navn) + r" (.*?) (?=" +
                      "|".join(re.escape(x) for x in FELTER[i + 1:] + ["Tags", "Kontakt arkivet"]) +
                      ")", f)
        if m:
            ud[navn] = m.group(1).strip()
    return ud


ider = {}
for o in ord_:
    for side in range(0, 6):
        u = ("https://arkiv.dk/soeg?searchstring=" + urllib.parse.quote(o) +
             ("&page=%d" % side if side else ""))
        try:
            t = hent(u)
        except Exception as e:                                 # noqa: BLE001
            print("%s side %d: FEJL %s" % (o, side, str(e)[:60])); break
        nye = re.findall(r'href="/vis/(\d+)"', t)
        if not nye:
            break
        for n in nye:
            ider.setdefault(n, o)
        print("%-22s side %d: %3d links (i alt %d)" % (o, side, len(set(nye)), len(ider)))
        if len(set(nye)) < 10:
            break

print("=== henter %d poster ===" % len(ider))
poster = []
for k, (i, o) in enumerate(ider.items(), 1):
    try:
        d = parse(hent("https://arkiv.dk/vis/" + i))
    except Exception as e:                                     # noqa: BLE001
        continue
    d["id"] = i
    d["fundet_via"] = o
    poster.append(d)
    if k % 40 == 0:
        print("  %d/%d" % (k, len(ider)))

json.dump(poster, open(udfil, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("gemt:", udfil, len(poster), "poster")
