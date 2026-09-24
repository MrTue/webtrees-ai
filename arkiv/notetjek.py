# -*- coding: utf-8 -*-
"""notetjek.py -- finder NOTER, DER KAN VAERE FORAELDEDE.

    python arkiv\\notetjek.py                 # hele traeet
    python arkiv\\notetjek.py --fra 1900      # kun poster fra og med X1900
    python arkiv\\notetjek.py --ord "ikke fundet"
    python arkiv\\notetjek.py --xref X123     # alt paa een post

DEN SYVENDE KONTROL, og den eneste, der ser paa INDHOLDET af noterne.

Hvorfor den findes: en note skriver, hvad der var kendt DEN DAG den blev skrevet. Naar et spor
senere aabnes, bliver saetningen «hendes doed er ikke undersoegt» staaende og lyver stille
videre. `linktjek` og `markutjek` ser kun paa henvisninger, `gentagtjek` kun paa
kendsgerningstyper -- INGEN AF DEM LAESER TEKSTEN.

Kontrollen kan ikke selv afgoere, om en note er forkert. Den finder de saetninger, der LOVER
noget om fremtiden -- «er ikke fundet», «kendes ikke», «ikke oprettet», «boer soeges» -- og
stiller dem op sammen med, hvad posten rummer i dag. **Doemmet er menneskets.**

TRE BUNKER:
  AABEN     noten siger, at noget mangler -- og posten har det stadig ikke
  MODSAGT   noten siger, at noget mangler -- MEN posten har det nu. Ret den.
  NAVNE     noten siger, at en navngiven person «ikke er oprettet» -- og der findes
            nu en person i traeet med det navn. Slaa op, om det er den samme.
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SCRATCH = (os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH", ""))
FACIT = os.path.join(SCRATCH, "facit.json") if SCRATCH else "facit.json"
if not os.path.exists(FACIT):
    print("finder ikke %s -- saet $env:SLAEGT_ARBEJDSMAPPE, eller koer facit.py" % FACIT)
    raise SystemExit(1)

# Saetninger, der lover noget om fremtiden. Nøglen er det, der mangler.
LOEFTER = [
    (r"(?:er |blev |står )?ikke (?:blevet )?(?:under)?søgt", None),
    (r"ikke (?:blevet )?undersøgt", None),
    (r"ikke fundet", None),
    (r"ikke efterprøvet", None),
    (r"ikke dokumenteret", None),
    (r"ikke oprettet", "PERSON"),
    (r"ikke åbnet", None),
    (r"ikke læst", None),
    (r"kendes ikke", None),
    (r"er ukendt", None),
    (r"står (?:stadig )?åb(?:en|ent)", None),
    (r"bør søges", None),
    (r"mangler", None),
    (r"uafklaret", None),
    (r"ikke afgjort", None),
]

# Hvad et loefte kan handle om, og hvordan man ser, at posten har det nu.
EMNER = [
    ("død",           r"\bdød(?:en|sdato|sindførsel|sfald)?\b",      ("1 DEAT", "1 BURI", "1 CREM")),
    ("fødsel",        r"\bfødsel(?:en|sdato)?\b|\bfødested\b",       ("1 BIRT",)),
    ("dåb",           r"\bdåb(?:en)?\b",                             ("1 CHR", "1 BAPM")),
    ("vielse",        r"\bvielse(?:n|sdato)?\b|\bægteskab(?:et)?\b", ("1 MARR",)),
    ("konfirmation",  r"\bkonfirmation(?:en)?\b",                    ("1 CONF",)),
    ("udvandring",    r"\budvandring(?:en)?\b|\budrejse(?:n)?\b",    ("1 EMIG", "1 IMMI")),
    ("børn",          r"\bbørn(?:ene)?\b|\bbørneflok",               ("1 FAMS",)),
    ("erhverv",       r"\berhverv(?:et)?\b|\bstilling(?:en)?\b",     ("1 OCCU",)),
    ("bopæl",         r"\badresse(?:n)?\b|\bbopæl(?:en)?\b",         ("1 RESI",)),
]

rest = sys.argv[1:]


def flag(navn, standard=None):
    if navn in rest:
        i = rest.index(navn)
        return rest[i + 1] if i + 1 < len(rest) else standard
    return standard


fra = int(flag("--fra", 0) or 0)
kun_ord = flag("--ord")
kun_xref = flag("--xref")

d = json.load(io.open(FACIT, encoding="utf-8"))


def navn_paa(p):
    for f in p["fakta"]:
        t = f["tekst"]
        if t.startswith(("1 NAME", "1 TITL")):
            return re.sub(r"[/]", "", t.split("\n")[0][7:]).strip()
    return ""


def nr(x):
    m = re.match(r"X(\d+)$", x)
    return int(m.group(1)) if m else -1


# HAENDELSESTAGS SKAL HAVE EN PRAECIS DATO, foer de taeller som «fundet».
# Hvorfor: `1 BIRT / 2 DATE ABT 1771` er REGNET UD af en alder ved doeden, og
# `1 MARR Y` betyder «gift, detaljer ukendte». En note, der siger «foedslen er
# ikke fundet», er STADIG SAND ved siden af en ABT-foedsel -- det er jo netop
# derfor, den staar som ABT. Uden den her regel er mere end halvdelen af
# traeffene falske.
MED_DATO = ("1 BIRT", "1 CHR", "1 BAPM", "1 MARR", "1 DEAT", "1 BURI",
            "1 CREM", "1 CONF", "1 EMIG", "1 IMMI", "1 NATU")
UNOEJAGTIG = re.compile(r"^(ABT|BEF|AFT|BET|EST|CAL|FROM|TO)\b", re.I)


def praecis(tekst):
    """Baerer kendsgerningen en dato, man kan bruge — eller er den et skoen?"""
    hoved = tekst.split("\n")[0]
    if hoved[:6] not in {t[:6] for t in MED_DATO}:
        return True                      # FAMS, OCCU, RESI m.fl. baerer sjaeldent dato
    if hoved.strip().endswith(" Y"):     # «1 MARR Y» = gift, detaljer ukendte
        return False
    for linje in tekst.split("\n")[1:]:
        if linje.startswith("2 DATE"):
            return not UNOEJAGTIG.match(linje[7:].strip())
    return False                         # ingen dato overhovedet


# «Hendes doed er ikke soegt» kan gaelde posten selv ELLER soesteren, der er
# naevnt to linjer foer. Kontrollen kan ikke afgoere det; den kan markere det.
ANDEN = re.compile(r"\b(søster(?:en|ens)?|bror(?:en|ens)?|broderen|sønnen|"
                   r"datter(?:en|ens)?|manden|hustruen|moderen|faderen|"
                   r"svigers\w+|barnets)\b", re.I)
# Et loefte inde i et citat er kildens ord, ikke vores. «Opholdssted ubekendt»
# i en afskrift af en gammel protokol er kildens udsagn og skal aldrig «rettes».
CITAT = re.compile(r"«[^»]*»|^\s*(?:2 CONT\s*)?>\s")


# Alle fornavne+efternavne i traeet, til NAVNE-bunken
kendte = {}
for x, p in d.items():
    if p.get("slags") == "PERSON":
        n = navn_paa(p)
        if n:
            kendte.setdefault(n.lower(), []).append(x)

aaben, modsagt, navne = [], [], []

for x, p in sorted(d.items(), key=lambda kv: nr(kv[0])):
    if kun_xref and x != kun_xref:
        continue
    if nr(x) < fra:
        continue
    tags = {f["tekst"].split("\n")[0][:6] for f in p["fakta"] if praecis(f["tekst"])}
    hele = "\n".join(f["tekst"] for f in p["fakta"])
    for f in p["fakta"]:
        t = f["tekst"]
        if "NOTE" not in t[:40] and not t.startswith(("1 NOTE", "1 TEXT")):
            if "2 NOTE" not in t and "3 NOTE" not in t:
                continue
        for linje in t.split("\n"):
            if kun_ord:
                if kun_ord.lower() not in linje.lower():
                    continue
                traef = kun_ord
            else:
                traef = None
                for m, _ in LOEFTER:
                    if re.search(m, linje, re.I):
                        traef = re.search(m, linje, re.I).group(0)
                        break
                if not traef:
                    continue
            kort = re.sub(r"\s+", " ", linje).strip()[:150]
            emne_fundet = False
            # SAETNINGEN, ikke linjen. En note paa ti linjer kan naevne baade en
            # datters doed og en fars erhverv; uden den her afgraensning meldes
            # hver kombination af de to, og listen drukner i falske traef.
            for saetning in re.split(r"(?<=[.!?:;])\s+|—", linje):
                m = re.search(traef, saetning, re.I) if isinstance(traef, str) else None
                if not m:
                    continue
                if CITAT.search(saetning):
                    continue             # kildens ord, ikke vores
                # Markoeren ser paa HELE linjen, ikke kun saetningen: «SØSTEREN
                # FLYTTEDE MED TIL BYEN — MEN HENDES DÅB ER IKKE FUNDET» deles af
                # tankestregen, og «søsteren» havner i den anden halvdel.
                # At markere for meget koster et blik; for lidt koster en fejl.
                mrk = " (SANDSYNLIGVIS EN ANDEN)" if ANDEN.search(linje) else ""
                for emne, moenster, kraev in EMNER:
                    e = re.search(moenster, saetning, re.I)
                    if not e or abs(e.start() - m.start()) > 60:
                        continue
                    emne_fundet = True
                    if any(k[:6] in tags for k in kraev):
                        modsagt.append((x, navn_paa(p), emne + mrk, traef, kort))
                    else:
                        aaben.append((x, navn_paa(p), emne, traef, kort))
            if not emne_fundet:
                aaben.append((x, navn_paa(p), "-", traef, kort))
            # Navngivne personer, der «ikke er oprettet»
            if re.search(r"ikke oprettet", linje, re.I):
                for kandidat in re.findall(r"\*\*([A-ZÆØÅ][^*]{3,40})\*\*", linje):
                    hvor = [y for y in kendte.get(kandidat.lower(), []) if y != x]
                    if hvor:              # postens eget xref taeller ikke
                        navne.append((x, kandidat, hvor))

print("=" * 78)
print("MODSAGT -- noten siger, at noget mangler, men posten har det nu (%d)" % len(modsagt))
print("=" * 78)
for x, n, emne, traef, kort in modsagt:
    print("  %-7s %-32s [%s]  «%s»" % (x, n[:32], emne, traef))
    print("          %s" % kort)

print()
print("=" * 78)
print("NAVNE -- «ikke oprettet», men navnet findes nu i traeet (%d)" % len(navne))
print("=" * 78)
for x, kandidat, hvor in navne:
    # Leveaarene skrives med, for et navnesammenfald er ikke en person. Naevner
    # noten en bror omkring 1800, og er navnefaellen i traeet doed hundrede aar
    # foer, ses det paa et oejeblik her -- og slet ikke uden.
    med_aar = []
    for y in hvor:
        aar = []
        for f in d[y]["fakta"]:
            if f["tekst"][:6] in ("1 BIRT", "1 DEAT"):
                m2 = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", f["tekst"])
                if m2:
                    aar.append(("f." if f["tekst"][:6] == "1 BIRT" else "d.") + m2.group(1))
        med_aar.append("%s (%s)" % (y, " ".join(aar) if aar else "uden årstal"))
    print("  %-7s %-40s -> %s" % (x, kandidat[:40], ", ".join(med_aar)))

print()
print("=" * 78)
print("AABEN -- stadig et aabent spor (%d)" % len(aaben))
print("=" * 78)
for x, n, emne, traef, kort in aaben:
    print("  %-7s %-28s [%s] %s" % (x, n[:28], emne, kort[:100]))

print()
print("%d modsagt · %d navne · %d aabne" % (len(modsagt), len(navne), len(aaben)))
