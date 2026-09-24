# -*- coding: utf-8 -*-
"""bogdata.py <person-xref> [led=5] [--facit <sti>] — raastoffet til en slaegtsfortaelling.

Laeser facit.json (koer arkiv/facit.py foerst) og skriver for proband og hans/hendes aner:

  1. ANETAVLE     ane-nummer (1 = proband, 2 = far, 3 = mor, 4 = farfar …), xref, navn,
                  foedt/doebt, doed, erhverv — og hvilke pladser der er TOMME
  2. FAMILIER     hvert anepar med vielse og HELE boerneflokken ved navn
  3. MEDIER       de scanninger, der haenger paa hver anes kilder — kandidater til billedklip
  4. TAVLER       faerdige udkast til ```tavle-blokke: én per bedsteforaelder-gren + proband

Intet sendes til webtrees, og intet skrives til disk — alt kommer paa skaermen:

    python arkiv\\bogdata.py X1 5 > %SLAEGT_ARBEJDSMAPPE%\\bogdata-X1.txt

Tallene er TRAEETS. Staar der noget andet i en fortaelling, er det fortaellingen, der skal
efterproeves — ikke traeet, der skal rettes efter hukommelsen.
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

MAANED = {"JAN": "januar", "FEB": "februar", "MAR": "marts", "APR": "april", "MAY": "maj",
          "JUN": "juni", "JUL": "juli", "AUG": "august", "SEP": "september",
          "OCT": "oktober", "NOV": "november", "DEC": "december"}
FORKORT = {"ABT": "ca.", "EST": "ca.", "CAL": "ca.", "BEF": "før", "AFT": "efter",
           "BET": "mellem", "AND": "og"}


def facitsti():
    if "--facit" in sys.argv:
        return sys.argv[sys.argv.index("--facit") + 1]
    for sti in (os.path.join((os.environ.get("SLAEGT_ARBEJDSMAPPE") or os.environ.get("CLAUDE_SCRATCH", "")), "facit.json"),
                "facit.json", os.path.join(os.path.dirname(__file__), "facit.json")):
        if sti and os.path.exists(sti):
            return sti
    sys.exit("facit.json blev ikke fundet. Koer arkiv\\facit.py foerst, eller brug --facit <sti>.")


def dato(d):
    """GEDCOM-dato -> dansk: «7 AUG 1873» -> «7. august 1873», «ABT 1820» -> «ca. 1820»."""
    ud = []
    for o in (d or "").split():
        if o in FORKORT:
            ud.append(FORKORT[o])
        elif o in MAANED:
            ud.append(MAANED[o])
        elif o.isdigit() and len(o) <= 2:
            ud.append(o + ".")
        else:
            ud.append(o)
    return " ".join(ud)


def aar(d):
    m = re.search(r"(\d{4})", d or "")
    return m.group(1) if m else ""


class Trae:
    def __init__(self, sti):
        self.d = json.load(io.open(sti, encoding="utf-8"))

    def fakta(self, x):
        return [f["tekst"] for f in self.d.get(x, {}).get("fakta", [])]

    def felt(self, x, tag, under=None):
        """Foerste «1 TAG»-kendsgerning; med under='DATE' den underliggende «2 DATE»."""
        for t in self.fakta(x):
            if re.match(r"1 %s\b" % tag, t):
                if under is None:
                    return t.split("\n")[0][len(tag) + 2:].strip()
                m = re.search(r"^2 %s (.*)$" % under, t, re.M)
                return m.group(1).strip() if m else ""
        return ""

    def peger(self, x, tag):
        return [m for t in self.fakta(x) for m in re.findall(r"^1 %s @(X\d+)@" % tag, t, re.M)]

    def navn(self, x):
        return self.felt(x, "NAME").replace("/", "").replace("  ", " ").strip() or "(uden navn)"

    def foraeldre(self, x):
        for fam in self.peger(x, "FAMC"):
            return (self.peger(fam, "HUSB") or [None])[0], (self.peger(fam, "WIFE") or [None])[0], fam
        return None, None, None

    def foedt(self, x):
        d, p = self.felt(x, "BIRT", "DATE"), self.felt(x, "BIRT", "PLAC")
        if not d:
            d, p = self.felt(x, "CHR", "DATE"), self.felt(x, "CHR", "PLAC")
            if d:
                return "døbt " + dato(d) + (" i " + p.split(",")[0] if p else "")
        return ("f. " + dato(d) if d else "") + (" i " + p.split(",")[0] if d and p else "")

    def doed(self, x):
        d, p = self.felt(x, "DEAT", "DATE"), self.felt(x, "DEAT", "PLAC")
        return ("† " + dato(d) if d else "") + (" i " + p.split(",")[0] if d and p else "")

    def levetid(self, x, fuld=False):
        """(1886-1961) — eller med fuld=True «(* 9. april 1886 · † 17. januar 1961)»."""
        if not fuld:
            f = aar(self.felt(x, "BIRT", "DATE") or self.felt(x, "CHR", "DATE"))
            d = aar(self.felt(x, "DEAT", "DATE") or self.felt(x, "BURI", "DATE"))
            if f and d:
                return "(%s-%s)" % (f, d)
            return "(f. %s)" % f if f else ("(† %s)" % d if d else "")
        ud = []
        for tegn, tags in (("*", (("BIRT", ""), ("CHR", "døbt "))),
                           ("†", (("DEAT", ""), ("BURI", "begr. ")))):
            for tag, ord_ in tags:
                d = self.felt(x, tag, "DATE")
                if d:
                    ud.append("%s %s%s" % (tegn, ord_, dato(d)))
                    break
        return "(%s)" % " · ".join(ud) if ud else ""

    def medier(self, x):
        """Filerne bag de kilder, personens kendsgerninger citerer — plus egne OBJE."""
        ud = []
        kilder = {m for t in self.fakta(x) for m in re.findall(r"SOUR @(X\d+)@", t)}
        for k in sorted(kilder | {x}, key=lambda s: int(s[1:])):
            for o in self.peger(k, "OBJE"):
                fil, titel = self.felt(o, "FILE"), self.felt(o, "FILE", "TITL")
                if fil and (fil, titel) not in ud:
                    ud.append((fil, titel))
        return ud


def tavlenavn(T, x):
    lev, erhv = T.levetid(x, fuld=True), T.felt(x, "OCCU")
    return " ".join(s for s in (T.navn(x), lev) if s) + ("; " + erhv if erhv else "")


def par(T, far, mor, fam, gennem=None):
    """gennem = den aegtefaelle, linjen oppefra skal ramme, naar kun den enes foraeldre kendes."""
    def n(x):
        return ("^" if x == gennem else "") + tavlenavn(T, x)
    if far and mor:
        v = aar(T.felt(fam, "MARR", "DATE")) if fam else ""
        return "%s ∞%s %s" % (n(far), "[%s]" % v if v else "", n(mor))
    return tavlenavn(T, far or mor)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--") and a != facit_arg()]
    if not args:
        sys.exit(__doc__)
    proband, led = args[0].strip("@"), int(args[1]) if len(args) > 1 else 5
    T = Trae(facitsti())
    if T.d.get(proband, {}).get("slags") != "PERSON":
        sys.exit("%s er ikke en person i facit.json" % proband)

    aner = {1: proband}
    for n in range(1, 2 ** led):
        if n in aner:
            far, mor, _ = T.foraeldre(aner[n])
            if far:
                aner[2 * n] = far
            if mor:
                aner[2 * n + 1] = mor

    print("=" * 78, "\n1. ANETAVLE for %s %s — %d led\n" % (proband, T.navn(proband), led) + "=" * 78)
    for g in range(led):
        pladser = range(2 ** g, 2 ** (g + 1))
        fundet = [n for n in pladser if n in aner]
        print("\n-- led %d: %d af %d kendt" % (g, len(fundet), len(pladser)))
        for n in fundet:
            x = aner[n]
            print("%4d  %-6s %s" % (n, x, " · ".join(s for s in (
                T.navn(x), T.foedt(x), T.doed(x), T.felt(x, "OCCU")) if s)))
        tomme = [n for n in pladser if n not in aner and n // 2 in aner]
        if tomme:
            print("      TOMME pladser: " + ", ".join(
                "%d (%s til %s)" % (n, "mor" if n % 2 else "far", T.navn(aner[n // 2])) for n in tomme))

    print("\n" + "=" * 78, "\n2. FAMILIER — hvert anepar med hele børneflokken\n" + "=" * 78)
    for n in sorted(aner):
        far, mor, fam = T.foraeldre(aner[n])
        if not fam:
            continue
        v = T.felt(fam, "MARR", "DATE")
        print("\n%s  %s  ×  %s%s" % (fam, T.navn(far) if far else "?", T.navn(mor) if mor else "?",
                                     "   viet " + dato(v) + " i " + T.felt(fam, "MARR", "PLAC").split(",")[0]
                                     if v else ""))
        for b in T.peger(fam, "CHIL"):
            print("    %s %-6s %s %s" % ("→" if b == aner[n] else " ", b, T.navn(b), T.levetid(b)))

    print("\n" + "=" * 78, "\n3. MEDIER — kandidater til billedklip (sti under media/)\n" + "=" * 78)
    for n in sorted(aner):
        m = T.medier(aner[n])
        if m:
            print("\n%d %s %s" % (n, aner[n], T.navn(aner[n])))
            for fil, titel in m:
                print("    media/%s\n        %s" % (fil, titel))

    print("\n" + "=" * 78, "\n4. TAVLER — udkast; ret ordlyd og undertekster, ikke navne og aar\n" + "=" * 78)
    for b, etiket in ((4, "Faderens far"), (5, "Faderens mor"), (6, "Moderens far"), (7, "Moderens mor")):
        if b not in aner:
            continue
        print("\n**%s**\n\n```tavle" % etiket)
        med = [s for s in (2 * b, 2 * b + 1) if s in aner and (2 * s in aner or 2 * s + 1 in aner)]
        if med:
            print("  ||  ".join(par(T, aner.get(2 * s), aner.get(2 * s + 1),
                                    T.foraeldre(aner[s])[2]) for s in med))
        if 2 * b in aner or 2 * b + 1 in aner:
            print(par(T, aner.get(2 * b), aner.get(2 * b + 1), T.foraeldre(aner[b])[2],
                      gennem=aner[med[0]] if len(med) == 1 else None))
        print(tavlenavn(T, aner[b]))
        print("```")
    print("\n**Og de to sider mødes**\n\n```tavle")
    med = [s for s in (2, 3) if s in aner and (2 * s in aner or 2 * s + 1 in aner)]
    if med:
        print("  ||  ".join(par(T, aner.get(2 * s), aner.get(2 * s + 1), T.foraeldre(aner[s])[2])
                            for s in med))
    if 2 in aner or 3 in aner:
        print(par(T, aner.get(2), aner.get(3), T.foraeldre(proband)[2],
                  gennem=aner[med[0]] if len(med) == 1 else None))
    print(tavlenavn(T, proband))
    print("```")


def facit_arg():
    return sys.argv[sys.argv.index("--facit") + 1] if "--facit" in sys.argv else None


if __name__ == "__main__":
    main()
