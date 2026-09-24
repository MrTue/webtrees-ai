# -*- coding: utf-8 -*-
"""ddd5.py <navn> <amt> [aargang] [--fodested X] [--alder N] [--sogn X]

Dansk Demografisk Database, folketaellingerne. Skrevet til soegesiden, som den
ser ud efter omlaegningen til AJAX; skrabere af den gamle formularside virker ikke.

HVAD DER AENDREDE SIG (efterproevet september 2026):

  * `soeg_person.asp` er nu en ren formularside. Den POSTER IKKE til sig selv
    laengere; soegeknappen er `<input type="button" id="btnSearch">`, og siden
    indlaeser `soegpersonudvidetajax.js`.
  * Det rigtige endepunkt er
        POST https://www.ddd.dda.dk/soegpersonudvidetajax.asp?action=search
    med formularen `#formkipfolder` serialiseret som krop.
  * Formularen har faaet et nyt felt, **fødested**, og felterne `county`,
    `kilde`, `sorter` og `sorter2` skal have RIGTIGE standardvaerdier
    ("alle", "alle", "a.navn", "b.aarfra"), ikke tomme strenge.
  * **AMT ER OBLIGATORISK.** JavaScriptet naegter selv at soege uden:
        if ($('#ddlCounty').val() == "alle") alert("Venligst vælg Amt");
    Den avancerede soegning kan derfor IKKE bruges landsdaekkende. Skal man
    soege i hele landet, maa man loebe amterne igennem eller bruge den simple
    soegning paa `soeg_person_enkel.asp`.
  * **Svaret er ikke en tabel.** Det er en raekke afsnit med etiketterne
    "Navn:", "Alder:", "Civilstand:", "Erhverv:", "Fødested:", "Fam.nr:",
    "Matr.nr:", "Stednavn:", "Sogn:", "Kilde:", "KIPnr:", "Lbnr:".
    En gammel `<tr>`-laeser finder nul raekker og ser ud, som om soegningen
    fejlede.
  * **Serveren viser hoejst 250 poster** og skriver selv "Kun 250 poster vises",
    naar der er flere. Snaevr soegningen, naar den linje dukker op.

Amtsnavne skrives som i formularen: Bornholm, Frederiksborg, Haderslev,
Hjoerring (Hjørring), Holbaek (Holbæk), Koebenhavn (København), Maribo, Odense,
Praestoe (Præstø), Randers, Ribe, Ringkoebing, Roskilde, Skanderborg, Soroe,
Svendborg, Thisted, Tønder, Vejle, Viborg, Aalborg, Aarhus m.fl.
"""
import html as H
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

BASE = "https://www.ddd.dda.dk/"
URL = BASE + "soegpersonudvidetajax.asp?action=search"
UA = {"User-Agent": "Mozilla/5.0",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "X-Requested-With": "XMLHttpRequest",
      "Referer": BASE + "soeg_person.asp"}

FELTER = ["Navn", "Alder", "Civilstand", "Erhverv", "Fødested", "Fam.nr",
          "Matr.nr", "Stednavn", "Sogn", "Kilde", "KIPnr", "Lbnr"]
DELER = re.compile(r"(%s):" % "|".join(re.escape(f) for f in FELTER))


def soeg(navn, amt, aar="alle", fodested="", alder="", sogn="", operator="3"):
    f = [("kipnr", ""), ("stednavn", ""), ("county", amt), ("herred", ""),
         ("parish", sogn), ("navn", navn), ("navn2", ""), ("operator", operator),
         ("navnelogik", "OR"), ("erhverv", ""), ("fødested", fodested),
         ("alder_valg", ""), ("alder", alder), ("faarb", ""), ("interval", "2"),
         ("sex", ""), ("kilde", aar), ("sorter", "a.navn"), ("sorter2", "b.aarfra")]
    # SKAL vaere utf-8. Serveren svarer 500, saa snart et FELT indeholder
    # aeoeaa og data er sendt som windows-1252 -- headeren siger charset=UTF-8,
    # og ASP-siden tror paa headeren. Det ramte hvert amt med saertegn:
    # Hjoerring, Praestoe, Holbaek, Koebenhavn, Soroe, Toender, Aalborg,
    # Ringkoebing og Aarhus var i praksis usoegbare. SVARET afkodes stadig som
    # windows-1252 -- det er en anden sag og uaendret.
    data = urllib.parse.urlencode(f, encoding="utf-8").encode()
    return urllib.request.urlopen(
        urllib.request.Request(URL, data=data, headers=UA), timeout=240
    ).read().decode("windows-1252", "replace")


def flad(t):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"(?is)<[^>]+>", " ", t))).strip()


def poster(t):
    """Deler det flade svar op i poster paa etiketterne."""
    s = flad(t)
    dele = DELER.split(s)
    ud, nu = [], {}
    for i in range(1, len(dele) - 1, 2):
        navn_felt, vaerdi = dele[i], dele[i + 1].strip()
        if navn_felt == "Navn" and nu:
            ud.append(nu)
            nu = {}
        nu[navn_felt] = vaerdi
    if nu:
        ud.append(nu)
    return ud


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__.split("\n\n")[0])
    navn, amt = sys.argv[1], sys.argv[2]
    rest = sys.argv[3:]
    aar = rest[0] if rest and not rest[0].startswith("--") else "alle"

    def flag(n, d=""):
        return rest[rest.index(n) + 1] if n in rest else d

    t = soeg(navn, amt, aar, flag("--fodested"), flag("--alder"), flag("--sogn"))
    s = flad(t)
    m = re.search(r"([\d.]+)\s+poster fundet", s)
    if m:
        print("%s poster fundet i %s" % (m.group(1), amt))
    if "Kun 250 poster vises" in s:
        print("** KUN 250 VISES — snaevr soegningen **")

    pk = poster(t)
    print("%d poster laest\n" % len(pk))
    for p in pk:
        print("%-34s %-4s %-26s %-22s %s" % (
            p.get("Navn", "")[:34], p.get("Alder", "")[:4],
            p.get("Sogn", "")[:26], p.get("Fødested", "")[:22],
            p.get("Kilde", "")[:12]))


if __name__ == "__main__":
    main()
