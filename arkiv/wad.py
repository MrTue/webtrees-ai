# -*- coding: utf-8 -*-
"""wad.py -- soeg i Wads Sedler hos Danske Slaegtsforskere.

    python arkiv\\wad.py Eksempelsen Prøvesen       # efternavne (indeholder)
    python arkiv\\wad.py --start Eksem              # navnet skal BEGYNDE saadan
    python arkiv\\wad.py --fornavn Mads
    python arkiv\\wad.py --sted Viborg              # stednavneregistret
    python arkiv\\wad.py --stilling Bager
    python arkiv\\wad.py --seddel 12345 "Eksempelsen Anders"   # én seddel, fuldt ud
    python arkiv\\wad.py --hent 12345 "Eksempelsen Anders" ud.jpg

Landsarkivar Gustav Ludvig Wads sedler, 1893-1924: et kartotek over personer,
han stoedte paa i danske arkivalier. 36.381 indtastede navne (feb. 2021);
selve sedlerne er fotograferet, og indtastningen er kun NAVNENE -- selve
seddelteksten skal laeses paa billedet.

Formen er GET, ingen cookies, ingen login:

  navneliste  vis_navne.php?page_id=14&stil=1|2&navn=<ord>&sort=e|f|s|st|i&ret=12
              stil=1 «starter med», stil=2 «indeholder»
              sort=e efternavn · f fornavn · s stednavn · st stilling · i billed-id
              Jokertegn: _ ét bogstav, % ét eller flere
  seddel      vis_sedler.php?page_id=15&sort=e&vis=2&id_nr=<n>&navn=<Efter+For>
              NB: BAADE id_nr OG navn skal med. Uden navn svarer serveren med
              en tilfaeldig seddel (altid #384 «Bager») -- det ligner et svar
              og er det ikke.
  billede     wad_data/<mappe>/<billednavn>.jpg -- kraever Referer-hoved,
              ellers kommer der et 1,3 kB pladsholderbillede. 900x548 px.
"""
import html
import os
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

ROD = "https://sedler.dis-danmark.dk/wad/"
HOVED = {"User-Agent": "Mozilla/5.0", "Referer": ROD}


def hent(sti):
    req = urllib.request.Request(ROD + sti, headers=HOVED)
    return urllib.request.urlopen(req, timeout=90).read()


def ren(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).replace("\xa0", " ").strip()


def navneliste(ord_, stil=2, sort="e"):
    """-> [(nr, 'Efternavn Fornavn', antal)] fra navneregistret."""
    q = urllib.parse.urlencode({"page_id": "14", "stil": str(stil), "navn": ord_,
                                "sort": sort, "ret": "12"})
    t = hent("vis_navne.php?" + q).decode("utf-8", "replace")
    t = t[t.find("cpg_main_block"):]
    ud = []
    for m in re.finditer(r'<a[^>]*href="vis_sedler\.php\?([^"]+)"[^>]*>(.*?)</a>(.*?)(?=<a|</td)',
                         t, re.S):
        par = urllib.parse.parse_qs(html.unescape(m.group(1)))
        navn = par.get("navn", [""])[0]
        nr = (par.get("nr") or par.get("id_nr") or [""])[0]
        antal = re.search(r"\((\d+)\)", ren(m.group(3)))
        ud.append((nr, navn, int(antal.group(1)) if antal else 1))
    return ud


def alle_idnr(nr, navn):
    """Navnesoejlen paa en seddelside ER det alfabetiske register: den rummer
    ét id_nr per FOREKOMST. Herfra hentes alle sedler, et navn optraeder paa."""
    raa = _side(nr, navn, "nr")
    kol = raa[raa.find("Det s&oslash;gte navn"):]
    ud, set_ = [], set()
    for q in re.findall(r'href="/wad/vis_sedler\.php\?([^"]+)"', kol):
        par = urllib.parse.parse_qs(html.unescape(q))
        if par.get("navn", [""])[0].strip() == navn.strip():
            v = par.get("id_nr", [""])[0]
            if v and v not in set_:
                set_.add(v)
                ud.append(v)
    return ud or [nr]


def _side(v, navn, felt):
    q = urllib.parse.urlencode({"page_id": "15", "sort": "e", "vis": "2",
                                felt: str(v), "navn": navn})
    return hent("vis_sedler.php?" + q).decode("utf-8", "replace")


def seddel(id_nr, navn, felt="id_nr"):
    """-> dict med hovedperson, stilling/aar, andre navne, seddel-id, billede."""
    raa = _side(id_nr, navn, felt)
    t = raa[raa.find("cpg_main_block"):]
    t = t[:t.find("Det s&oslash;gte navn")]  # naboerne i navnesoejlen skal ikke med

    d = {"id_nr": str(id_nr), "navn": navn}
    m = re.search(r"Sedlens hovedperson:(.*?)</t", t, re.S)
    d["hovedperson"] = ren(m.group(1)) if m else ""
    m = re.search(r"Seddel-Id:\s*</?[^>]*>?\s*#?(\d+)", ren(t).replace(" ", "")) \
        or re.search(r"Seddel-Id:\s*#?(\d+)", ren(t))
    d["seddel_id"] = m.group(1) if m else ""
    m = re.search(r"pic_id=([^'\"]+\.jpg)", raa)
    d["billede"] = m.group(1) if m else ""

    # stilling/sted/aar staar som links til stillings- og stednavneregistret
    d["stilling"] = [ren(x) for x in re.findall(r'sort=st&amp;ret=12"[^>]*>(.*?)</a>', t)]
    d["sted"] = [ren(x) for x in re.findall(r'sort=s&amp;ret=12"[^>]*>(.*?)</a>', t)]
    m = re.search(r"\b(1[0-9]{3})\b", ren(t))
    d["aar"] = m.group(1) if m else ""
    d["andre"] = [ren(x) for _, x in
                  re.findall(r'href="/wad/vis_sedler\.php\?([^"]+)"[^>]*>([^<]*)</a>', t)
                  if ren(x)]
    m = re.search(r"Billednavn:\s*([\w]+)", ren(raa))
    d["billednavn"] = m.group(1) if m else ""
    return d


def vis(d):
    print("  seddel #%s (id_nr %s)  %s" % (d["seddel_id"], d["id_nr"], d["hovedperson"]))
    if d["stilling"] or d["sted"] or d["aar"]:
        print("        %s %s %s" % (", ".join(d["stilling"]), ", ".join(d["sted"]), d["aar"]))
    if d["andre"]:
        print("        nævnt sammen med: %s" % " · ".join(d["andre"]))
    if d["billede"]:
        print("        %s%s" % (ROD, d["billede"]))


def hent_billed(id_nr, navn, ud):
    d = seddel(id_nr, navn)
    if not d["billede"]:
        sys.exit("ingen billedsti i svaret")
    data = hent(d["billede"])
    if len(data) < 5000:
        sys.exit("kun %d bytes -- Referer-hovedet blev afvist" % len(data))
    open(ud, "wb").write(data)
    print("%s  (%d kB)" % (os.path.abspath(ud), len(data) // 1024))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "--seddel":
        vis(seddel(a[1], a[2]))
    elif a[0] == "--hent":
        hent_billed(a[1], a[2], a[3])
    else:
        stil, sort, ord_ = 2, "e", None
        i = 0
        while i < len(a):
            if a[i] == "--start":
                stil = 1
            elif a[i] == "--fornavn":
                sort = "f"
            elif a[i] == "--sted":
                sort = "s"
            elif a[i] == "--stilling":
                sort = "st"
            else:
                ord_ = a[i]
                r = navneliste(ord_, stil, sort)
                print("== %s: %d navn(e)" % (ord_, len(r)))
                for nr, navn, antal in r:
                    print("   %-8s %-45s %s" % (nr, navn, "(%d sedler)" % antal if antal > 1 else ""))
                    if len(r) <= 15:
                        try:
                            for v in alle_idnr(nr, navn):
                                vis(seddel(v, navn))
                        except Exception as e:
                            print("        (kunne ikke hentes: %s)" % e)
            i += 1
        if ord_ is None:
            sys.exit(__doc__)
