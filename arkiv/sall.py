# -*- coding: utf-8 -*-
"""sall.py <kategori> [amt] [myndighed] — browser Sall Datas indeks til Arkivalieronline.

Sall Data (ao.salldata.dk) er et alternativt indeks til HELE Arkivalieronline,
ordnet efter kategori og amt, og det giver BSID direkte — netop den noegle,
projektets egne vaerktoejer bruger.

Kategorier:
  kb kirkeboeger · ft folketaellinger · personregister soenderjyske personregistre
  borgerlige borgerlige vielser · stiftelsen Foedselsstiftelsen
  udvandring ud- og indvandring · notarial · faeste faesteprotokoller
  borgerskab · skifter · justits · laegd laegdsruller · medalje erindringsmedaljer
  stamb stamboeger · flaaden · milits · matrikel Chr. V's matrikel 1688
  bygning ejendomshistorie · tingbog tingboeger 1927-2000 · brand brandforsikringer
  gods godsarkiver · retsbetjent · told · rejsende · selskaber · amt · kommune
  medicin

    python sall.py brand                 -> amterne
    python sall.py brand Sorø            -> myndighederne i Sorø amt
    python sall.py brand Sorø "Korsør Købstads Branddirektorat"   -> bindene med bsid
"""
import re
import sys
import urllib.parse
import urllib.request
import html as H

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 slaegtsforskning/1.0"}
BASE = "http://ao.salldata.dk/index.php"


def hent(**p):
    u = BASE + "?" + urllib.parse.urlencode(p)
    return urllib.request.urlopen(
        urllib.request.Request(u, headers=UA), timeout=120).read().decode("utf-8", "replace")


def valg(t, niv):
    """Muligheder i den select, der peger paa naeste niveau."""
    ud = []
    for m in re.finditer(r'(?is)<select[^>]*>(.*?)</select>', t):
        for v, txt in re.findall(r'(?is)<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', m.group(1)):
            navn = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", txt))).strip()
            if navn and ("n%d=" % niv) in H.unescape(v):
                ud.append(navn)
    return sorted(set(ud))


a = sys.argv[1:]
if not a:
    raise SystemExit(__doc__)
p = {"type": a[0]}
if len(a) > 1:
    p["n1"] = a[1]
if len(a) > 2:
    # Sall Datas egne links lyder «n1=<amt>&n2=<herred>&n3=<sogn>», og paa
    # amtssiden staar herredet TOMT. Sender man sognet som n2, faar man nul
    # bind hver gang. Proev derfor n3 foerst og fald tilbage til n2.
    p["n2"] = ""
    p["n3"] = a[2]
t = hent(**p)
if len(a) > 2 and "bsid=" not in t:
    p.pop("n3", None)
    p["n2"] = a[2]
    t = hent(**p)

if len(a) == 1:
    print("AMTER:", ", ".join(valg(t, 1)))
elif len(a) == 2:
    print("MYNDIGHEDER i %s:" % a[1], ", ".join(valg(t, 2)))
else:
    filt = a[3].lower() if len(a) > 3 else None
    n = 0
    for rk in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", t):
        b = re.search(r"bsid=(\d+)", rk)
        if not b:
            continue
        celler = [re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
                  for c in re.findall(r"(?is)<td[^>]*>(.*?)</td>", rk)]
        celler = [c for c in celler if c]
        tekst = " | ".join(celler[2:]) if len(celler) > 2 else " | ".join(celler)
        if filt and filt not in tekst.lower():
            continue
        n += 1
        print("bsid %-8s %s" % (b.group(1), tekst[:150]))
    print("\n%d bind" % n)
