# -*- coding: utf-8 -*-
"""cop.py <query> [format] [antal]

Det Kgl. Biblioteks COP-syndikering bag «Danmark set fra luften».
Fundet ved at fremkalde en fejlmeddelelse fra /danmarksetfraluften/async/search/,
som roebte den bagvedliggende adresse:

    https://cop.kb.dk/cop/syndication/images/luftfo/2011/maj/luftfoto/
        ?format=kml&query=<felt>:<vaerdi>&itemsPerPage=..&page=..

Felter: building, location, person, fritekst. Format: kml, rss, json.
Eksempel:  python cop.py building:Solbakken
"""
import urllib.request, urllib.parse, ssl, sys, re, html

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0"}
BASE = "https://cop.kb.dk/cop/syndication/images/luftfo/2011/maj/luftfoto/"

query = sys.argv[1]
fmt = sys.argv[2] if len(sys.argv) > 2 else "kml"
antal = sys.argv[3] if len(sys.argv) > 3 else "40"

u = BASE + "?" + urllib.parse.urlencode(
    {"format": fmt, "query": query, "itemsPerPage": antal, "page": "1"},
    encoding="utf-8")
try:
    t = urllib.request.urlopen(urllib.request.Request(u, headers=UA),
                               timeout=120, context=CTX).read().decode("utf-8", "replace")
except urllib.error.HTTPError as e:
    print("HTTP", e.code, u)
    print(e.read().decode("utf-8", "replace")[:500])
    sys.exit(1)

print("svar:", len(t), "tegn —", u)
# kml: <Placemark><name>..</name><description>..</description>
poster = re.findall(r"(?s)<Placemark>(.*?)</Placemark>", t)
if poster:
    print("placemarks:", len(poster))
    for p in poster[:30]:
        navn = re.search(r"(?s)<name>(.*?)</name>", p)
        besk = re.search(r"(?s)<description>(.*?)</description>", p)
        n = html.unescape(navn.group(1)).strip() if navn else ""
        b = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ",
                   html.unescape(besk.group(1))))).strip() if besk else ""
        print("  * %-42s %s" % (n[:42], b[:150]))
else:
    print(t[:1200])
