# -*- coding: utf-8 -*-
"""distriktsaviser.py <soegeord> ... — slaar en lokalavis op i Det Kgl. Biblioteks
registrant over distriktsaviser i Statens Avissamling.

    python distriktsaviser.py "Struer Posten" Struer

Svarer med titlens aargange og MAGASINNUMMER (fx H-129), som er dét, biblioteket
skal bruge ved en kopibestilling.

HVORFOR DEN FINDES: distriktsaviser og ugeaviser er stort set IKKE digitaliseret.
Mediestream rummer 505 avistitler, og de koebenhavnske er de store historiske
dagblade — ingen lokale ugeaviser fra nyere tid. Et nul i Mediestream betyder
derfor ikke, at avisen ikke findes; den staar bare paa papir i Aarhus.

Registranten daekker aviser fra 1866 og frem, ca. 31.200 bind, pakker og aesker.
Raekkefoelgen er IKKE alfabetisk — titlerne staar som i «Lokalpressen»s
titelregister, saa en avis kan gemme sig under en anden hovedtitel. Derfor skal
man soege paa flere stavemaader og paa bydelen.
"""
import io
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

URL = ("https://www.kb.dk/find-materiale/samlinger/avissamlingen/lister/"
       "liste-over-distriktsaviser/liste-over-distriktsaviser.pdf")


def hent_tekst():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=120).read()
    from pypdf import PdfReader
    r = PdfReader(io.BytesIO(raw))
    sider = []
    for p in r.pages:
        t = p.extract_text() or ""
        t = re.sub(r"\.{3,}", " … ", t)      # de lange punktlinjer
        t = re.sub(r"[ \t]+", " ", t)
        sider.append(t)
    return sider


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    sider = hent_tekst()
    print("registranten: %d sider" % len(sider))
    for naal in sys.argv[1:]:
        print("\n=== %s ===" % naal)
        fundet = 0
        for nr, t in enumerate(sider, 1):
            linjer = [l.strip() for l in t.split("\n") if l.strip()]
            vist = set()          # linjer, en tidligere traeffer allerede har vist
            for i, l in enumerate(linjer):
                if i in vist or not re.search(re.escape(naal), l, re.I):
                    continue
                # en post loeber fra titlen til naeste graa streg
                slut = i + 1
                while slut < len(linjer) and not linjer[slut].startswith("____"):
                    slut += 1
                print("   s.%d:" % nr)
                for j in range(i, slut):
                    print("      %s" % linjer[j][:120])
                    vist.add(j)
                fundet += 1
                if fundet >= 8:
                    break
            if fundet >= 8:
                break
        if not fundet:
            print("   ingen traeffere — proev en anden stavemaade eller bydelen")


if __name__ == "__main__":
    main()
