# -*- coding: utf-8 -*-
"""kbh.py "<solr-query>" [--rows 20] [--start 0] [--samling 1,17] [--sort ...]
        [--felter a,b,c] [--raa]

Koebenhavns Stadsarkivs indtastede kilder, direkte mod deres aabne Solr:
    https://solr.kbharkiv.dk/solr/apacs_core/select

Samlinger (collection_id) — HELE listen, facetteret september 2026,
i alt 2.793.824 poster:
    17 = Politiets registerblade 1890-1923   1.965.257  (hovedpersoner OG bipersoner)
     1 = Begravelsesprotokoller                619.509
    10 = BORGERLIGE VIELSER                    143.499
   150 = Folkeregisterkort                      51.568  (kun et UDPLUK af byen)
    19 = Politiets efterretninger                9.033
    18 = Erindringer                             3.322
     5 = Begravelsesprotokoller (lille rest)     1.636
(Graensefladen paa kbharkiv.dk soeger som standard i 1,17,18,19 — samling 150
 OG 10 kommer KUN med, hvis man selv skriver collection_id i soegningen.)

BORGERLIGE VIELSER (10) er let at overse. Egne felter: `marriage_date`, `role` ("Brud"/"Brudgom"),
`civilstatus`, `birthplace_free`, `residence_free` og TRE trosfelter —
`current_denomination`, `former_denomination`, `children_denomination`.
Det sidste er guld ved blandede aegteskaber: parret maatte skriftligt erklaere,
i hvilken tro boernene skulle opdrages.
RAEKKEVIDDEN ER SKAEV. Bindet 1851-1875 er kun taget med i udpluk: hele vinduet
1851-1870 rummer 314 poster, mens 1900-tallet er taet. Et nul foer 1875 beviser
derfor INTET. Og husk, at borgerlig vielse foerst blev mulig i 1851 og laenge
mest blev brugt af dem, der IKKE kunne vies i folkekirken.

BEGRAVELSESPROTOKOLLERNE (1) er bedre, end de ser ud. De raekker fra 1805 til
ind i 1900-tallet og har `dateOfDeath`, `ageYears`, `deathcauses` (latin),
`deathplace`, `cemetary`, `addresses`, `civilstatus` og — for gifte kvinder og
boern — MANDENS eller FADERENS erhverv i `positions`. Feltet `comments` rummer
tit et direkte AO-link til doedsattesten, og af og til en krydshenvisning af
formen «Se ogsaa nummer 1202», som peger paa et andet loebenummer i samme bind.

FOLKEREGISTERKORTENE (150) er de eneste, der raekker efter 1923. De har felterne
`role` ("Mand", "Kvinde", "Barn under 15 aar") og en BOERN-liste, der opregner
husstandens boern med navn — altsaa en husstand paa ét kort. Udpluk­ket er lille,
saa et nul beviser ingenting; men et traeffer giver hele familien paa én gang.

Nyttige felter:  freetext_store  firstnames  lastname  fullname  birthname
                 yearOfBirth  dateOfBirth  birthplace  streets  addresses
                 positions  collection_id  personType  card_id

REGISTERBLADENE ER GULD: hvert blad har ÆGTEFÆLLE og BOERN 10-14 aar med
fulde navne og foedselsdatoer. De ligger i feltet jsonObj og udskrives
her som "ÆGTEFÆLLE" og "BØRN".

Eksempler:
    python kbh.py "freetext_store:(*Eksempelsen* AND *kurvemager*)"
    python kbh.py "lastname:Eksempelsen AND yearOfBirth:[1900 TO 1920]" --rows 50
    python kbh.py "card_id:1234567" --samling 17
"""
import json, sys, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
BASE = "https://solr.kbharkiv.dk/solr/apacs_core/select"
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://kbharkiv.dk/"}
SKIP = {"jsonObj", "event_timestamp", "task_id", "unit_id", "post_id",
        "entry_id", "user_id", "user_name", "page_id", "back_page_id",
        "last_update_user_id", "last_update_user_name", "_version_"}

if len(sys.argv) < 2:
    print(__doc__)
    raise SystemExit(1)
q = sys.argv[1]
a = dict(zip(sys.argv[2::2], sys.argv[3::2]))
raa = "--raa" in sys.argv

p = {"wt": "json", "q": q, "start": a.get("--start", "0"),
     "rows": a.get("--rows", "20"), "sort": a.get("--sort", "lastname asc")}
if "--samling" in a:
    p["fq"] = "collection_id:(%s)" % a["--samling"].replace(",", " ")

d = json.loads(urllib.request.urlopen(
    urllib.request.Request(BASE + "?" + urllib.parse.urlencode(p), headers=UA),
    timeout=90).read().decode("utf-8"))

r = d["response"]
print("TRÆF: %d (viser fra %d)" % (r["numFound"], r["start"]))
felter = a["--felter"].split(",") if "--felter" in a else None


def dato(s):
    return (s or "")[:10]


for i, doc in enumerate(r["docs"], r["start"] + 1):
    print("--- %d ---" % i)
    for k, v in sorted(doc.items()):
        if felter and k not in felter:
            continue
        if not felter and (k.startswith("_") or k in SKIP):
            continue
        if isinstance(v, list):
            v = " | ".join(str(x) for x in v)
        print("   %-20s %s" % (k, v))
    if felter:
        continue
    o = json.loads(doc.get("jsonObj", "{}"))
    if raa:
        print(json.dumps(o, ensure_ascii=False, indent=2))
        continue
    for s in o.get("spouses") or []:
        print("   ÆGTEFÆLLE            %s %s  f. %s  %s" % (
            s.get("firstnames", ""), s.get("lastname", ""),
            dato(s.get("dateOfBirth")), s.get("birthplace") or ""))
    for c in o.get("children") or []:
        print("   BARN                 %s %s  f. %s  (alder %s)" % (
            c.get("firstnames", ""), c.get("lastname", "") or "",
            dato(c.get("dateOfBirth")), c.get("age", "")))
    for ad in o.get("addresses") or []:
        if isinstance(ad, dict) and ad.get("address_date"):
            print("   ADRESSE %s   %s" % (dato(ad["address_date"]),
                                          ad.get("full_address", "")))
