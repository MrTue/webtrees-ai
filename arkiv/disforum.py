# -*- coding: utf-8 -*-
"""disforum.py -- soeg i BEGGE slaegtsforskerfora paa én gang.

    python arkiv\\disforum.py Eksempelsen Prøvesen "Vester Eksempelby"
    python arkiv\\disforum.py --gammel Eksempelsen   # kun det lukkede DIS-forum
    python arkiv\\disforum.py --ny Eksempelsen       # kun forum.slaegt.dk
    python arkiv\\disforum.py --traad <url>          # hent og vis en traad

To fora, to teknikker:

**Det gamle DIS-Forum** (`dis-danmark.dk/forum`) er **Phorum**, lukket for nye
indlaeg i 2012, men **stadig laesbart og soegbart**. Det rummer 42.036 traade
alene i AneEfterlysning. Soegningen er TO skridt: `search.php?forum_id=0&search=…`
svarer «Din soegning er i gang» og et `<meta refresh>` til den rigtige adresse,
som har Phorums komma-form:

    search.php?0,search=<ord>,page=<n>,match_type=ALL,match_dates=0,match_forum=ALL

**Hent den anden adresse direkte** -- ellers faar man ventesiden. **Siderne er
windows-1252**, ikke utf-8; afkodes de forkert, forsvinder æøå.
`match_dates` staar som standard paa **30 dage** — og paa et forum, der lukkede
i 2012, giver det **nul**. Saet altid `match_dates=0`.

**Det nye forum** (`forum.slaegt.dk`) er **SMF 2.1** og kan soeges af gaester med
et rent GET: `index.php?action=search2&search=<ord>`. Ingen session, ingen cookie.
Resultatet er UTF-8. Traadene fortsaetter det gamle forums traditioner.

> **Et forumindlaeg er et SPOR, ikke en kilde.** Efterproev i kirkebogen.
"""
import html
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0"}
GAMMEL = "http://www.dis-danmark.dk/forum/"
NY = "https://forum.slaegt.dk/index.php"


def _hent(url, kode="utf-8"):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                  timeout=120).read().decode(kode, "replace")


def _ren(s):
    s = re.sub(r"<(script|style).*?</\1>", "", s, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def gammel(ord_, sider=2):
    """Phorum. -> [(dato, forfatter, titel, forum, url)]"""
    ud = []
    for side in range(1, sider + 1):
        u = (GAMMEL + "search.php?0,search=%s,page=%d,match_type=ALL,"
             "match_dates=0,match_forum=ALL" % (urllib.parse.quote(ord_), side))
        t = _hent(u, "windows-1252")
        if side == 1:
            m = re.search(r"Resultater \d+ - \d+ af (\d+)", _ren(t))
            print("== [gammelt DIS-forum] %s: %s træf" % (ord_, m.group(1) if m else "0"))
            if not m:
                return ud
        for blok in re.split(r'<div class="PhorumRowBlock">', t)[1:]:
            a = re.search(r'<a href="([^"]*read\.php\?[^"]+)"[^>]*>(.*?)</a>', blok, re.S)
            if not a:
                continue
            dato = re.search(r"(\d\d/\d\d/\d\d \d\d:\d\d)", blok)
            forf = re.search(r'profile\.php\?[^"]*"[^>]*>(.*?)</a>', blok, re.S)
            forum = re.search(r'list\.php\?\d+"[^>]*>(.*?)</a>', blok, re.S)
            ud.append((dato.group(1) if dato else "", _ren(forf.group(1)) if forf else "",
                       _ren(a.group(2)), _ren(forum.group(1)) if forum else "", a.group(1)))
    return ud


def ny(ord_):
    """SMF 2.1. -> [(dato, forfatter, titel, uddrag, url)]"""
    t = _hent(NY + "?action=search2&search=" + urllib.parse.quote(ord_))
    ud = []
    for blok in re.split(r'<div class="windowbg"', t)[1:]:
        a = re.search(r'<a href="([^"]*index\.php/topic,[^"]+)"[^>]*>(.*?)</a>', blok, re.S)
        if not a:
            continue
        m = re.search(r'smalltext">(\d\d \w+ \d{4} - \d\d:\d\d) af .*?>([^<]*)</a>', blok, re.S)
        brd = re.search(r'index\.php/board,[^"]*"[^>]*>(.*?)</a>', blok, re.S)
        uddrag = _ren(re.sub(r"\.{4,}", " … ",
                             blok.split('word_break">')[-1]))[:500].lstrip("… ")
        ud.append((m.group(1) if m else "", (m.group(2) if m else "") + " / " +
                   (_ren(brd.group(1)) if brd else ""), _ren(a.group(2)), uddrag, a.group(1)))
    print("== [forum.slaegt.dk] %s: %d træf paa side 1" % (ord_, len(ud)))
    return ud


def traad(url):
    kode = "windows-1252" if "dis-danmark" in url else "utf-8"
    print(_ren(_hent(url, kode))[:12000])


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "--traad":
        traad(a[1]); sys.exit()
    kun = None
    if a[0] in ("--gammel", "--ny"):
        kun, a = a[0][2:], a[1:]
    for ord_ in a:
        if kun != "ny":
            for d, f, ti, fo, u in gammel(ord_):
                print("   %-15s %-24s %-58s %s" % (d, f[:24], ti[:58], fo))
                print("      %s" % u)
        if kun != "gammel":
            for d, f, ti, ud, u in ny(ord_):
                print("   %-22s %-22s %s" % (d, f[:22], ti[:60]))
                if ud:
                    print("      … %s" % ud)
                print("      %s" % u)
