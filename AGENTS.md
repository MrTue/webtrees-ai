# AGENTS.md

Regler for den AI-assistent, der arbejder i dette repo — Claude Code, Codex, Gemini CLI eller
en anden agent, der kan køre kommandoer, læse filer og **se billeder**. `CLAUDE.md` og
`GEMINI.md` henviser hertil, så reglerne kun findes ét sted.

## Hvad det her er

Ikke et almindeligt softwareprojekt, men et **arbejdsrum for dansk slægtsforskning**: en
webtrees-installation i Docker (fx på en Synology-NAS), plus de scripts, der henter
arkivalier ned og skriver fundene ind i træet. Der er ingen build, ingen tests og ingen
linter. Python-scripts køres direkte med `python` (Python 3; udviklet på 3.14).
Tredjepartsafhængighederne — `Pillow` og `reportlab` — installeres med
`pip install -r requirements.txt`.

Mappen **er et git-repo**, men repoet rummer kun **metoden og værktøjerne**. Alt, der
handler om brugerens egen slægt, holdes ude af git via `.gitignore` og skal oprettes lokalt:
`facit.json`, `poster/*.result.json`, `poster/log.jsonl`, egne jobfiler i `poster/`,
`SLAEGTSHISTORIEN*.md`, `dokumenter/`, `billeder/`, `webtrees-steder.csv`, journalen
`arkiv/README-DA.md` og `arkiv/bind.json`. **Læg aldrig personlige data i en fil, git følger** —
ingen navne på nulevende, ingen private stier, værtsnavne eller e-mails.

Alt er skrevet på dansk. Skriv også dansk — i dokumentation, kilder, noter og opsummeringer.

## Kom i gang

Repoet leverer skabeloner under navne, git følger. Kopiér dem selv til de rigtige navne,
som `.gitignore` holder ude:

| Skabelon i repoet | Kopiér til |
|---|---|
| `arkiv/README-DA.skabelon.md` | `arkiv/README-DA.md` — journalen |
| `GOER-MANUELT.skabelon.md` | `GOER-MANUELT.md` |
| `SLET-MANUELT.skabelon.md` | `SLET-MANUELT.md` |
| `webtrees-steder.eksempel.csv` | `webtrees-steder.csv` |
| `login.eksempel.json` | `%USERPROFILE%\.webtrees\login.json` — **udfyldes af brugeren selv** |

To miljøvariabler styrer, hvor tingene ligger:

- **`SLAEGT_ARBEJDSMAPPE`** — arbejdsmappen til `facit.json`, prøvebilleder, kontaktark og
  prøve-PDF'er. Er den ikke sat, bruger scriptene temp-mappen (enkelte den aktuelle mappe).
- **`WEBTREES_MEDIA`** — webtrees' mediemappe, standard `//NAS/docker/webtrees/data/media`.
  Bruges af `medietjek.py`, `klip.py`, `mdpdf.py` og `gemmedie.py`.

Desuden kan `WEBTREES_LOGIN` pege på en anden loginfil, og `PYTHON` på en anden fortolker
i `byg-pdf.ps1`.

## De faste kommandoer

```
python webtrees_klient.py --check                         # login + rettigheder, intet andet
python webtrees_klient.py --dry-run poster\job.json       # vis præcis hvad der ville blive sendt
python webtrees_klient.py poster\job.json                 # kør
python webtrees_klient.py poster\job.json --set KILDE=S12 # genkør uden allerede skabte ops
python arkiv\<script>.py …                                # arkivværktøjerne, se arkiv\README-DA.md
python arkiv\facit.py && python arkiv\linktjek.py && python arkiv\markutjek.py && python arkiv\medietjek.py && python arkiv\stedtjek.py
python arkiv\mdpdf.py SLAEGTSHISTORIEN.md ud.pdf          # markdown → sat PDF
.\byg-pdf.ps1                                             # hver SLAEGTSHISTORIEN*.md som bog (mdpdf --bog)
python arkiv\klip.py kirkeboger/<fil>.jpg --gitter        # find koordinaterne til et billedklip
python arkiv\bogdata.py X1 5                              # anetavle, børneflokke, medier og tavle-udkast til en fortælling
python arkiv\tekstkontrol.py <ny>.md <backup>.md          # er alt redaktionelt ude — og faldt en dato ud under omskrivningen?
```

**Kør altid `--dry-run` først og vis brugeren resultatet**, før noget sendes til træet.

## Sådan hænger delene sammen

| Del | Rolle |
|---|---|
| `docker-compose.yml` | webtrees + MariaDB. Filen redigeres her, men deployes på NAS'en. Se `INSTALL-DA.md`. |
| `webtrees_klient.py` | **Skrivevejen ind i træet.** webtrees har ingen API, så klienten logger ind som en redaktørbruger (fx `ai`) og poster de samme formularer som browseren. |
| `poster/*.json` | Ét job = én afsluttet registrering. Kørslen skriver `*.result.json` (id → xref) og én linje per op i `poster/log.jsonl`. Jobformatet står i `poster/README-DA.md`; `poster/eksempel.json` viser et job. |
| `arkiv/*.py` | **Læsevejen ud af arkiverne.** Små scripts mod Arkivalieronline, Mediestream, arkiv.dk, Sall Data, Erik Brejl, Københavns Stadsarkiv m.fl. |
| `arkiv/README-DA.md` | **Arkivjournalen** (lokal) — hvad der er søgt i, bind for bind, og især hvad der er **udelukket**. |
| `arkiv/bind.json` | Maskinlæsbar udgave (lokal): `bsid`, `grundtal`, opslagstal og opbygning per kirkebogsbind. `billed_id = grundtal + opslagsnummer`. |
| `arkiv/KILDER-ONLINE.md` | Hvilke danske kilder der kan hentes maskinelt, og hvilke der ikke kan. |
| `dokumenter/` | Råmateriale (lokalt), der **ikke** hænger på nogen i træet (hele avissider m.m.). |
| `SLAEGTSHISTORIEN*.md` | Fortællingen (lokal), med dokumenteret tekst og formodninger holdt visuelt adskilt. |
| `METODE.md` | **Den egentlige metodebeskrivelse** — søgning, kildekritik og webtrees-fælder. Læs den, før du gør noget fagligt. |
| `.claude/agents/slaegtsforsker.md` | Tynd skal, der gør `METODE.md` til en underagent i Claude Code. |
| `.claude/skills/` | `dansk-slaegtsforskning` (metoden uden projektets stier) og `slaegtsbog` (opskriften på bogen). Skrevet i det åbne `SKILL.md`-format; bruger du et andet værktøj end Claude Code, så læs dem som almindelige dokumenter, når opgaven passer til deres beskrivelse. |

## Regler, der ikke kan gættes ud af koden

**Læs journalen først — hver gang.** `arkiv/README-DA.md` og `arkiv/bind.json` rummer al
tidligere navigation. Et negativt resultat kostede lige så meget arbejde som et positivt.
**Før journalen ajour bagefter, også når du intet fandt.**

**Kodeord.** Klienten læser `%USERPROFILE%\.webtrees\login.json`. Den fil åbner du aldrig, og
du indtaster aldrig et kodeord. Hold loginfilen uden for repoet og uden for enhver mappe,
der backes op til skyen; klienten nægter med vilje at læse den fra projektmappen.

**Klienten kan ikke slette — med vilje.** Skal en post væk, gør brugeren det i
brugerfladen. Familier slettes til sidst. **Arbejdslisten er `GOER-MANUELT.md`**, som rummer
alt det manuelle i rækkefølge; **`SLET-MANUELT.md` er det detaljerede grundlag under
sletningerne.** Står en opgave i begge, er det en fejl — de to filer kan komme til at
modsige hinanden.

**En dublet slås sammen. Den slettes ikke.** webtrees' «Slå sammen» stiller felterne op ved
siden af hinanden, før noget forsvinder; sletningen gør ikke, og den kan ikke fortrydes. Det
koster én ekstra dialogboks. **Skriv derfor aldrig «slet dubletten» i en opgaveliste** — og
især ikke «der går intet tabt ved at slette», med mindre du har stillet de to poster op felt
for felt. Den påstand er før holdt op med at holde: det substantielle var reddet over på den
gode post, men to håndskriftlæsninger stod kun på dubletten. Sletning af *noter og
kendsgerninger* er en anden sag — dér er der ikke noget at sammenligne.

**Klienten kan derimod godt sammenkæde to poster, der allerede findes — men ingen af
`add-*`-operationerne gør det.** De *opretter* alle sammen en ny person. Den rene kædning
har sin egen op:

```
{"id": "K1", "op": "link-child-to-family", "child": "X100", "family": "X200", "pedi": ""}
```

Tom `pedi` er brugerfladens egen standard og betyder fødsel. Der findes **også** et
enkeltstående værktøj, `arkiv\haeftbarn.py <barn> <familie> [PEDI] [--gør]`, som gør
nøjagtig det samme uden jobfil — brug det til ét enkelt klik, og op'en når kædningen hører
med til en større registrering, så den kommer i `poster/log.jsonl`. **Læs afsnittet om
jobformatet i `poster/README-DA.md` til ende, før du udvider klienten** — det, du mangler,
findes måske allerede.

**Kædningen er reversibel** i brugerfladen («fjern fra familien») — til forskel fra en
dublet, som kun brugeren kan slette. **Opret derfor aldrig en dublet i stedet for en kædning.**

**Og du kan selv fjerne en kædning.** En `1 CHIL @X###@` på en familie og en `1 FAMC @X###@`
på en person er **kendsgerninger som alle andre**, og `edit-raw` skelner ikke mellem en
person- og en familiepost. `arkiv\fjernnoter2.py` kan derfor flytte et barn fra den ene
familie til den anden, når rækkefølgen er rigtig:

```
python arkiv\haeftbarn.py <barn> <ny-familie> --goer    # 1) kæd til den rigtige familie FØRST
python arkiv\fjernnoter2.py opgaver.json --goer         # 2) fjern så {"<gammel-familie>": ["1 CHIL @<barn>@"],
                                                        #              "<barn>": ["1 FAMC @<gammel-familie>@"]}
```

**Kæd altid til den nye familie først**, så barnet aldrig står uden forældre undervejs; at stå
i to familier et øjeblik koster intet. Typisk tilfælde: kilderne flytter et barn fra faderens
andet ægteskab til hans første. **Husk at rette de noter, der nævner den gamle familie** —
`notetjek.py` fanger dem ikke, for de er ikke løfter om fremtiden.

`link-spouse-to-individual` og `link-family-to-individual` findes som ruter i webtrees, men
er **ikke** pakket ind hverken i klienten eller i et værktøj. Dem skriver du i
**`GOER-MANUELT.md`** — modstykket til `SLET-MANUELT.md` — med xref på både posten og
familien, og med kildecitatet, så brugeren kan se *hvorfor*.

**Forudsiger et job et xref, så tæl familierne med.** Kilder, medieobjekter, personer **og
familier** trækker alle fra samme X-nummerrække. En `add-parent` lægger derfor beslag på
**to** numre — personen og den nye familie — mens `add-spouse-to-family` kun tager ét.

### Syv kontroller, ikke én

**`linktjek.py`** følger `@X###@` — de rigtige GEDCOM-pegepinde.
**`markutjek.py`** tager `[[X###]]`, som er ren visning og ellers ikke kontrolleres nogen
steder. **`medietjek.py`** slår hvert medieobjekts `1 FILE` op i mediemappen, for **ingen af
de andre åbner en fil**, og en forkert sti giver et brudt billede, man først ser på netop
den post. **`stedtjek.py`** krydser hvert `2 PLAC` mod `webtrees-steder.csv`, for **ingen af
de tre andre ser på steder** — et sted uden række får ingen prik på kortet, og det opdager
man aldrig. Kør alle fire efter `facit.py`.

`stedtjek.py` melder **tre** slags: **danske steder med tre led**, hvor herredet ser ud til at
være faldet ud · **steder uden række i filen** · og **mellemniveauer uden række**.
Udenlandske og bevidst grove steder — «Bornholm, Danmark», «Omaha, Nebraska, USA» — listes
til orientering og tæller ikke som fejl.

**Den tredje er den, man ellers aldrig finder.** webtrees bygger en knude for **hvert led** i
en stednavnesti: «Sogn, Herred, Amt, Danmark» er **fire** knuder, ikke én, og en knude uden
række får ingen koordinat — **en gul trekant i stedlisten.** Alle sogne kan være på plads, så
`stedtjek` melder nul, og der står stadig trekanter, fordi **et helt amt** med poster under
sig mangler sin egen række. Kontrollen ser derfor på alle led. **Niveau 1 og 2 er afrundede
midtpunkter** — reglen om sognekirkens koordinat gælder niveau 3.

**Den femte er ikke rutine: `dubletjek.py`.** Den finder personer, der bærer samme navn, og
den er en **revision** — kør den, når der er oprettet mange personer. Den støjer med vilje:
slægter kalder op efter døde børn, så de fleste træf er ægte navnefæller. **Derfor viser den
fødselsår og familie ved siden af, og den markerer de par, der har SAMME FØDSELSDATO** — dem
er næsten altid dubletter.

```
python arkiv\dubletjek.py            # hele træet
python arkiv\dubletjek.py --fra 500  # kun poster fra og med X500
```

**Den sjette, af samme slags: `gentagtjek.py`.** Hvor `dubletjek` finder to *poster* med
samme navn, finder den to *livshændelser* på samme post — en person fødes, døbes,
konfirmeres, dør og begraves én gang hver. Den sorterer selv træffene i tre bunker og siger,
hvad der skal gøres ved hver: **ordret ens** (altid en fejl, `arkiv\fjerndublet.py` fjerner
den uden tab) · **den ene indeholdt i den anden** (en nøgen `1 BIRT` ved siden af en med sted
og note — brug `fjernnoter2.py`) · og **forskellige** (to kilder, der siger hver sit, fx en
trykt slægtsbog og en kirkebog, der er uenige om dødsdagen — **de skal blive stående**).
Kontrollen kan ikke selv se forskel på en fejl og en uenighed, og det skal den heller ikke.

**Den syvende er den eneste, der læser selve teksten: `notetjek.py`.** De seks andre ser på
henvisninger, filer, steder og kendsgerningstyper — **ingen af dem åbner en note og læser,
hvad der står.** En note skriver, hvad der var kendt *den dag*, og når sporet senere åbnes,
bliver sætningen «hendes død er ikke undersøgt» stående og lyver stille videre. Kontrollen
leder efter de sætninger, der lover noget om fremtiden — «ikke fundet», «kendes ikke», «bør
søges» — og stiller dem op mod, hvad posten rummer i dag:

```
python arkiv\notetjek.py              # hele træet
python arkiv\notetjek.py --xref X300  # én post
python arkiv\notetjek.py --ord "ikke læst"
```

**MODSAGT** er arbejdslisten (noten siger mangler, posten har det nu) · **NAVNE** er «X er ikke
oprettet», hvor navnet nu findes · **AABEN** er ægte åbne spor, som skal blive stående.
**Den kan ikke se, HVEM en sætning handler om** — «hendes død er ikke søgt» kan gælde posten
selv eller moderen, der er nævnt to linjer før; dér skriver den **«SANDSYNLIGVIS EN ANDEN»**.
**Åbn noten og læs den, før du retter.**

> **Et skøn er ikke et fund.** Kontrollen kræver en **præcis dato** på en hændelse, før den
> regner den som svar på noten: `1 BIRT / 2 DATE ABT 1771` er regnet ud af en alder ved døden,
> og `1 MARR Y` betyder «gift, detaljer ukendte». **En note, der siger «fødslen er ikke
> fundet», er stadig sand ved siden af en `ABT`-fødsel** — det er jo netop derfor, den står
> som `ABT`. Og **et løfte inde i et `«…»`-citat er kildens ord, ikke vores**: «Sidste fælles
> bopæl kendes ikke» i en gammel dødsanmeldelse skal aldrig «rettes».

### Jobfilernes fælder

**`create-source` opløser ikke `@ID@`-pladsholdere.** `run_op` sender den rå op videre til
`create_source` uden at køre den gennem `resolve`, så et job-id i en kildetekst bliver skrevet
råt ind som en brudt henvisning — og **`linktjek.py` fanger den ikke**, fordi den kun følger
mønstret `@X###@`. Skriv tekstlige henvisninger i kildetekster («se kilden …»), aldrig
job-id'er. Litterale `@X###@` er derimod i orden.

**`target` i `add-fact` og `edit-fact` skal være et *nøgent* xref — `X400`, ikke `@X400@`.**
`resolve()` lader en litteral `@X###@` stå urørt, så krøllealferne havner råt i URL'en, og
webtrees svarer **400 «Parameteren xref mangler»**. Det rammer især, når et target er
maskinskrevet ud fra et tidligere jobs resultatfil. `@X###@` hører kun hjemme *inde i*
GEDCOM-linjerne (`2 SOUR @X410@`).

**Job-id'er (`@KILDE@`, `@B1@`) gælder kun inden for ét job.** Skal et nyt job pege på
noget, et tidligere job skabte, så slå tallet op i `poster/<job>.result.json` og skriv det
rigtige xref. Der er ingen fejlmeddelelse, hvis man glemmer det i en `[[…]]`-markering —
kun `markutjek.py` opdager den.

**Slå op, om personen allerede findes, før du skriver et `add-child`.** Et `add-*` opretter
altid en ny post; den kan ikke fortryde sig selv, og en dublet kan kun fjernes i
brugerfladen. Søg i `facit.json` på navnet — også på fornavnet alene — og hører personen
allerede til træet, så kæd den i stedet (eller skriv kædningen i `GOER-MANUELT.md`).

**`/admin/*` svarer 403 for redaktørbrugeren.** Import af geografiske data og oprydning i
stednavne er altid brugerens klik. Kontrollér i stedet resultatet via
`/tree/<træ>/place-list/…`, som indlejrer koordinaterne som GeoJSON.

**`add-parent` opretter altid en ny familie.** Anden forælder tilføjes med
`add-spouse-to-family` på `@FØRSTE.FAMS@`. Og brug **aldrig** `.FAMS` om en person, der
endnu kun er barn i en familie — opslaget falder tilbage på `FAMC`, og barnebarnet ender som
søskende. Det er sket, og det kunne kun rettes i brugerfladen.

**`add-child`, `add-spouse` og `add-parent` kan tabe `1 CHR`.** `BIRT`, `OCCU`, `RESI` og `NOTE`
kommer altid med i den nye post, men **dåben er både faldet ud af formularen og kommet med**
i to kørsler med få dages mellemrum. Hvad der skiller de to tilfælde, er ikke afklaret.
**Slå derfor op i resultatet, om dåben kom med**, og tilføj den kun med en `add-fact`, hvis
den mangler — ellers står den to gange. Det er et eksempel på reglen nedenfor: en sætning om,
hvad værktøjet *ikke* kan, er en påstand med en dato på.

**`edit-fact` erstatter hele kendsgerningen**, ikke kun de linjer du nævner; kildecitater
skal skrives med. `match` skal ramme præcis én. Se posten med `arkiv\vis.py <xref>` først.

**Og `edit-fact` kan rette en kildes egen tekst.** `find_fact_id` finder `1 TEXT` på en
kildepost som enhver anden kendsgerning, så `{"op":"edit-fact","target":"X500","match":"1 TEXT", …}`
virker — **klienten behøver ingen `edit-source`.** Teksten skal deles i rigtige GEDCOM-linjer
(`1 TEXT` + `2 CONT`); ellers havner strengen «2 CONT» råt i kilden.

**`create-media` uploader ikke.** Filen lægges først i mediemappen (`WEBTREES_MEDIA`,
standard `//NAS/docker/webtrees/data/media`) over SMB, og stien angives relativt derfra.
Filnavne: årstal først, små bogstaver, ingen mellemrum, ingen æøå — navnet indgår i en URL
og kan ikke ændres bagefter. Hæft scanningen på **kilden**, ikke på personen, så den følger
med hver gang kilden citeres.

**Ingen fil må ligge både i `dokumenter/` og i mediemappen**, og aldrig under to navne.

### Steder

**Nye `2 PLAC` skal skrives ind i `webtrees-steder.csv` med det samme**
(`3;Danmark;<Amt>;<Herred>;<Sogn>;E<længde>;N<bredde>;14;` — semikolon, UTF-8 uden BOM,
CRLF), ellers får stedet ingen prik på kortet. Formen er altid `Sogn, Herred, Amt, Danmark`
med **historiske** inddelinger, og niveau 3 er sognekirkens koordinat, ikke landsbyens.
Slå herredet op — gæt det aldrig. **Skriv filen altid binært med CRLF** — `stedtjek.py`
læser filen binært, og en fil gemt med rene LF får kontrollen til at melde «3 sogne, 2
herreder» og liste hvert eneste sogn i træet som manglende, selv om filen er uskadt.
Filen er ofte åben i Excel hos brugeren; `PermissionError` betyder "sig til", ikke "opgiv".
`.bak1…9` er en manuel rotation — lav en ny, før du retter.

### Noter

**En note skriver det, der er rigtigt — ikke at den før sagde noget forkert.** Ingen «RETTET
DEN …», «Noten hed før …», «her stod to ting, som begge var forkerte», og aldrig brugerens
navn i en note om et menneske fra 1700-tallet. **Er noget rettet, står der kun det rigtige.**
Hører rettelsen til noget, der skal kunne findes igen, hører den hjemme i `arkiv/README-DA.md`
— **journalen er stedet for processen, posten er stedet for mennesket.**

Undtagelsen er **kildekritik, ikke selvkritik**: at en indførsel kan læses to måder, at et
negativt resultat dækker bestemte årgange, at en alder ved døden er et skøn — det er
oplysninger om *kilderne* og skal blive stående.

**Der er ingen OCR.** Alle afskrifter er håndskrift læst af AI-assistenten fra scanningen. Mærk dem
som sådan i kildenoten, sig når en læsning er usikker, og hæft altid billedet på.

### Nulevende

**Opret ikke nulevende mennesker**, blot fordi de er nævnt i et dokument. Skriv navnene i
afskriften og spørg. **Men dokumenterede slægtninge må oprettes, også hvis de muligvis
lever** — det er projektets regel: det kræver en kilde, der binder dem sikkert til familien
(dåb, vielse, folketælling, en forælders dødsindførsel), og aldrig `1 DEAT`/`1 DEAT Y` på en,
der kan være i live. Et FamilySearch-brugerbidrag alene er ikke nok.

### Læsning og søgning

**Mistro din egen læsning, ikke kun databasen.** Et stednavn eller et fornavn, du har
læst forkert, kan bære en hel søgning hen, hvor der intet er — og hver kontrolprøve undervejs
vil bekræfte, at søgningen var korrekt udført. Ét fejllæst sognenavn har kostet tre grundige
folketællingssøgninger, en herredsopslagning, en kirkekoordinat og to rækker i stedfilen.
**Et ord, der ikke kan læses sikkert, må ikke bære en søgning alene** — søg på det, der er
sikkert (alder, fødesogn, patronym), og lad stednavnet være kontrollen.

**Årsoverskrifter står ikke altid øverst på siden.** I mange bind står «Anno NNNN» midt på
siden, hvor en ny årgang begynder. Et kontaktark, der kun tager toppen af hvert opslag
(`gkasse.py … 0 1 0 0.16`), viser derfor den forkerte årgang. **Kalibrér på en overskrift,
du har set hele vejen ned til.**

**Et år er ikke læst, før begge naboopslag er set.** Kirkebøger ført «fra advent til advent»
begynder i december året før, og en årgang deler typisk opslag med både den foregående og den
følgende — fx nr. 1-3 nederst på ét opslag og nr. 4-12 på det næste.

**En smal navnesøjle kan ikke bære et negativt resultat.** At beskære x 0,10-0,46 af hver
side og stable flere opslag er hurtigt til at *finde* et navn, men to kendte dåb i samme
spænd er blevet overset af netop den stribe. **Et «ikke fundet» kræver, at siderne er læst.**

**Ved du ikke, hvilket sogn du skal slå op i, så prøv `arkivdk.py` på navnet alene, før du går
i avisen.** En person kan være søgt forgæves i flere runder — altid på efternavnet *sammen
med* et formodet sted — mens `arkivdk.py "Fornavn Efternavn"` giver ét træf: et navngivet
pressefoto med bopæl, og en søgning på efternavnet alene giver faderen. **Bopæl, sogn og
faderens navn på ét minut**, hvor timers avisarbejde ikke rakte — og derefter er kirkebogen
en almindelig opslagning. Lokalarkivernes billedregistranter rummer hundredvis af navngivne
portrætter fra 1960'erne og 70'erne, altså netop det vindue, hvor kirkebøgerne holder op.

**Et negativt resultat fra Mediestream efter 1886 betyder «ikke læst», ikke «ikke fundet».**
Alt nyere end 140 år er spærret: `avis.py` kan se *hvilken* avis, dato og side et navn står på,
men ikke teksten. **`njavis.py` kan læse den** — NORDJYSKEs historiske avisarkiv viser et gratis
OCR-uddrag af selve siden og dækker Vendsyssel Tidende og Aalborg Stiftstidende **1767-1999**.
Sider, der var «ulæselige» i Mediestream, kan på den måde blive til læsbare artikler.
**Har sporet nordjyske rødder, så prøv altid `njavis.py`, før du skriver noget negativt ned.**

> **Og Mediestream kan TÆLLE, selv om den ikke kan læse.** `/aviser/hits` virker på hele
> perioden, og `py:` og `timestamp:` kan snævres ind. Med nok tællinger kan en enkelt side
> indkredses til dag og avis uden at se et ord.

**Er en person født i udlandet, så slå KONFIRMATIONEN op i den danske kirkebog.** Rubrikken
hedder «Konfirmandens fulde Navn efter forevist **Daabsattest**» — og når dåben er sket i
udlandet, måtte præsten skrive *hvor*. Én linje kan give både det udenlandske sogn og
moderens **pigenavn**, som ingen anden dansk kilde har: hverken folketællingen,
dødsregistret eller registerbladet. **Samme rubrik navngiver også forældrene.** Det er den
billigste vej ind i et udenlandsk sogn — og den ligger i Danmark.

**Skal du finde et sjældent efternavn blandt de begravede, så TØM kirkegårdene — søg dem ikke
igennem.** `gravsted.py`s søgefelt tager kun ét efternavn ad gangen, så 400 navne på 1.756
kirkegårde er en halv million kald. **`hel_kirkegaard()` henter en hel kirkegård i få kald**, og
så sorteres navnene bagefter. Hovedstadsområdets 112 kirkegårde kan læses på den tid, det tager
at søge ét navn over hele landet — og resultatet er uafhængigt af, om man gættede navnet rigtigt.

> **Og kirkegården fanger dem, skifteretten aldrig nævner.** Dødsregisterets nyere del og
> `stat.py` hviler begge på **Statstidendes proklama**, og et bo, der afsluttes som **uskiftet bo
> eller boudlæg, bekendtgøres aldrig.** En person kan ligge på en kirkegård, som
> dødsregistret slet ikke kender. **Et nul i Statstidende er ikke et nul.**

**Kraks Vejviser 1770-1969 er søgbar maskinelt** med `arkiv\krak.py` — se
`arkiv\KILDER-ONLINE.md`. **Gaderegistret er den hurtige vej**, for navneregistrets store
slægtsnavne er ordnet efter **stilling**, ikke efter fornavn.

**Søg også bruden.** En gennemgang, der kun leder efter slægtsnavnet som **brudgom**,
overser «N.N. og *Birthe Magdalene Eksempels Datter*». Patronymer på `-s Datter` og `-sen`
bærer slægtsnavnet videre gennem kvinderne.

### DDD (Dansk Demografisk Database)

**DDD skal have UTF-8 — ellers er ni amter usøgbare.** Formularen blev sendt som
`windows-1252`, mens headeren siger `charset=UTF-8`, og ASP-siden tror på headeren.
**Resultatet var HTTP 500, så snart et felt indeholdt æøå** — altså for **Hjørring, Præstø,
Holbæk, København, Sorø, Tønder, Aalborg, Ringkøbing og Århus**, og for ethvert navn eller
sogn med særtegn. Rettet i `ddd5.py` og `ddd6.py`. **Svaret afkodes stadig som
windows-1252** — det er en anden sag.

> **Og 500 betyder ikke «findes ikke».** Serveren svarer 500 på en fejl i forespørgslen, ikke
> med en tom liste. Et 500 er blevet læst som «den årgang har DDD ikke» — i virkeligheden var
> det ø'et i amtsnavnet. **Skil altid de to ad ved at gentage søgningen med et amt uden særtegn.**

> **Og 500'et er tilmed flakkende.** DDD kan svare 500 på *alle* forespørgsler i timevis —
> også kontrolsøgninger, der virkede minutter før — og et «ikke søgbart» i journalen er da
> forhastet. Nogle timer senere virker serveren igen, og med fire genforsøg per stavemåde
> kommer svarene. Én stavemåde af et efternavn kan give nul, mens en anden giver netop den
> husstand, der skal bruges. **Gentag et 500 mindst fire gange, og prøv navnet
> stavet på flere måder, før du skriver noget negativt ned.**

**DDD's nyere årgange er kun delvis indtastet.** Et amt kan have tællingerne fra 1911 til
1930, mens **1940 giver nul for hele amtet**, og enkelte sogne er slet ikke indtastet for
1921, 1925 og 1930 — efterprøvet mod et nabosogn, som giver over hundrede. **Et nul fra DDD i
1900-tallet betyder oftest «ikke indtastet», ikke «ikke til stede».** Gå til scanningerne.

**DDD's amtsnavne er ikke moderne dansk, og navnesøgningen er et «indeholder».** Amtet hedder
**«Aarhus»**, ikke «Århus» — og den forkerte form giver **500, ikke nul**. Og navnefeltet matcher
på hele strengen som delstreng: **`Søren Prøvesen` giver nul, mens `Søren Prøvessen` giver
træf**, når kilden staver efternavnet med dobbelt s. **Søg på fornavnet alene, eller på en
delstreng uden patronymets endelse**, når et navn, du ved findes, ikke vil komme frem.

**DDD har to døde felter.** `fødested` og `herred` sendes med i formularen og **ignoreres af
serveren** — et nul fra dem betyder intet. `county` (amt) er obligatorisk, og `parish` (sogn)
virker. **Efterprøv altid filteret på noget, du ved findes, før du tror på et nul.**
Husstandsvisningen (`dddperson.py`) giver til gengæld amt, herred, sogn og stednavn gratis i
overskriftslinjen.

### Træet

**En xref-liste er ikke en navneliste.** `1 CHIL @X600@` fortæller intet om, hvem
barnet er. Der er oprettet dubletter på netop den måde: en familie blev slået op, **børnene
talt** — fem stykker — og et «sjette» barn oprettet, som var nummer tre af de fem. Og en
person blev oprettet «uden for træet, så sporet ikke går tabt», skønt hun havde stået der
siden dagen før med både dåb og trolovelse. **Slå navnene op, ikke antallet — og gør det,
før jobfilen skrives, ikke efter.**

En hurtig kontrol før enhver `add-child`, `add-spouse`, `add-parent` eller `add-unlinked`
(kør den i mappen med `facit.json`, dvs. `SLAEGT_ARBEJDSMAPPE`):

```
python -c "import json,io,sys; sys.stdout.reconfigure(encoding='utf-8'); d=json.load(io.open('facit.json',encoding='utf-8')); [print(x,' '.join(f['tekst'].split(chr(10))[0] for f in p['fakta'] if f['tekst'].startswith('1 NAME'))) for x,p in d.items() if p.get('slags')=='PERSON' and 'SØGEORD' in json.dumps(p,ensure_ascii=False)]"
```

**«Klienten kan ikke X» er en påstand med en dato på, ikke en naturlov.** Denne fil er
skrevet i lag over lang tid, og en sætning om, hvad værktøjerne *ikke* kan, kan være
forældet. **Søg i mappen, før du bygger noget:** et `grep` på webtrees-rutenavnet
(`link-child-to-family`) finder `arkiv\haeftbarn.py` på ét sekund, og det er billigere end at
udvide klienten med noget, der allerede ligger der. Læs også
`poster\README-DA.md` **til ende**, ikke kun op-tabellen.

**Og mistro især et fund, der virker for godt.** Et ukendt barn af den ældste kendte
stamfader, eller en person, ingen har set før, er langt oftere en post, man ikke har slået op,
end en opdagelse.

**Den samtidige kilde slår den senere.** En dåb fra 1746 vejer tungere end en alder opgivet
ved døden i 1811. **Aldre i dødebøger og folketællinger er skøn** — gode nok til at genkende
en person på, ikke gode nok til at datere en fødsel med.

## Slægtshistorierne som bog

**Opskriften står i `.claude\skills\slaegtsbog\SKILL.md`** — trin for trin fra råstof til
kontrolleret PDF, med fejlmeldinger og fælder. **Følg den, også når opgaven ser lille ud.**
Råstoffet (anetavle, børneflokke, mediefiler og tavle-udkast) kommer fra
`python arkiv\bogdata.py <xref> [led]`, som læser `facit.json` — **en tavle skrives aldrig
efter hukommelsen.** Startpersonen er den, fortællingen handler om (typisk brugeren selv).

`byg-pdf.ps1` sætter hver `SLAEGTSHISTORIEN*.md` i roden med `mdpdf.py --bog`: titelblad,
indholdsfortegnelse, ny side for hver «del» (H1), levende sidehoved og PDF-bogmærker. Uden
`--bog` sættes et dokument fortløbende. Øverst i filen kan stå `<!-- undertitel: … -->` og
`<!-- forside: media/… "klip=…" -->`.

**Slægtstavler skrives som en ```` ```tavle ````-blok, ikke som ASCII-kunst.** Én linje per
generation, de ældste øverst; `mdpdf` tegner bokse og linjer:

```
Far; undertekst ∞ Mor  ||  Far ∞ Mor; undertekst        to par side om side
Søn; f. 1861 ∞[gift 14. maj 1889] Datter                to par over ét par = de to børn gifter sig
søskende[10 børn, 7 fundet]: A (1890) · ^B (1897) · C    søskendeflok i ét felt; ^ = den, linjen går gennem
børn: Folmer; glarmester || ^Magna ∞ Olfert              børn i hver sin boks
A — B                                                    — er samliv (stiplet), ∞ er ægteskab
Anders Eksempelsen <-- femtipoldefar                     randnote
```

`;` indleder en undertekst · `Navn (1852-1917)` får årstallene på egen linje · `∞[1889]`
tegnes «∞ 1889» · `^` foran en person betyder, at slægtslinjen går gennem hende og ikke
gennem den førstnævnte. En syntaksfejl standser bygningen med linjenummer. En almindelig
```` ``` ````-blok sættes stadig i fastbreddeskrift og skaleres ned, hvis den er for bred.

**Billedklip er almindelig markdown med klippet i titlen:**

```
![Eksempelby kirkebog 1847, døde mandkøn nr. 9: N.N.](media/kirkeboger/1847-eksempelby-doede-nn.jpg "klip=0.10 0.68 0.41 0.48")
![Dagbladet, 12. februar 1953](media/dodsannoncer/1953-….jpg "side=højre bredde=0.42")
```

`media/` er webtrees' mediemappe (`WEBTREES_MEDIA`). `klip=x0 x1 y0 y1` er brøk-koordinater
som i `gkasse.py`; `side=højre|venstre` lader de næste afsnit løbe rundt om billedet;
`bredde=` er andel af satsbredden; `kontrast` strammer en bleg side op. **Klippet laves i
hukommelsen, hver gang PDF'en bygges — der skrives ingen billedfil**, så reglen om, at ingen
fil må ligge to steder, holdes af sig selv. `arkiv\klip.py <fil> --gitter` lægger et
10 %-gitter over siden, `klip.py <fil> x0 x1 y0 y1` viser prøveklippet og udskriver den
færdige markdown-linje. Billedteksten skal nævne kilde, år og nummer. **Brugeren udpeger
selv, hvilke klip der skal med** — det skal være få.

## Docker-opsætningen, kort

`DB_*` og `WT_*` er **med vilje udeladt** af compose-filen: er de sat, kalder entrypointet
sin egen Apache, før den lytter, og containeren genstarter i ring. Opsætningsguiden køres i
browseren i stedet. `BASE_URL` skal matche det værtsnavn, installationen nås på (fx et
Tailscale-navn), præcist — ellers fejler login. Resten — backup, Tailscale-ACL,
privatlivsindstillinger — står i `INSTALL-DA.md`.
