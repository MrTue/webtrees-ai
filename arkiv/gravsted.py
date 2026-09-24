# -*- coding: utf-8 -*-
"""gravsted.py --by <sted> --navn <efternavn>      soeg paa alle kirkegaarde i et omraade
   gravsted.py --kirkegaarde <soegeord>            list kirkegaarde med id (tom = alle 1754)
   gravsted.py --kgd <id> --navn <navn>            soeg paa én kirkegaard
   gravsted.py --alle <efternavn>                  FEJ HELE LANDET, ca. 4 minutter
   gravsted.py --kgd <id> --grav "2 13  106"       hvem ligger ellers i den grav?

findgravsted.dk er Brandsofts kirkegaardssystem. Siden er en JavaScript-app, men
den hviler paa to enkle endepunkter, som kan kaldes direkte:

    POST /bsk_app/Bsk_wsfindgravsted_pck.SoegKirkegaard
    POST /bsk_app/bsk_wsoffentlig_pck.AfdoedeSoeg

Svaret er XML (ISO-8859-1) med AFDOED-blokke: fornavne, efternavn, foedsels- og
doedsdato, kirkegaard og gravstedsnummer. InKlientHttp maa gerne vaere et
tilfaeldigt GUID — serveren kontrollerer det ikke.

Registret daekker ca. 1.750 danske kirkegaarde i Folkekirkens faelles system.

BRUG DET TIL PERSONLIG SLAEGTSFORSKNING. Serveren er Folkekirkens, ikke din: hold lav
hastighed (pause mellem kaldene), respekter sidens vilkaar, og brug `--alle` og
`hel_kirkegaard()` sparsomt — en landsfejning er ca. 1.750 kald. Proev `--kgd` foerst.
"""
import urllib.request, urllib.parse, ssl, sys, re, html, uuid, time, json

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
BASE = "https://findgravsted.brandsoft.dk"
UA = {"User-Agent": "Mozilla/5.0",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "Accept": "application/json, text/plain, */*",
      "Origin": BASE, "Referer": BASE + "/"}
KLIENT = uuid.uuid4().hex.upper()   # 32 hex-tegn UDEN bindestreger — serveren svarer 500 paa uuid-formen


def kald(sti, par, forsoeg=3):
    b = urllib.parse.urlencode(par, encoding="utf-8").encode()
    for i in range(forsoeg):
        try:
            r = urllib.request.urlopen(urllib.request.Request(BASE + sti, data=b, headers=UA),
                                       timeout=90, context=CTX).read()
            t = r.decode("utf-8", "replace")
            if t.startswith('"'):                      # svaret er en JSON-indpakket streng
                t = t[1:-1].encode().decode("unicode_escape")
            return html.unescape(t)
        except Exception:                              # noqa: BLE001
            if i == forsoeg - 1:
                raise
            time.sleep(2 + 3 * i)


def blokke(xml, tag):
    ud = []
    for m in re.finditer(r"(?s)<%s>(.*?)</%s>" % (tag, tag), xml):
        d = {}
        for f in re.finditer(r"<([A-Z_0-9]+)>([^<]*)</\1>", m.group(1)):
            d[f.group(1)] = f.group(2).strip()
        if d:
            ud.append(d)
    return ud


# KIRKEGAARDSOPSLAGET.
# Bemaerk stavemaaden: parameteren hedder InKirkegaardId med lille d, ikke
# InKirkegaardID, og fritekstfeltet hedder InSoegeStr. Parametrene staar i
# sidens egen JavaScript-bundle, hvor kaldet foretages.
#
#   POST /bsk_app/Bsk_wsfindgravsted_pck.SoegKirkegaard
#        InKlientHttp, InSoegeStr, InKirkegaardId, InAfdelingId, InLat, InLng
#
# Svaret er JSON (ikke XML som AfdoedeSoeg). En TOM InSoegeStr giver ALLE
# 1754 kirkegaarde i ét kald — det er den, `--alle` bruger.
#
# AFDOEDESOEG:
#   * en TOM InSoegekriterie giver hele kirkegaarden, ikke nul
#   * InIndex sider igennem, InAntalHits op til mindst 500 ad gangen
# Tilsammen kan en hel kirkegaard tommes og filtreres paa GRAVSTED_NR, hvilket
# er den eneste maade at se, HVEM DER ELLERS LIGGER I SAMME GRAV.
# Dine egne ofte brugte kirkegaarde: {"kort navn": (kirkegaards-id, "fuldt navn")}.
# Id'et findes med `--kirkegaarde <soegeord>`. Listen bruges ikke af scriptet selv.
KENDTE = {}


def kirkegaarde(soeg=""):
    """Slaar op i findgravsteds egen liste. Tom soegestreng giver alle 1754."""
    x = kald("/bsk_app/Bsk_wsfindgravsted_pck.SoegKirkegaard",
             {"InKlientHttp": KLIENT, "InSoegeStr": soeg,
              "InKirkegaardId": "", "InAfdelingId": "", "InLat": "", "InLng": ""})
    ud = []
    for k in json.loads(x).get("kirkegaarde", []):
        ud.append({"KIRKEGAARD_ID": str(int(k["kgdId"])),
                   "KIRKEGAARD_NAVN": k.get("navn", ""),
                   "ADRESSE": k.get("adresse", "")})
    return ud


def hel_kirkegaard(kgd, side=500, loft=40000):
    """Alle begravede paa én kirkegaard. Brug den til at se, hvem der ligger
    i samme gravsted — AfdoedeSoeg kan ikke soege paa gravstedsnummer."""
    ud = []
    i = 0
    while True:
        d = afdoede(kgd, "", side, i)
        ud.extend(d)
        if len(d) < side or i >= loft:
            return ud
        i += side


def gravfaeller(kgd, gravsted_nr):
    nr = gravsted_nr.split()
    return [a for a in hel_kirkegaard(kgd)
            if a.get("GRAVSTED_NR", "").split() == nr]


def landet_over(navn, kgde=None, log=None):
    """Fejer HELE landet for ét efternavn. Ca. 4 minutter for 1754 kirkegaarde."""
    kgde = kgde or kirkegaarde("")
    ud = []
    for n, k in enumerate(kgde, 1):
        try:
            for a in afdoede(k["KIRKEGAARD_ID"], navn, 50):
                a.setdefault("KIRKEGAARD_NAVN", k["KIRKEGAARD_NAVN"])
                ud.append(a)
        except Exception:                                   # noqa: BLE001
            continue
        if log and n % 100 == 0:
            log("... %d/%d, %d traef" % (n, len(kgde), len(ud)))
    return ud


def afdoede(kgd, navn, antal=100, index=0):
    x = kald("/bsk_app/bsk_wsoffentlig_pck.AfdoedeSoeg",
             {"InKlientHttp": KLIENT, "InDBSID": "BSK", "InKirkegaardID": kgd,
              "InSoegekriterie": navn, "InIndex": index, "InAntalHits": antal,
              "InFodselsAar": 2026, "InFodselLigMed": "N", "InFodselMindreEnd": "N",
              "InFodselStorreEnd": "N", "InDodsAar": 2026, "InDodLigMed": "N",
              "InDodMindreEnd": "N", "InDodStorreEnd": "N"})
    return blokke(x, "AFDOED")


def vis(a):
    return "%-26s %-22s f. %-11s d. %-11s  %-26s %s" % (
        a.get("FORNAVNE", "")[:26], a.get("AKT_EFTERNAVN", "")[:22],
        a.get("DATO_FODT", "") or "—", a.get("DATO_DOD", "") or "—",
        a.get("KIRKEGAARD_NAVN", "")[:26], a.get("GRAVSTED_NR", ""))


if __name__ == "__main__":
    a = dict(zip(sys.argv[1::2], sys.argv[2::2]))
    if "--kirkegaarde" in a:
        for k in kirkegaarde(a["--kirkegaarde"]):
            print("%-10s %-34s %s" % (k.get("KIRKEGAARD_ID"), k.get("KIRKEGAARD_NAVN", "")[:34],
                                      k.get("ADRESSE", "") or k.get("POSTNR_BY", "")))
    elif "--alle" in a:
        kg = kirkegaarde("")
        print("fejer %d kirkegårde for «%s» …" % (len(kg), a["--alle"]))
        r = landet_over(a["--alle"], kg, log=print)
        for x in sorted(r, key=lambda y: (y.get("KIRKEGAARD_NAVN", ""), y.get("FORNAVNE", ""))):
            print("  " + vis(x))
        print("i alt %d begravede ved navn «%s» i hele landet" % (len(r), a["--alle"]))
    elif "--grav" in a:
        r = gravfaeller(a["--kgd"], a["--grav"])
        print("gravsted «%s»: %d personer" % (a["--grav"], len(r)))
        for x in r:
            print("  " + vis(x))
    elif "--kgd" in a:
        for x in afdoede(a["--kgd"], a["--navn"]):
            print("  " + vis(x))
    else:
        kg = kirkegaarde(a["--by"])
        print("kirkegårde i «%s»: %d" % (a["--by"], len(kg)))
        i_alt = 0
        for k in kg:
            try:
                r = afdoede(k["KIRKEGAARD_ID"], a["--navn"])
            except Exception as e:                     # noqa: BLE001
                print("  %-30s FEJL %s" % (k.get("KIRKEGAARD_NAVN", "")[:30], str(e)[:40]))
                continue
            for x in r:
                i_alt += 1
                print("  " + vis(x))
        print("i alt %d begravede ved navn «%s»" % (i_alt, a["--navn"]))


