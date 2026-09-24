# -*- coding: utf-8 -*-
"""tekstkontrol.py <ny.md> <backup.md> [FRA TIL [FRA TIL …]] — kontrol af en slaegtsfortaelling.

To kontroller i én kørsel:

  1. ORDKONTROL — leder efter det redaktionelle stof, stilarket forbyder: gennemgaaet,
     udelukket, opslag, «traeet», «blev fundet», du/din/jeg, formodningsbokse og resten.
     Hver rest skal ses efter: nogle er harmloese («han soegte om navnebevis»), resten rettes.

  2. FAKTAKONTROL — traekker alle datoer, aarstal og **fremhaevede navne** ud af begge filer
     og viser, hvad der er VÆK og hvad der er NYT. **Alt, der er vaek, skal forklares** —
     enten hoerte det til et fjernet redaktionelt afsnit, eller ogsaa skal det ind igen.
     Alt nyt skal kunne findes i den gamle tekst eller i facit.json.
     **Bemaerk:** et linjeskift midt i en dato giver falsk udslag. Efterproev hvert enkelt
     med en soegning i den nye fil, foer du retter noget.

Er kun et udsnit af backuppen skrevet om, saa angiv linjeintervallerne bagefter:

    python arkiv\\tekstkontrol.py ny.md SLAEGTSHISTORIEN.md.bak-… 120 480
    python arkiv\\tekstkontrol.py ny.md SLAEGTSHISTORIEN.md.bak-… 900 1100 1400 1650
"""
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")

FORBUDT = [
    r"gennemgå\w*", r"udeluk\w*", r"\bsøgning\w*", r"\bsøgt\b", r"\bopslag\b", r"\bbsid\b",
    r"scanning\w*", r"\bindeks\w*", r"Arkivalieronline", r"Mediestream", r"FamilySearch",
    r"Danish Family Search", r"webtrees", r"\btræet\b", r"ikke fundet", r"blev fundet",
    r"\ber fundet\b", r"vi ved ikke", r"ved vi ikke", r"negativ\w*", r"\bnullet\b",
    r"\bi går\b", r"senere samme dag", r"læst på", r"ikke læst", r"lærestreg\w*",
    r"\[\[X\d+\]\]", r"registerblad\w*", r"\bdødsregist\w*", r"efterprøv\w*",
    r"\bbestil\w*", r"sidst opdateret", r"senest udvidet", r"Skrevet af Claude",
    r"\bdu\b", r"\bdig\b", r"\bdin\b", r"\bdit\b", r"\bdine\b", r"\bjeg\b", r"\bmig\b",
    r"^> \*\*", r"\bavisarkiv\w*", r"\bkontaktark\w*", r"vides ikke",
]

ny, gl = sys.argv[1], sys.argv[2]
T = io.open(ny, encoding="utf-8-sig").read()
B = io.open(gl, encoding="utf-8-sig").read()
if len(sys.argv) > 4:          # tekstkontrol.py ny.md backup.md FRA TIL  — kun et udsnit
    L = B.split("\n")
    dele = list(zip(sys.argv[3::2], sys.argv[4::2]))
    B = "\n".join("\n".join(L[int(a) - 1:int(b)]) for a, b in dele)
linjer = T.split("\n")

print("=" * 70, "\nORDKONTROL —", ny, "\n" + "=" * 70)
fund = 0
for m in FORBUDT:
    r = re.compile(m, re.I | re.M)
    traef = [(i + 1, l.strip()[:100]) for i, l in enumerate(linjer)
             if r.search(l) and not l.lstrip().startswith("![")]
    if traef:
        fund += len(traef)
        print("\n%-24s %d" % (m, len(traef)))
        for n, l in traef[:6]:
            print("   %5d  %s" % (n, l))
print("\n-- i alt %d rester" % fund)

# Faktakontrol: datoer, aarstal og fremhaevede navne
MAAN = "januar|februar|marts|april|maj|juni|juli|august|september|oktober|november|december"
def fakta(t):
    d = set(re.findall(r"\d{1,2}\.? (?:%s) \d{4}" % MAAN, t))
    a = set(re.findall(r"\b1[5-9]\d\d\b|\b20[0-2]\d\b", t))
    n = set(re.findall(r"\*\*([A-ZÆØÅ][^*]{2,40})\*\*", t))
    return d, a, n

dn, an, nn = fakta(T)
db, ab, nb = fakta(B)
print("\n" + "=" * 70, "\nFAKTAKONTROL mod", gl, "\n" + "=" * 70)
for navn, ny_, gl_ in (("datoer", dn, db), ("årstal", an, ab), ("fremhævede navne", nn, nb)):
    v, k = sorted(gl_ - ny_), sorted(ny_ - gl_)
    print("\n%s: %d i ny, %d i gammel" % (navn, len(ny_), len(gl_)))
    if v:
        print("  VÆK (%d): %s" % (len(v), " · ".join(v)))
    if k:
        print("  NY  (%d): %s" % (len(k), " · ".join(k)))
