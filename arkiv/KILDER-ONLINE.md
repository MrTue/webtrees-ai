# Danske kilder på nettet — hvad der findes, og hvad der kan bruges maskinelt

Alt herunder er afprøvet mod kilderne selv (efterprøvet sept. 2026) — der står ved hver
enkelt, hvad status er. Kolonnen «maskinlæsbar» siger, om kilden kan hentes med et script
uden login, uden CAPTCHA og uden browser.

Mærkning:
**✔ virker** = afprøvet og brugt · **○ afprøvet** = fundet og verificeret,
endnu ikke brugt · **? uprøvet** = kendt, men ikke testet · **✘ lukket** = prøvet,
virker ikke maskinelt.

---

## 0. Hurtigoversigt — det, der virker fra kommandolinjen

| Kilde | Kald | Værktøj |
|---|---|---|
| **Arkivalieronline** billeder | `ao-images.rigsarkivet.dk/ao/<id>/full/full/0/default.jpg` | `baand.py` `grundtal.py` |
| **Arkivalieronline** bind for et sogn | `api.rigsarkivet.dk/ao/v1/…?bsid=` | `bindng.py` `geosoeg.py` |
| **Sall Data** — indeks til HELE AO efter kategori | `ao.salldata.dk/index.php?type=&n1=&n2=` | **`sall.py`** |
| **Erik Brejl** — skifteuddrag, fuldtekst | `brejl.dk/<herred>.html` | **`brejlalle.py`** `brejlsoeg.py` |
| **Banditter** — fangeprotokoller 1752-1932 | `banditter.dk` (ASP.NET-postback) | **`banditter.py`** |
| **Mediestream** — aviser | `labs.statsbiblioteket.dk/labsapi/api/aviser/hits?query=` | `avis.py` |
| **Københavns Stadsarkiv** — Solr | `solr.kbharkiv.dk/solr/apacs_core/select?q=` | `kbhdato.py` `kbhsweep.py` |
| **arkiv.dk** — lokalarkivernes billeder | `arkiv.dk/soeg?searchstring=` | `arkivhent2.py` |
| **Findgravsted** | `findgravsted.brandsoft.dk/bsk_app/…` | `gravsted.py` |
| Tjek af om en kilde svarer | — | **`kildetjek.py`** |

**Kun gennem brugerens egen browser:** FamilySearch (se `METODE.md`).

**Virker ikke maskinelt:** Danish Family Search
(kræver oprettelse) · Dansk Demografisk Database via den gamle formular (se `ddd5.py`) · Histreg
(endepunktet svarer, søgningen giver nul) · Ancestry og MyHeritage (betaling).

---

## 1. Det, projektet allerede bruger

### Arkivalieronline — Rigsarkivets skanninger

| | |
|---|---|
| **Adresse** | `https://arkivalieronline.rigsarkivet.dk` |
| **Billed-API** | `https://api.rigsarkivet.dk/ao/v1/billedviser/billed-reference-lister?bsid=<n>` |
| **Billeder** | `https://ao-images.rigsarkivet.dk/ao/<grundtal+opslag>/full/full/0/default.jpg` |
| **Status** | **✔ virker** — hele projektets fundament |

Alt hentes uden login. Nøglerne er **bsid** (et bind) og **grundtal** (billed-id
for opslag 0). Værktøjerne `grundtal.py`, `bindng.py`, `baand.py`
bygger på det.

**To grene, som er let at forveksle:**
- **Geo-grenen** `/da/geo/geo-collection/<n>` — kun få samlinger: **5** kirkebøger ·
  **3** personregistre Sønderjylland · **8** brandforsikring · **9** realregistre og
  skøde-/panteprotokoller · **12** borgerlige vielser · **18** skifter · **42**
  retsvæsen · **55** fæsteprotokoller · **60** provstierne · **63** købstæder og
  købstadskommuner.
- **Tema-grenen** `/da/collection/theme/<n>` — alt det øvrige: **2** folketællinger ·
  **12** ejendomme · **21** lægdsruller · **30** skifter.

**Folketællingerne** ligger et tredje sted igen: `/da/rif/rif-collection/7` →
`/da/rif/select/7/<årgangs-id>`, og hver årgang har sit eget indeks. Værktøjerne
`ftaar.py` og `ftsogn.py` gør det. **Bemærk at sogne, der før 1864 hørte under hertugdømmet
Slesvig — også dem nord for Kongeåen og de slesvigske enklaver i kongeriget — ligger under
«Slesvig», ikke under «Landdistrikter».** Leder man det forkerte sted, finder man intet.

> **Den nyeste folketælling er 1940 — der kommer ingen 1950-tælling** (efterprøvet sept. 2026
> med `python arkiv\ftaar.py 19`): rækken ender ved **Folketælling 1940**
> (København, Frederiksberg, Gentofte, Købstæder, Sogne- og købstadslister) plus samlingen
> «Originale folketællinger (1769-1935)». **Regn derfor ikke med, at 75-årsreglen åbner
> 1950-tællingen** — den er ikke lagt ud, og den amerikanske `ft1950.py` er noget andet
> (USA's tælling, frigivet 2022).
>
> **Det sætter en hård grænse for nulevende slægtninge født efter november 1940:** de kan
> ikke findes i nogen dansk folketælling. Tilbage står kirkebøgernes fødte, som er scannet
> og læsbare op til ca. 1960 — kun Anmærkninger-kolonnen er sløret i vinduet 1892-ca. 1960.

### Mediestream — Det Kgl. Biblioteks aviser

| | |
|---|---|
| **API** | `https://labs.statsbiblioteket.dk/labsapi/api/aviser/hits?query=…` |
| **Tekst** | `/aviser/export/fields` — **kun materiale ældre end 140 år** |
| **Status** | **✔ virker** (`avis.py`) |

Årstal skal ind i selve søgningen som `py:[1870 TO 1890]`; `startTime`/`endTime`
ignoreres. Flerords­udtryk **skal** sættes i anførselstegn, ellers OR-søges der.
Andre felter: `lplace:Odense` (udgivelsessted), `familyId`.



### Distriktsaviser og ugeaviser — de findes, men ikke på nettet

| | |
|---|---|
| **Registrant** | `kb.dk/find-materiale/samlinger/avissamlingen/lister/liste-over-distriktsaviser/liste-over-distriktsaviser.pdf` |
| **Værktøj** | `distriktsaviser.py <søgeord>` |
| **Status** | **✔ virker** — men giver et magasinnummer, ikke en tekst |

**Mediestream rummer 505 avistitler.** Det lyder af meget, men de københavnske er
udelukkende de store historiske dagblade — Aftenbladet, Dagbladet, Dags-Telegraphen,
Fædrelandet, København, Politiken. **Ingen lokale ugeaviser fra nyere tid.**

> **Et nul i Mediestream betyder derfor ikke, at avisen ikke findes.**
> Den står bare på papir i Statens Avissamling i Aarhus.

#### To veje uden om 140-årsgrænsen

**1. `nordjyske-avisarkiv.dk` — Det Nordjyske Mediehus' eget arkiv.** 3,8 mio. sider,
**fuldtekstsøgbare og læsbare**, uden ophavsretsspærring, fordi huset selv ejer rettighederne.
Titler og årgange: **Vendsyssel Tidende 1873-1999** · **Aalborg Stiftstidende 1767-1999** ·
NORDJYSKE Stiftstidende 1999- · Frederikshavn Avis 1853-1995 · Thisted Dagblad 1882-2009 ·
Morsø Folkeblad 1877-2019 · Løgstør Avis 1882-1999 · Fjerritslev Avis 1899-1999 · Skagens Avis
1913-1993. **Aalborg Amtstidende og Nordjyllands Social-Demokrat er IKKE med** — de hørte til
andre huse. **Søgningen er gratis, og træflisten viser et kort OCR-uddrag omkring søgeordet** —
nok til at afgøre, om man har fat i den rigtige side og den rigtige annonce. **Hele siden og
artiklen kræver abonnement.** Værktøj: **`arkiv/njavis.py`**.

> **Uddraget kan løbe to nabospalter sammen**, så to dødsannoncer bliver til én tekstklump —
> læs efter, hvor den ene slutter. Og **mellemrum skal sendes som `%20`, ikke `+`**: med `+`
> falder citationstegnene ud af kraft, og en frasesøgning bliver til løsrevne ord.

Arkivet er inkluderet i Nordjyskes almindelige digitale abonnementer; de gamle dags- og
ugepriser fra åbningen findes ikke længere. **Køb og login er brugerens; AI-assistenten læser
kun i brugerens egen, loggede-ind fane.**

**Arkivet har en liste over kendte huller** (strejker, lockout, manglende mikrofilm) på
`/spoergsmaal-og-svar/` — blandt andet **Aalborg Stiftstidendes A-udgave 1943-1960 og
egnssiderne 1969-1980, som slet ikke er med**, og Vendsyssel Tidende Hjørrings lange strejke
**28.3.-15.8.1981**. Slå datoen op dér, før et nul tolkes som «ikke i avisen».

**2. `Mediestream Folkebibliotek`.** Siden 2017 kan folkebiblioteker give adgang til **ca. 6,5
mio. avissider fra 68 titler fra før 2002**. Adgangen er **IP-styret på bibliotekets matrikel**
— ikke hjemmefra med lånernummer — men det er det *lokale* bibliotek, ikke Det Kgl. Bibliotek i
København eller Aarhus. Nogle kommuner åbner den også på lokal- og stadsarkiver. **Titellisten
er ikke offentlig; spørg `forbiblioteker@kb.dk` eller det lokale bibliotek.**

Det Kgl. Bibliotek har en **registrant over distriktsaviser**: 271 sider, aviser fra
1866 og frem, ca. 31.200 bind, pakker og æsker. For hver titel står årgangene og et
**magasinnummer** (`H-129`, `K-108` og så videre) — og magasinnummeret er præcis dét,
biblioteket skal bruge ved en kopibestilling.

```
python distriktsaviser.py "<avistitel>"

   <avistitel> (<by>)           … 1960 – 1969 H-1xx
                                … 1970 – 1979 H-1xx
                                … 1980 – 1989 H-1xx
```

**To fælder i registranten:**

Rækkefølgen er **ikke alfabetisk** — titlerne står, som de står i «Lokalpressen»s
titelregister, så en avis kan gemme sig under en anden hovedtitel. Registrantens egen
vejledning siger det rent ud: *«Søg og du skal finde!»* Søg derfor på flere stavemåder
og på bydelens navn, ikke kun på titlen.

Og PDF'ens punktlinjer (`.........`) klæber årstallene sammen med titlen i tekstlaget.
Scriptet erstatter dem, før der søges; gør man det ikke, matcher ingenting.

**Hvad man kan bruge dem til:** lokalaviserne skrev om almindelige mennesker — skolefester,
foreningsliv, sølvbryllupper, portrætter af folk i kvarteret. Det er stof, de store
dagblade aldrig bragte. For enhver københavner efter ca. 1900 er der en distriktsavis, der
dækkede netop den gade.

### Politikens digitale avisarkiv — dødsannoncerne

| | |
|---|---|
| **Adresse** | `https://e-avis.politiken.dk` |
| **Dækning** | fuldtekstsøgbart fra **1. oktober 1884** |
| **Adgang** | brugerens eget abonnement, logget ind i Chrome |
| **Status** | **✔ virker** |

**Søgeopskriften** er en ren URL, ingen klikkeri i datovælgeren (den er ubrugelig):

```
https://e-avis.politiken.dk/search?q=%22Anders+Eksempelsen%22&title=2669&from=1950-01-01&to=1979-12-31&s=date_asc
```

`title=2669` er Politiken. Anførselstegn giver frasesøgning. Uden datofilter
stopper resultatlisten ved 10.000.

**Sidebilledet hentes sådan:** åbn opslaget, skift til enkeltsidetilstand, klik
zoom to gange — først da henter læseren siden i **2560 punkters bredde** i
stedet for 768. Billedet ligger som en `blob:`-URL på et `<img>`-element og kan
gemmes med et par linjers JavaScript i konsollen. Derefter klippes udsnittet med
`PIL` og forstørres 3-4 gange.

#### Det, der faktisk kan findes — og det, der ikke kan

> **Kun den fede navnelinje i en dødsannonce kommer igennem OCR'en.**

Det er den vigtigste erfaring. En dødsannonce har navnet sat i halvfed antikva i
12-14 punkt — det læses rent. Alt det øvrige — pårørendes underskrifter i
kursiv, adresser, klokkeslæt — er sat i seks punkt og bliver til grød.
Erfaringerne fra en række prøvesøgninger:

* **Den dødes navn** i den fede linje → typisk **1 træf**, det rigtige.
* **En efterladts navn** i underskriften → **0 træf**, selv om navnet står med
  rene bogstaver på den fundne side. Det er sat i kursiv seks punkt.
* **Et efternavn med ø** giver ofte **0 træf**; stavet med o i stedet giver det
  tusindvis af træf på lignende ord. Søgemaskinen er fuzzy og **ø'et overlever sjældent**.
* **Et kort efternavn, der ligner et almindeligt ord** (eller et bøjet verbum), giver
  10.000 træf, og alle sammen er det almindelige ord.

**Regel:** søg på **den dødes** navn, aldrig på de efterladtes. Og søg på
efternavne, der ikke ligner almindelige ord.

#### To slags stof, to epoker

**1884 til ca. 1945: den daglige begravelsesliste.** Politiken bragte hver dag
en fortegnelse over Københavns begravelser, ordnet efter kirke og kapel, med
klokkeslæt efter hvert navn:

> «— *[Kirke]:* Snedker **[fulde navn]**, 14. — *[Kirke]:* Direktør [fulde navn], 14. …»

Den er redaktionelt stof — familien betalte ikke for den — så **alle**
københavnske begravelser står der. For enhver forfader, der døde i København
eller på Frederiksberg før krigen, er der altså en linje at hente, med kirke,
dag og time.

**Efter krigen: de betalte annoncer.** Listen forsvinder, og tilbage står
rubrikken DØDE med familiernes egne annoncer. De er til gengæld langt mere
værd, for de **navngiver de efterladte**: enken, døtrene med deres ægtemænd,
stilling, begravelsesdag og kirkegård. Underskrifterne binder ofte tre generationer
sammen med de navne, familien brugte i det virkelige liv — kaldenavne og gifte navne,
som folkeregistret aldrig kendte.

#### Ophavsret og hensyn

Materialet er bag abonnement. Enkeltsider kan hentes ned til privat brug efter
ophavsretslovens § 12 og gemmes lokalt. **Systematisk
høstning af arkivet er ikke gjort og bør ikke gøres** — det er i strid med
abonnementsvilkårene og risikerer at lukke kontoen.

### Københavns Stadsarkiv — åbent Solr-endepunkt

| | |
|---|---|
| **API** | `https://solr.kbharkiv.dk/solr/apacs_core/select?wt=json&q=…` |
| **Status** | **✔ virker** (`kbhsweep.py`, `kbhdato.py`) |

Samlinger: **17** politiets registerblade 1890-1923 (1.965.257 poster) · **1**
begravelsesprotokoller 1805-1940 (619.178) · **10** borgerlige vielser (143.488) ·
**150** folkeregisterkort (51.568) · **19** politiets efterretninger (9.033) ·
**18** erindringer (3.322).

> **Det, der virkelig virker her, er at søge på FØDSELSDATO i stedet for navn:**
> `dateOfBirth:"1852-11-04T00:00:00Z"`. Det finder en begravelse, hvor navnesøgningen
> fejler, fordi navnet er stavet eller indtastet anderledes.

### Øvrige, der er brugt

| Kilde | Adresse | Status |
|---|---|---|
| **arkiv.dk** (lokalarkivernes fælles base) | `arkiv.dk/soeg?searchstring=…` | **✔** — billeder ligger i `og:image` **uden filendelse**: `arkibasapi-apim.azure-api.net/filer/visning/<guid>` |
| **Slægtsbiblioteket** (Danskernes Historie Online) | `slaegtsbibliotek.dk` · **`/online-lister/alle-online`** | **✔✔ DEN VIGTIGSTE AF DEM ALLE — se afsnit 2b.** Titellisten er én HTML-side; `sbib.py` søger i den. Bøgerne er PDF med tekstlag, så `pdfsoeg.py` kan søge i dem |
| **Findgravsted** | `findgravsted.brandsoft.dk/bsk_app/…` | **✔** — to endepunkter: `SoegKirkegaard` og `AfdoedeSoeg` |
| **Dødsregisteret** | `dodsregister.dk` | **✔** — alle dødsfald 1943-1969 + udvalgte 1804-1939 |
| **Wiberg, præstehistorie** | `wiberg-net.dk/<nr>-<Sogn>.htm` | **✔** — kan afkode et forvansket præstenavn i en til-/afgangsliste og dermed det sogn, attesten kom fra |
| **Luftfotos, Det Kgl. Bibl.** | `cop.kb.dk/cop/syndication/images/luftfo/…` | **✔** |
| **FamilySearch (træ og indeks)** | `familysearch.org` | **✔ i brugerens egen, logget-ind browserfane · ✘ fra et script** — botbeskyttelse blokerer programmatisk login. Brugeren logger selv ind; assistenten henter i fanen. Se `METODE.md` |
| **Dansk Demografisk Database** | `ddd.dda.dk` | **✔ med det nye endepunkt** — den gamle `soeg_person.asp` svarer 0 rækker; se afsnittet om DDD længere nede (`ddd5.py`, `dddperson.py`) |

---

## 2. Sall Data — et indeks til hele Arkivalieronline

| | |
|---|---|
| **Adresse** | `http://ao.salldata.dk/index.php?type=<kategori>&n1=<amt>&n2=<myndighed>` |
| **Status** | **○ afprøvet — virker, ingen login, ingen begrænsning** |

**Det er et komplet alternativt indeks til hele Arkivalieronline, ordnet efter
kategori og amt — og det giver bsid direkte.** Det er præcis den nøgle, projektets
egne værktøjer bruger.

**De otteogtyve kategorier** (`type=`):

`kb` kirkebøger · `ft` folketællinger · `personregister` sønderjyske personregistre ·
`borgerlige` borgerlige vielser · `stiftelsen` Fødselsstiftelsen ·
`udvandring` ud- og indvandring · `notarial` notarialprotokoller ·
`faeste` fæsteprotokoller · **`borgerskab`** · `skifter` ·
`justits` justitsministeriet · `laegd` lægdsruller · `medalje` erindringsmedaljer ·
`stamb` stambøger · `flaaden` flåden · `milits` andre militære ·
`matrikel` Christian V's matrikel 1688 · `bygning` ejendomshistorie ·
`tingbog` tingbøger 1927-2000 · `brand` brandforsikringer · `gods` godsarkiver ·
`retsbetjent` · `told` · `rejsende` · `selskaber` · `amt` · `kommune` · `medicin`.

**Hvorfor det er stort:** de kategorier, der ellers er svære at finde — borgerskab,
brandforsikring, fæste, tingbøger, godsarkiver, notarialprotokoller — er ét opslag væk.

**Et eksempel på, hvad det giver:** `type=borgerskab&n1=<amt>&n2=<købstad>` kan give en
håndfuld bind, og blandt dem kan der være en *maskinskrevet*, alfabetisk fortegnelse over
byens borgerskaber i 1600-tallet med navn, dato **og fødested** («født i [landsby]», «født i
[by] i Holsten»). Få opslag, fuldt læsbare.

**Sall Data har desuden en række opslagsværktøjer**, som ville have sparet timer:

| Værktøj | Adresse | Hvad det gør |
|---|---|---|
| **Sogn til lægd — lægd til sogn** | `salldata.dk/laegd/` | slår lægdsnummeret op — **brug den før enhver lægdsrulle-søgning**; alternativet er at binærsøge lægdsnummeret i hjørnerne af rullerne, og det kan koste en time. **○ afprøvet:** kaskaderende formular, `index.php?amt=&herred=&sogn=&aar=` — **amt, herred og sogn skal sættes samtidig**, ellers kommer kun listerne |
| **Find skiftemyndighed** | `salldata.dk/skifter/` | hvilken skifteret dækkede et sogn — afgørende og svært at slå op andre steder; brug den før enhver skiftesøgning. Hedder «Sogn til gods» |
| **Find matrikelnumre** | `salldata.dk/matrikel/` | |
| **Find ejerlav i et sogn** | `salldata.dk/ejerlav/` | |
| Gade til sogn i København | `salldata.dk/gader/` | |
| Lægedistrikt og lægekreds | `salldata.dk/laege/` | |
| Kirkesogne | `salldata.dk/sogne/` | |
| Stednavne | `salldata.dk/Sted/` · `/Stednavn/` | |
| Amts- og sognekort | `salldata.dk/Kort/` | |
| Hyppighed af navne | `salldata.dk/antal/` | hvor sjældent er et navn — afgør, hvor meget et navnesammenfald vejer |
| Ordbog over gamle ord | `salldata.dk/leksikon/` | |
| **Folketællinger som csv-filer** | `salldata.dk/zip/` | **hele indtastede årgange i CSV (KIP-format), til download.** Det er dér, en maskinel søgning burde begynde: en lokal CSV kan gennemsøges på sekunder mod timer i skanningerne. **Hentningen kræver, at man klikker et link, der bekræfter reglerne — «Filerne må udelukkende bruges til ikke-kommercielle formål!» AI-assistenten henter dem ikke. Det er brugerens beslutning at acceptere vilkårene** |
| Arne Julins indeks · Skippere · Erindringsmedaljer | fra forsiden | personindekser |

**Tegnsæt:** siden er UTF-8, men enkelte lister er latin-1. Indholdet ligger i
almindelig HTML uden JavaScript — let at parse.

---

## 2b. Slægtsbiblioteket — den vigtigste af dem alle

| | |
|---|---|
| **Titelliste** | `slaegtsbibliotek.dk/online-lister/alle-online` — én HTML-side med alle digitaliserede titler |
| **Bøgerne** | `slaegtsbibliotek.dk/<nr>.pdf` og `/2023/<nr>.pdf`, `/2024/<nr>.pdf` · nogle på `dis-danmark.dk/bibliotek/<nr>.pdf` |
| **Status** | **✔✔** — PDF'erne har tekstlag, så `pdfsoeg.py` kan fuldtekstsøge dem |

Biblioteket rummer **utrykte og trykte slægtsstudier, sognehistorier og
kildeafskrifter**, som privatpersoner har lagt til rådighed. De er ofte resultatet
af årtiers arbejde — og de er gratis.

**Søg både på slægtsnavnet og på stedet.** `sbib.py <efternavn>` finder slægtsbøger
om navnet — ofte udtømmende gennemgange af alle familier med navnet i en by, ordnet i
kodede led (A.119, E.13 …), med ordrette afskrifter af kirkebogsindførsler,
folketællinger og skifter, eller ældre stamtavler med kildehenvisninger til Wiberg og
Personalhistorisk Tidsskrift. `sbib.py <by eller sogn>` finder sognehistorier og
kildeudgaver.

`sbib.py <sogn>` kan give **en trykt kildeudgave af sognets ældste kirkebøger** — ofte
med tekstlag, så den kan fuldtekstsøges. Sådanne udgaver rummer tit mere end kirkebogen:
udgiveren har lagt samtidige lister ved, fx en **fortegnelse over sognets gårde og huse med
beboernes navne**. Den slags lister fanger også tilflyttere, som kirkebogen kun nævner i
forbifarten.

> **Læren:** før man fejer en kirkebog opslag for opslag, skal man spørge, om nogen
> allerede har skrevet den af. Det tager under et minut at finde ud af.

Hentede bøger bør ligge i webtrees' mediemappe (fx under **`boger/`**), hæftet på
deres kilder som medieobjekter — og ikke et sted uden for backuppen. Lad filnavnene
bære Slægtsbibliotekets nummer, fordi det er det eneste stabile håndtag disse værker
har: `slaegtsbibliotek-<nr>-…`. De kan fuldtekstsøges med `pdfsoeg.py`.

---

## 3. Erik Brejls skifteuddrag — det andet store fund

| | |
|---|---|
| **Adresse** | `https://www.brejl.dk/` — én HTML-side per herred/amt |
| **Status** | **○ afprøvet — ren HTML, fuldtekst, kan grepes** |

Erik Brejl har gennem årtier **transskriberet skifteuddrag** for det meste af
Jylland og en del af øerne. Hvert uddrag har samme faste form:

> *«161 [afdøde] i [landsby] i [sogn]. 6.8.1772, fol.310B. E: [enkens navn].
> LV: [navn], præst i [sogn]. B: 1) [søn] 11 2) [søn] 9½ 3) [søn] 6 4) [søn] 4
> 5) en datter, født efter…»*
> (E = enke/enkemand · B = børn · FM = formynder · LV = lavværge)

**Det er hele familier på én linje, med aldre og slægtskabsforhold.** For 1700-tallet,
hvor kirkebøgerne ofte kun giver faderens navn, er det den korteste vej til en
familierekonstruktion.

**Dækningen er bred, men ikke fuldstændig.** De fleste jyske herreder og amter har en
side, men enkelte herreder har ingen — og folk derfra kan alligevel dukke op på en
nabokøbstads side, fordi de blev skiftet dér. Nogle sider rummer ikke skifter, men
tingbøger, og enkelte købstadsider standser tidligere end de øvrige. **Et nul hos Brejl
siger derfor kun noget, når man har set, at sognets herred faktisk er dækket.**

> **Filnavnene følger ikke herrederne.** Et herred kan ligge under **amtets** side i stedet
> for sin egen; Nim herred hedder `voernim.html` og Tyrsting `tyrsgods.html`.
> **Gæt aldrig et filnavn** — brug `brejlalle.py`, som selv henter fortegnelsen og
> søger i alle 178 sider.

**Formyndere og lavværger er et spor i sig selv:** en formynder, hvis slægt og
landsby også optræder som faddere i familiens dåbsindførsler, er sjældent tilfældig.

Ud over skifterne rummer siden **tingbøger, matrikler og jordebøger,
brandprotokol og personarkiver**.

> **Tingbøgerne er en overraskelse for sig.** En af siderne er ikke skifter, men **et
> herreds tingbog fra 1577** — millioner af tegn ordret referat af retsmøderne. En søgning på en landsbys navn kan give snesevis af træf tre hundrede
> år før kirkebøgerne — i formen *«[bonde] på [gård] fordelte [tjenestekarl], som tjente
> ham og løb fra ham og for 4 mark, han har oppebåret af sin løn.»* (1577)
>
> Tingbøger giver ikke slægtskab direkte, men de giver **naboer, tjenestefolk,
> stridigheder og gårdnavne** — og for tiden før kirkebøgerne er de ofte det eneste,
> der findes.

**Tegnsæt:** siderne er blandet — nogle utf-8, andre windows-1252. Værktøjerne
`brejlsoeg.py` og `brejlalle.py` afkoder nu begge og vælger den, der giver færrest
erstatningstegn.

**Filnavnene er ikke systematiske** — herredsnavn ≠ filnavn (Nim herred =
`voernim.html`, Tyrsting = `tyrsgods.html`, flere ligger under `Niels/`). Hent
listen fra forsiden i stedet for at gætte. Scriptet `brejlliste.py` gør det.

---

## 4. Personindekser, der dækker på tværs af sogne

| Kilde | Adresse | Indhold | Status |
|---|---|---|---|
| **Nygaards Sedler** | `ddd.dda.dk/nygaard/sogeside.asp` | **425.433 sedler om JYSKE slægter**, 29.725 efternavne, 6.313 stednavne. Holger Hertzum-Larsen/Nygaards excerpter fra skifter, tingbøger, lensregnskaber m.m. | **○ fundet** — søgeside virker, endepunktet bag den er ikke fundet endnu |
| **Wads Sedler** | `sedler.dis-danmark.dk/wad/index.php` | Landsarkivar G. L. Wads kartotek 1893-1924 | **? uprøvet** |
| **Danish Family Search** | `danishfamilysearch.dk` | Indtastede kirkebøger og folketællinger **frem til 1960'erne**. Har egne indtastningsprojekter for **folketællingen 1906 OG 1940**, lægdsruller og gadenavne | **○ afprøvet — kræver gratis oprettelse.** Søgesiden sender til `/user/new/`. Siden er ASP.NET WebForms med `__VIEWSTATE`, så den kan ikke kaldes rent maskinelt. **AI-assistenten opretter ikke konti** — det skal brugeren gøre, hvis den skal bruges |
| **Politiets Registerblade** | `politietsregisterblade.dk` | Københavnere 10 år og ældre 1890-1923 | dækket af Solr-endepunktet ovenfor |
| **Banditter** | `banditter.dk` | **Indsatte i danske arrester, fængsler og tugthuse 1752-1932**, plus «offentlige fruentimmere» registreret hos politiet. Danske Slægtsforskere Odenses indtastning af fangeprotokollerne. Felter: fornavn, efternavn, bopæl, fødeår, indsættelsesår, forbrydelse | **✔ VIRKER MASKINELT — værktøj `arkiv/banditter.py`.** I praksis et historisk kriminalregister. Gratis, ingen login. Siden er ASP.NET, så der skal et viewstate-omløb til; det gør værktøjet. **Søgeresultatet giver fornavn, efternavn, kaldenavn, erhverv, fødselsdato, fødested og året for første indsættelse.** Navnesøgningen er «fuzzy» — et kort efternavn giver også alle sammensatte navne, det indgår i, forrest eller bagerst |
| **Erindringsmedaljer** (Sall) | `ao.salldata.dk?type=medalje` | Deltagere i krigene 1848-50 og 1864 | **? uprøvet** |
| **Skippere** (Sall) | `ao.salldata.dk` | Søfarende | **? uprøvet** |

---

## 5. Uden for kirkebøgerne — det, der bryder dødvande

Dette er afsnittet om at tænke ud af boksen. Hver af dem svarer på et spørgsmål,
kirkebøgerne ikke kan.

### Ejendommen frem for personen

**Brandforsikringsprotokoller** (AO geo-samling 8, eller Sall `type=brand`).
Hvert hus i en købstad har et **brandnummer**, og protokollen fører ejeren år for
år med vurdering og bygningsbeskrivelse.

> **Brug folketællingens brandnummer:** købstædernes folketælling 1801 opgiver ofte
> husets **brandnummer**. Brandprotokollen for det nummer viser, hvornår personen
> overtog huset — og hvem han overtog det fra. Det er den hurtigste vej til en
> tilflytters ankomst til byen.

**Realregistre og skøde- og panteprotokoller** (AO geo-samling 9). Hvem købte og
solgte hvad. Realregistret er ordnet efter *ejendom*, ikke efter person, og fører
hver matrikel gennem alle sine ejere.

**Christian V's matrikel 1688** (Sall `type=matrikel`) og **markbøgerne** — hvem
sad på hvilken gård før kirkebøgerne bliver detaljerede.

### Erhvervet frem for bopælen

**Borgerskabsprotokoller** (Sall `type=borgerskab`, AO geo-samling 63).
En håndværksmester i en købstad **skulle** løse borgerskab, og protokollen
navngiver som regel hjemstavnen. Se afsnit 2.

**Lavsarkiver** — smedelavet, bagerlavet. Svendebreve og mesterstykker. Ligger i
købstadsarkiverne. **? uprøvet.**

**Fæsteprotokoller** (AO geo-samling 55, Sall `type=faeste`) — for fæstebønder er
det ofte den eneste kilde, der binder to generationer sammen.

**Tyendeprotokoller** (Sall) — tjenestefolks skudsmål.

### Bevægelsen frem for stedet

**Til- og afgangslister** i kirkebøgerne. De fører **hvorfra, hvorhen, hvornår og
hvilken præst der udstedte attesten**. Den tredje oplysning — præstenavnet — kan
afkode et forvansket sognenavn: slå præsten op i Wiberg, så har man sognet.

> **Læren:** læs *alle* kolonner i en tilgangsliste. Datoen er attestens dato, ikke
> ankomstdatoen, og navnet bagefter er afsenderpræstens.

**Udvandrerprotokollerne** (`ddd.dda.dk`, Det Danske Udvandrerarkiv
`udvandrerarkivet.dk`, Ellis Island). Politiets udvandrerprotokoller 1868-1940 er
indtastet og fri.

**Lægdsruller** (AO tema 21, Sall `type=laegd`). Følger *mænd* fra fødsel til 36-års
alderen med **hvert eneste flytteår** noteret som «53 F 117». Kun landdistrikter
før 1849 — købstadsfødte drenge blev ikke indrulleret.

### Naboer og vidner

Faddere, forlovere, formyndere og lavværger er slægt. Det er den enkle, billige
metode: **en fadder, der går igen ved dåbene i tre husstande med samme efternavn i
samme sogn, binder dem sammen.**

### Trykte kilder

| Kilde | Adresse | Hvad |
|---|---|---|
| **Wibergs Præstehistorie** | `wiberg-net.dk` | alle sognepræster fra reformationen |
| **Dansk Biografisk Leksikon** | `runeberg.org/dbl/` · `biografiskleksikon.lex.dk` | |
| **Vort Sogns Historie** | `slaegtsbibliotek.dk/samlinger/vort-sogns-historie` | sognebeskrivelser for hele landet |
| **Trap Danmark** | `trap.lex.dk` | topografi, gårde, herregårde |
| **Kraks Blå Bog** | `runeberg.org/blaabog/` | |
| **Vejvisere og telefonbøger** | Det Kgl. Bibliotek | adresser år for år i byerne |

### Kort og geografi

| Kilde | Adresse | Hvad | Status (sept. 2026) |
|---|---|---|---|
| **Historiske Kort** | **`historiskekort.dk`** | cirka **100.000 skannede kort** fra 1600-tallet til år 2000 — original- og høje målebordsblade, matrikelkort, søkort — **plus cirka 100.000 digitaliserede luftfotos**. Drives af Klimadatastyrelsen | **adressen er flyttet.** Den gamle `hkpn.gst.dk` svarer ikke længere på DNS |
| **DIGDAG** | `digdag.dk` | administrativ inddeling gennem tiderne — hvilket herred hørte sognet til hvornår | **○ delvis nede:** «Grundet tekniske vanskeligheder har vi været nødt til midlertidigt at lukke for dele af siden» |
| **Krabsens stednavnebase** | `krabsen.dk/stednavnebase/` | stednavn → sogn, herred, amt | **○ nede:** «Teknisk omlægning. Grundet en teknisk omlægning er stednavnedatabasen…» |
| **sogn.dk** | | adresse → nutidigt sogn | ? |
| **ois.dk** | | adresse → matrikelnummer | ? |

### Gravsteder og dødsfald

| Kilde | Adresse | Status (sept. 2026) |
|---|---|---|
| **Findgravsted** | `findgravsted.brandsoft.dk` | **✔ virker** — to endepunkter, brugt i projektet |
| **Dødsregisteret** | `dodsregister.dk` | **✔ virker** — alle dødsfald 1943-1969 |
| **DK-gravsten** | `dk-gravsten.dk` | **○ svarer, har søgeformular** — og en «**Søgning efter forældre**», som er usædvanlig og nyttig. Alle kirkegårde alfabetisk |
| **Afdøde** | `afdoede.dk` | **○ svarer, har søgeformular** — dødsannoncer og mindesider, nyere tid |
| Find en grav | `findengrav.dk` | **○ svarer, men er bygget med frames** fra 1990'erne. Fotos af gravsten |
| Aneguf | `aneguf.dk` | **○ svarer, frames.** Indeks til dele af Statstidende — efterlyste arvinger i dødsboer |
| Weblager | `weblager.dk` | **○ svarer** — byggesager, JavaScript-drevet |

### Udenlandsk — når sporet går over grænsen

| Land | Kilde | Bemærkning |
|---|---|---|
| **Norge** | `digitalarkivet.no` · **`histreg.no`** | Digitalarkivet er gratis og har 80 mio. personnavne. **Histreg er et personbaseret indeks til hele Digitalarkivet** — kirkebøger, folketællinger og udvandrerprotokoller koblet sammen person for person. **○ afprøvet:** POST til `histreg.no/index.php/searchresults` med felterne `name · surname · birthyearfrom · birthyearto · birthdate · birthplace · place · job`, plus jokertegn (`Krist*`, `*nes`, `-Haugen`, `Ola\|Ole`). Endepunktet svarer, men gav nul rækker på alle prøver — formularen har desuden op mod hundrede kommune-flueben (`k0101`…), og søgningen kræver formentlig mindst ét. **Uløst.** Værktøj: `arkiv/histreg.py` |
| **Sverige** | **`sok.riksarkivet.se/folkrakningar`** · ArkivDigital (betaling) · Sveriges Dödbok (betaling, Rötter) | **✗ ikke maskinlæsbar — ALTCHA.** Søgeformularen er beskyttet af ALTCHA, et anti-bot-system med maskinudfordring, og **bruges ikke maskinelt**. Brugeren søger selv i browseren; til maskinel brug findes det frie CC0-datasæt nedenfor (`dds.py`). Søgbare personårgange: **1860, 1870, 1880, 1890, 1900, 1910 og 1930** (1930 er stadig under registrering). **Kun personer over 100 år er søgbare** (GDPR). **Den danske FT1950 har ingen svensk pendant, der kan søges:** FOLK1950 findes, men kun som forskningsdata via CEDAR i Umeå. **Husk svensk stavning:** dansk *Knud* er svensk **Knut**, *Valter* kan stå som *Walter*. **Dækningen er skæv:** 1860-tællingen findes stort set kun for Jämtland og Västernorrland, mens flere sydsvenske län først er med fra 1880. **En udvandrer fra de län, der rejste i 1870'erne, står derfor slet ikke i folkräkningarna.** |
| Slesvig/Holsten | `archion.de` (betaling) · Kirchenbuchportal | for sogne syd for 1920-grænsen |
| **Sverige, den frie vej** | **`filer.riksarkivet.se/registerdata/DDS/…`** · `data.riksarkivet.se/api/records` · `oai-pmh.riksarkivet.se/OAI/` · `lbiiif.riksarkivet.se` | **✓ frie data, ingen captcha.** Søgetjenesten `sok.riksarkivet.se` er ALTCHA-beskyttet **i hele sit omfang** — også `/arkiv/<id>` og `/fodelseregister/` — så de frie data er vejen for maskinel brug. **Demografisk Databas Södra Sverige** (grundlaget under fødselsregistret) ligger frit som CC0: `…/DDS/{Fodda,Doda,Vigslar}/…_csv.zip`, i alt 167 MB, **kodet cp1252, ikke UTF-8**. Det er både hurtigere og mere fleksibelt end formularen. Værktøj: `arkiv/dds.py` (`--hent` tager under et minut; zip-filerne hører ikke hjemme i projektmappen). **Dækning:** for 1850 kun omkring **en tredjedel af de skånske sogne**, og hele herreder er stort set fraværende. **Et nul fra DDSS betyder derfor oftest «ikke indtastet».** `data.riksarkivet.se/api/records?text=…` søger i BirthRecord og MarriageRecord, men **ikke** i folkräkningarna, og rate-limiter ved at **afbryde TCP-forbindelsen**, ikke med en HTTP-kode — læg pauser mellem kaldene. **IIIF-billeder af frit materiale:** billedserveren `lbiiif.riksarkivet.se` kræver samme Referer som arkivets egen fremviser (`Referer: https://sok.riksarkivet.se/`); uden den svarer den 403, også på frit materiale, og det må ikke læses som en tilgængelighedsgrænse. Værktøj: **`arkiv/riksark.py`** (`manifest` · `hent` · `gitter`). Billed-id'et er bindets C-nummer (fx `SE/LLA/<nr>/B/1` = `C00xxxxx`), opslagene `C00xxxxx_00001`, `_00002` …, og **opslag 1 er altid Riksarkivets omslagsblad**. Størrelser som IIIF: `full/max/…` eller `full/2000,/…`. **Og samme bog ligger under to id-systemer:** det gamle rent numeriske (otte cifre) svarer 403, mens `C`-nummeret på nøjagtig samme bind svarer 200 — et 403 betyder derfor «forkert id», ikke «spærret». **Bindets titel koster ingenting at slå op:** en `Range: bytes=0-1000` på manifestet giver `{"sv":["… Husförhörslängder, SE/LLA/<nr>/A I/6 (1863-1876)"]}`, og `C`-numrene er fortløbende og alfabetiske efter arkivnavn, så en løkke kortlægger et helt sogns bindliste på et minut. |
| USA | Ellis Island · FamilySearch · Find a Grave (`findagrave.com`) | Find a Grave har gravsten og mindesider med familielinks; værktøjer: `arkiv/findagrave.py`, `arkiv/fag2.py`, `arkiv/fagmem.py`. **Kun til enkeltopslag:** Find a Grave forbyder masse-skrabning i sine vilkår. Slå de få personer op, du faktisk leder efter, hold pause mellem kaldene, og brug det til personlig slægtsforskning |

> **Brug fødestedet i folketællingen:** fra 1845 opgiver de danske tællinger
> fødestedet, også når det er i udlandet («født i Trondhjem i Norge»). Et
> efternavn, der dukker op i et dansk sogn uden spor forinden, kan være norsk eller
> tysk — og **histreg.no** er stedet at prøve en norsk tråd.

### Maskinlæsning af den gamle skrift

**Transkribus** (`transkribus.org/languages/danish`) har modeller til dansk gotisk
kursiv og kirkebogsskrift. **FamilySearch Full-Text Search** kører AI-læsning af
håndskrift og er ude af Labs siden RootsTech 2024 — dækningen for Danmark er
uafklaret og bør efterprøves. Begge kunne i princippet vende hele arbejdsformen om:
i stedet for at læse tre hundrede opslag for at finde ét navn, søger man på navnet.

---

## 6. Det, der ikke virker maskinelt

| Kilde | Problem |
|---|---|
| **FamilySearch** | Botbeskyttelse. Login kan ikke og skal ikke gennemføres fra et script. Brug brugerens egen, logget-ind browserfane (se `METODE.md`) |
| **Dansk Demografisk Database, gammel formular** | `soeg_person.asp` returnerer nul rækker uanset søgning. Brug det nye endepunkt (`ddd5.py`), se afsnittet om DDD |
| **Ancestry / MyHeritage** | betaling og login |
| **CPR** | ikke offentligt efter 1968 |
| **Rigsarkivets 100-årsregel** | fødselsregistre lukket til cirka 1926 |

---

## 7. Værktøjerne til disse kilder

| Fil | Hvad |
|---|---|
| `arkiv/baand.py` | skærer to lodrette bånd (venstre og højre sides navnekolonner) ud af hvert opslag og stiller dem side om side — halverer antallet af visninger ved en folketællingsfejning |
| **`arkiv/sall.py`** | **browser Sall Datas indeks til hele Arkivalieronline. `sall.py <kategori> [amt] [myndighed] [filter]` → bind med bsid** |
| **`arkiv/brejlalle.py`** | **fuldtekstsøger i ALLE 178 sider hos Erik Brejl på én gang, med cache** |
| `arkiv/brejlsoeg.py` | søger i udvalgte Brejl-sider |
| `arkiv/brejlliste.py` | henter Brejls sidefortegnelse, så filnavnene kendes |
| **`arkiv/banditter.py`** | **søger i fangeprotokollerne 1752-1932 på banditter.dk — virker** |
| `arkiv/histreg.py` | Histreg, Norge — endepunktet svarer, men søgningen giver endnu nul |
| `arkiv/nygaard.py` | prøver Nygaards Sedler |

---

## 8. Hvad de indtastede kilder giver

En oversigt over, hvad de tre store indgange typisk giver, når de bruges mod konkrete
spørgsmål i et slægtstræ.

### Sall Data → en købstads borgerskabsprotokoller

`sall.py borgerskab <amt> <købstad>` giver en håndfuld bind. Blandt dem kan der være en
maskinskrevet, alfabetisk fortegnelse over byens borgerskaber med navn, dato **og
fødested**: *«[Efternavn], [fornavn], født i [landsby]»*. Fortegnelsen kan standse
tidligere end selve protokollen, så se efter i originalen, hvis årstallet ligger sent.

### Sall Data → en købstads skøde- og panteprotokoller

`sall.py bygning <amt> "<byfoged og herreder>" <by>` giver typisk:

| Protokol | Omfang |
|---|---|
| Personregister til skøde- og panteprotokoller for købstaden | ofte et helt århundrede |
| Flere overlappende personregistre for samme by | forskellige spænd i 1700- og 1800-tallet |
| Koncepter til realregister | midten af 1800-tallet |

Et personregister over hundrede års skøder og pantebreve kan afgøre, om en bestemt
person ejede et hus i byen — men opslagene er tætskrevne registerkolonner og kræver et
ordentligt gennemløb.

Retskredsene har lange, historiske navne, der ofte opregner tre-fire herreder og ændrer
sig undervejs. Slå myndighedens navn op i Sall frem for at gætte det; dens skøde-, pante-
og tingbøger ligger samme sted.

### Erik Brejl → en familie samlet fra skifterne

`brejlsoeg.py <efternavn> <side>.html` på et sjældent efternavn kan give en hel familie:
et skifte opregner børnene med alder, og ved et andet ægteskab kommer også halvsøskende
med. **Formynderne er ofte slægt** — en farbror, en morbror, en ældre halvbror — og binder
dermed grenene sammen. Brejl har også transskriberet andre kildetyper for enkelte egne,
som kan føre familien videre.

> **Et fravær kan også sige noget.** Står et led i et brugerbidraget onlinetræ, men
> slet ikke i de skifter, hvor det burde optræde, så mangler det støtte fra netop den
> kilde, der skulle have båret det.

### Erik Brejl → et slægtled fra ét skifte

`brejlalle.py "<fornavn> <efternavn>"` gennemgår alle 178 sider på én gang. Et skifte
efter en håndværker kan give enken, lavværgen og **alle børnene** — sønnerne med stilling
og bopæl, døtrene med deres ægtemænds navn og stilling. En datter, der kun var kendt fra
en dåbsindførsel, får dermed forældre og søskende.

Skiftet kan også **datere et ægteskab**: er en datter allerede gift på skiftedatoen,
ligger vielsen før — og ikke i de senere årgange af vielsesbogen.

### Slægtsbiblioteket → trykte slægtsbøger og stamtavler

**En trykt slægtsbog om en bys familier med ét efternavn** kan på én side give fødesogne,
børnenes fødselsdatoer og **faddernes navne ved dåbene**. Faddere fra et fjernt sogn kan
dokumentere et bånd mellem to sogne, som ellers kun hvilede på et navnesammenfald.

**En ældre stamtavle i bogstavled** (A1, B9, C1 …) kan **bekræfte** et mellemled, som
ellers kun står i et onlinetræ — og samtidig **rette** det, fx når linjen i virkeligheden
går gennem en bror til den, onlinetræet har valgt. Et forkert led i et onlinetræ er ikke
altid opdigtet; det kan være sat ind på den forkerte plads i familien.

### Hvad det siger om metoden

Fællesnævneren er, at det er **indekser og afskrifter, ikke skanninger**. At feje en bog
opslag for opslag virker, men det er dyrt: ét sogns folketælling kan koste over tyve
visninger for at give ét negativt svar, mens en søgning i et indeks koster ét kald.

> **Spørg et indeks først.** Sall Data siger på ét opslag, hvilke bind der findes; Brejl
> siger på ét greb, om navnet overhovedet optræder i herredets skifter. Først når indekset
> peger, skal skanningen frem.

Standardrækkefølgen:

**0) Slægtsbiblioteket — har nogen allerede skrevet slægten af?
1) Sall Data for at finde bindet ·
2) Brejl og de indtastede baser for at finde personen ·
3) Arkivalieronline for at læse originalen og gemme skanningen.**


---

## Tre greb i Politikens arkiv

**1. Forskyd OCR-vinduet ved at søge på et ord længere fremme i sætningen.**
Søgeresultatet viser kun omkring tres tegn på hver side af træffet, og en dødsannonce eller
en nekrolog er længere end det. Med brugerens eget abonnement kan man læse det, man får,
finde et genkendeligt ord i højre ende — også et forvansket et — og søge på dét. Så flytter
vinduet sig frem.

En nekrolog giver typisk den dødes stilling, uddannelse, karriereforløb og flytninger med
årstal, og nævner ofte ægtefælle og børn — mere personalhistorie end nogen dødsannonce.

**2. Billedviseren kan ikke styres udefra — og den henter kun en lavopløst side.**
Sidebilledet ligger som en `blob:`-URL på 768 x 1075 punkter; det er for lidt til at læse
petit. Viserens egne zoomknapper (`aria-label="Zoom ind"`) reagerer ikke pålideligt på
programmerede klik, og `computer`-værktøjets `zoom` arbejder i et andet koordinatsystem end
viserens lærred. Der findes en **«Download PDF»**-knap, som formentlig giver fuld opløsning,
men en filhentning skal brugeren selv sætte i gang.

**Konsekvens:** brug søgningen til at finde og læse teksten, og notér dato, sektion og
sidetal, så siden kan slås op i hånden bagefter. Det er hurtigere end at kæmpe med viseren.

**Og husk 140-års-grænsen gælder ikke her.** Mediestream giver kun avis, dato og side for
udgivelser yngre end 140 år. Politikens eget e-avisarkiv giver **søgbar fuldtekst helt frem
til i dag** — det er derfor den eneste vej til dødsannoncer og nekrologer fra 1900-tallet.


**3. Søgningen dækker fjorten titler, ikke kun Politiken.**
Udelader man `title=`-parameteren helt, sætter siden selv denne liste ind:

    title=2669,4863,4819,4865,3501,4821,3503,4823,4871,4873,5581,6027,6097,4747

Det er hele JP/Politikens Hus' arkiv. `title=2669` alene er Politiken. **Søg bredt først**
— en dødsannonce kan være rykket i et andet af husets blade — og snævr ind bagefter.


---

## Flere kilder, der er værd at kende

### Danskerbasen — 6,8 millioner danskere født 1583-1968

> **LUKKET FOR FRI SØGNING (efterprøvet sept. 2026),** både i browseren og med `curl`:
> **både `/danskerbasen/` og `/search/` svarer nu med en server-302 til
> kontooprettelse.** Den frie søgning, der er beskrevet nedenfor, virker ikke længere.
> **AI-assistenten opretter ikke konti** — vil brugeren bruge basen, skal vedkommende selv oprette en. Beskrivelsen
> står, fordi feltnavnene og dækningstallene stadig gælder, hvis adgangen kommer tilbage.

Den ligger **inde i Danish Family Search**, men er en anden base end kirkebogssøgningen:

    https://www.danishfamilysearch.dk/danskerbasen/

**6.800.213 indtastede personer, født mellem 1583 og 1968.** Siden oplyser selv, at den dækker
**55,86 procent af alle fødte** i perioden. Det er væsentligt mere end kirkebogssøgningen, og
den bør derfor være det **andet** sted, man leder, når en person ikke kan findes.

**Felter:** fornavn, efternavn, fødselsdag, fødeår fra/til, samt amt, herred og sogn.
Feltnavnene er enkle, uden `searchfields`-mellemlag:

    ctl00_ContentPlaceHolder1_txt_firstname
    ctl00_ContentPlaceHolder1_txt_lastname
    ctl00_ContentPlaceHolder1_txt_borndayfrom
    ctl00_ContentPlaceHolder1_txt_bornyearfrom
    ctl00_ContentPlaceHolder1_txt_bornyearto

Søgningen fyres af med det sædvanlige greb:

    __doPostBack('ctl00$ContentPlaceHolder1$btn_search','')

**Der er også personsider**, `/danskerbasen/personNNNNNN`, med forældre, biografi, tidslinje,
billeder og familietræ. De er brugerbyggede og ofte tomme — med «Fader ukendt» og «Moder
ukendt». **Resultatlistens rækker linker ikke til dem**; person-id'erne
dukker derimod op som links i den almindelige kirkebogssøgnings resultater.

### Statstidende fra 2001 — dødsboernes proklama (`arkiv\stat.py`)

Appens eget endepunkt, læst ud af browserens netværksfane:

```
GET https://www.statstidende.dk/api/messagesearch?t=<fritekst>&page=0&ps=25&o=40
```

> **FRITEKSTFELTET HEDDER `t`, IKKE `q`.** Med `q` svarer serveren med **hele registret** —
> 367.175 meddelelser — og ser fuldstændig ud som et vellykket opslag. Det er den værste
> slags fejl, for den ligner et svar. **Efterprøv altid på et navn, du ved findes.**

Et proklama bærer navn, dødsdato og retskreds. Dækningen begynder midt i 2001.

**Et nul betyder ikke, at personen lever.** Et bo, der afsluttes som **boudlæg** eller
**uskiftet bo**, bekendtgøres aldrig — og det er netop et bo med en efterlevende ægtefælle,
der oftest gør det. Kirkegårdsregistret (`gravsted.py`) er uafhængigt af skifteretten og
fanger dem, proklamaet aldrig nævner: en person kan stå i kirkegårdsregistret, selv om
dødsregistret slet ikke kender vedkommende.

**CPR-numre står åbent i svaret.** `stat.py` maskerer dem; de må hverken vises, gemmes eller
skrives i træet.

### Hullet i kirkegårdsregistret: FREDERIKSBERG er slet ikke med

`findgravsted.dk` dækker **Folkekirkens fælles** kirkegårdssystem, og det er ikke det samme
som alle danske kirkegårde. **Frederiksbergs kirkegårde — Solbjerg Parkkirkegård og
Frederiksberg Ældre Kirkegård — er kommunale og står ikke i registret.** Blandt de 1.756
kirkegårde er der ikke én med en Frederiksberg-adresse (efterprøvet sept. 2026).

**Et nul fra `foedtden.py` eller `gravsted.py` siger derfor intet om en frederiksberger.**
Det samme gælder enhver anden kommunal eller privat kirkegård, et ryddet gravsted og en urne
spredt over havet. Vejen er kommunens egen kirkegårdsforvaltning.

### Autorisationsregistret — og hvorfor et nul dér intet betyder

`autregweb.stps.dk/da/searchResults?quickSearch=<navn>` giver fornavn, efternavn,
fødselsdato og faggruppe for danske sundhedspersoner. **Men en dansk autorisation bortfalder
ved det fyldte 75. år**, og registret viser kun gyldige autorisationer — enhver, der er født
før ca. 1951, er usynlig. Søgningen er desuden uskarp: et kort efternavn på fire bogstaver giver snesevis af træf
på navne, der kun afviger med ét bogstav.

### Kraks Vejviser 1770-1969 — hele København, ikke kun de fine (`arkiv\krak.py`)

Københavns Biblioteker har scannet hele rækken og lagt den på FlippingBook
(`user-9y8ca5x.cld.bz/Kraks-Vejviser-<år>-<del>/<side>/`). **Hver sides HTML bærer
OCR-fuldteksten** i `<div class="full-text">`, så den kan søges maskinelt.

```
python arkiv\krak.py --find 1963 gaderegister <gadenavn>   # binærsøg på sidehovedet
python arkiv\krak.py --side 1963 gaderegister <side>       # hele sidens OCR
python arkiv\krak.py --scan 1963 navneregister <fra> <til> "<fornavn> <initial>"
```

**Delene hedder ikke det samme hvert år:** 1960-1967 har `gaderegister`, 1969 har
`husregister`. Prøv begge.

**GADEREGISTRET ER OFTEST DEN HURTIGE VEJ.** Kender man adressen, står hele husstanden —
etage for etage, med stilling og telefonnummer — på én side. Kender man kun navnet, er
navneregistret en nål i en høstak: **en stor slægts indførsler er ordnet efter STILLING**,
ikke efter fornavn (en stor navneblok løber over mange sider i rækkefølgen *Gross.*,
*Kt.chef*, *Lektor*, *Prok.*, *Tandl.* osv.). Uden at kende stillingen kan en Nielsen ikke
slås op.

**Fælden i sidehovedet:** hovedet står spatieret (`H A N S`, `T R A N - T R I P`), men det
gør linjen `N A V N E - R E G . f. K Ø B E N H A V N O G O M E G N` også. Sorteres den ikke
fra, læser binærsøgningen «NAVNE» på hver side og lander altid på den sidste. Personregistret
dækker også **Frederiksberg og Gentofte**.

**Krak er ikke et folkeregister** — det er husstandsoverhoveder, næringsdrivende og
telefonabonnenter. Et manglende træf beviser intet i sig selv, og OCR'en er rå.

### Kraks Blå Bog-registret 1910-1988 — hvem der overhovedet har en biografi

    https://runeberg.org/blaabog/1988reg/

**Register over 15.229 personer**, digitaliseret af Projekt Runeberg. Hver linje er:

> efternavn · fornavn · titel · fødselsdato - dødsdato · **sidste årgang, personen stod i**

Det er en glimrende **kontrolkilde**: to datoer på dagen og en officiel titel, for enhver, der
har været nogen i Danmark. Og det fortæller, om det overhovedet kan betale sig at gå på
bibliotek efter selve artiklen.

**Selve biografierne er kun frit tilgængelige for 1910 og 1937** (Runeberg), og Erik Rosekamps
scanninger for LFL's Bladfond rækker ligeledes kun til 1910. Alt derefter skal læses i en trykt
årgang.

**Blå Bogs biografi oplyser fast:** forældrenes navne og stillinger, uddannelse, hele
karriereforløbet, ægteskabet med hustruens fulde navn OG hendes forældre, og bopælen. Nogle
årgange nævner også børnene. **For en slægtsforsker er det en af de rigeste enkeltkilder, der
findes** — og den er ofte overset, fordi den ikke ligner et arkivalie.

### Og et kirkegårds-id

`findgravsted.brandsoft.dk` virker, men listens søgefelt filtrerer ikke ved programmeret
indtastning. Find navnet direkte i DOM'en og klik på det; adressen bliver
`/kirkegaard/<ID>/BSK`, hvor id'et er et ottecifret tal. Kendte id'er kan skrives ind i
`gravsted.py`, så de ikke skal findes igen.


---

## To ting, folketællingsindekset hos Danish Family Search kan, som man let overser

**1. Resultatlisten har en fødested-kolonne.** Man behøver ikke åbne husstanden for at få et
fødested — søgeresultatet viser det. Én søgning på to fornavne + efternavn kan give et par
linjer, der alle peger på samme by i udlandet eller i hertugdømmerne — og dermed flytte en
familie fra ét land til et andet i træet.

**2. Stillingsrubrikken skelner mellem «hendes» og «deres».** Står der *«deres Barn»*, er begge
forældre i husstanden; står der *«hendes døtre»*, er faderen væk. Skal der vælges mellem
flere træf på den samme kvinde, kan det ene ord pege på den rigtige tælling — den, hvor
faderen stadig var hjemme.

**Og en advarsel om indtastningerne:** de er indtastninger, ikke afskrifter. En folketælling
kan fx være tastet ind som *«Mette Dorthea Eksempelsen født Xxxrup ?»* — **med spørgsmålstegn**,
fordi indtasteren ikke kunne læse navnet, mens en tidligere tælling giver et helt andet
pigenavn. Skriv aldrig et
indtastet navn med spørgsmålstegn ind i træet som en kendsgerning; skriv det som et problem,
der skal løses.


---

## Kirkegårdsregistret (findgravsted.brandsoft.dk) — hele Danmark på fire minutter

Brandsofts kirkegårdssystem dækker **1.754 danske kirkegårde** i Folkekirkens fælles system.
Siden er en JavaScript-app, men den hviler på to enkle POST-endepunkter, der kan kaldes direkte.
**Parametrene står i klartekst i sidens egen bundle, `/js/266.*.js`** (efterprøvet sept. 2026).
Svarer et opslag 500, så læs dem dér, før du gætter.

```
POST /bsk_app/Bsk_wsfindgravsted_pck.SoegKirkegaard      → JSON
     InKlientHttp, InSoegeStr, InKirkegaardId, InAfdelingId, InLat, InLng

POST /bsk_app/bsk_wsoffentlig_pck.AfdoedeSoeg            → XML
     InKlientHttp, InDBSID, InKirkegaardID, InSoegekriterie, InIndex, InAntalHits, …
```

**De to endepunkter staver det ikke ens:** `InKirkegaardId` med lille d i det første,
`InKirkegaardID` med stort i det andet. Hold dem adskilt.

`InKlientHttp` må gerne være et tilfældigt GUID på 32 hex-tegn **uden bindestreger** — serveren
kontrollerer det ikke, men svarer 500 på uuid-formen med bindestreger.

### Tre ting, der ikke står nogen steder

* **Tom `InSoegeStr` giver alle 1.754 kirkegårde i ét kald.** Ingen paginering.
* **Tom `InSoegekriterie` giver hele kirkegården**, ikke nul. `InIndex` sider igennem,
  `InAntalHits` mindst 500 ad gangen.
* Derfor kan **en hel kirkegård tømmes og filtreres på `GRAVSTED_NR`** — og det er den eneste
  måde at se, **hvem der ellers ligger i samme grav**. Søgningen selv kan kun navne.

Felterne pr. afdød: `FORNAVNE`, `AKT_EFTERNAVN`, `DATO_FODT`, `DATO_DOD`, `GRAVSTED_NR`,
`GRAVSTED_ID`, `KIRKEGAARD_ID`, `KIRKEGAARD_NAVN`, `GPS_KOORDINAT_LAT/LNG`. **Koordinaten «-1»
betyder fællesgrav** — ingen individuel plads.

### Hvad det koster

En landsdækkende fejning efter ét efternavn: **1.754 kald, ca. fire minutter, ingen fejl.**
`gravsted.py --alle <efternavn>`.

> **Tempo og vilkår.** Serveren er Folkekirkens, ikke din. Brug `gravsted.py` og
> `foedtden.py` til personlig slægtsforskning, hold lav hastighed med pause mellem
> kaldene, og respektér sidens vilkår. `--alle`, `hel_kirkegaard()` og en landsfejning i
> `foedtden.py` er tunge greb — prøv altid én kirkegård (`--kgd`) først, og fej kun hele
> landet, når spørgsmålet ikke kan afgøres på anden måde.

### Hvad det IKKE dækker

**Frederiksberg og Gentofte kommuner er ikke med** — de driver deres egne kirkegårde uden for
Folkekirkens system. Til gengæld **er** Københavns kommunale kirkegårde med, blandt andre Vestre,
Assistens, Bispebjerg, Sundby, Holmens, Garnisons og Vor Frelsers. I alt 59 kirkegårde i
postnummerområdet 1000-2990.

> **Et gravsted er en slægtstavle.** Gravstedsnummeret binder mennesker sammen, som intet andet
> offentligt register binder sammen — og det rækker helt op i nutiden, hvor kirkebøger,
> folketællinger og indekser for længst er holdt op.


---

## Hvor langt rækker kirkebøgerne — og hvad der er sløret

Prøvet på to store forstadssogne (efterprøvet sept. 2026).

### Rækkevidden

| Bogtype | Sidste digitaliserede bind |
|---|---|
| **Viede** | det ene sogn til ca. **1960**, det andet til ca. **1963** |
| **Fødte** | begge til ca. **1960-61** |
| **Døde** | begge op i **1960'erne** |

**Grænsen ligger omkring 1960-63 og er ikke den samme for hvert sogn.** Det ene sogns
vielsesbog rakte tre år længere frem end det andets. **Kontrollér altid det enkelte sogn med `bind2.py`,
før du konkluderer, at noget «ikke kan nås».**

Efter grænsen findes der **ingen** maskinel vej: personregistrene er elektroniske og lukkede,
Danskerbasen er en fødselsdatabase for 1583-1968 med 55,86 % dækning, og Danish Family Searchs
kirkebogsindeks er meget tyndt for hovedstadsområdet efter 1946.

### Sløringen

Rigsarkivet **slører dele af de nyeste opslag**:

> *«Oplysninger er sløret af databeskyttelseshensyn. Du kan søge om adgang til oplysningerne via
> Rigsarkivets hjemmeside.»*

I praksis lægges et hvidt felt hen over de yderste rubrikker — anmærkninger og en del af
fadderne. **Navnekolonnen og forældrekolonnen er åbne.** En fejning efter et efternavn kan
altså sagtens lade sig gøre.

> **Sløring er ikke et hul i samlingen.** Et manglende billede kan man lede efter andetsteds;
> en sløring er arkivets egen afgørelse om nulevende menneskers oplysninger, og den skal stå.
> **Skriv i kildenoten, at der VAR sløret** — så ved den næste, at noget er udeladt med vilje
> og ikke ved en fejl.

### Hvad en fejning koster

Med `ark.py` og den smalleste kolonne, der afgør sagen:

| Bog | Opslag | Poster | Kontaktark | Tid |
|---|---|---|---|---|
| Vielsesbog | 216 | ~850 | 36 (6 opslag/ark) | ca. 25 min |
| Fødselsbog | 225 | ~1.100 | 29 (8 opslag/ark) | ca. 20 min |

**Brudgommens navn alene:** `0.075 0.245 0.17 1.0`, seks opslag per ark.
**«Barnets fulde navn» alene:** `0.238 0.342 0.19 1.0`, otte opslag per ark.
Begge skaleret til 1900 punkter i bredden. Under det bliver håndskriften utydelig.


---

## Kirkebogsindekset hos Danish Family Search — fire ting, der virker

Fire greb, der kan få en slægt til at vokse fra en håndfuld kendte personer til en hel
familie på få timer.

### 1. Søg på det SJÆLDNESTE FORNAVN, ikke på efternavnet

Et almindeligt efternavn i en købstad over et par årtier giver **så mange træf, at loftet
nås**. Et sjældent dobbelt fornavn fra samme søskendeflok giver **en håndfuld**, og
dåben er som regel blandt dem.

I en søskendeflok deler alle efternavnet, men ét af børnene har altid et navn, ingen andre har.
Find det i folketællingen, og søg på det alene — så falder hele familiens sogn på plads med ét
opslag.

**Prøv navnet i den stavemåde, KILDEN bruger, ikke den dit træ bruger.** «Detlev» kan
give nul, mens **«Ditlev»** giver dåben med det samme. Prøv systematisk vokalerne, de
dobbelte konsonanter, -ph-/-f- og C/K/Z: Detlev/Ditlev, Bartholomæus/Bartolomeus,
Josephine/Josefine, Zacharias/Sakarias.

### 2. Tre slags links, tre slags materiale

| Linkform | Hvad det er |
|---|---|
| `/kbid<N>` | **fuld indtastning** — hele indførslen som tekst, inkl. forældre og faddere |
| `/churchbook/sogn<S>/churchlisting<L>/opslag<O>` | **kun en scanning** — skal læses med øjnene |
| `/cid<N>` | folketællingshusstand, indtastet |

### 3. Når DFS' egen scanning mangler, ligger billedet hos Rigsarkivet

DFS hoster en del scanninger selv på
`https://filedn.eu/lxUb0Tww4FLXaQb4oa0WB3k/ch/<sogn>/<listing>/<opslag>.jpg` — men **ikke alle**.
Giver den 404, så **åbn churchbook-siden i browseren og læs `img`-kilden**: den peger på
`https://api.rigsarkivet.dk/ao/v1/images/<billed-id>`, som kan hentes direkte.

### 4. Indekset dækker meget ujævnt — kontrollér før du konkluderer

* **Fødte i ét københavnsk sogn** kan være fuldt indtastede for en årgang (`kbid`-links),
  mens nabosognets fødte fra samme årti **kun findes som scanninger**.
* **Konfirmerede i en købstad** kan mangle helt for nogle årgange og først begynde nogle år
  senere.
* **Vielser i København 1855-1864** er stort set ikke indtastede.
* Til gengæld findes **et maskinskrevet vielsesregister for hele staden**, scannet ind sammen med
  Trinitatis Sogns bøger: én linje per par med brudgommens fag, begges alder, dato og løbenummer.
  Det er ofte nok til at datere en vielse uden at finde selve indførslen.

> **Et nul i indekset betyder kun noget, hvis man har kontrolleret, at årgangen og sognet
> overhovedet er indtastet.** Tjek med en kontrolsøgning på et almindeligt navn i samme sogn og år.


## Københavns Stadsarkivs Solr — hele samlingslisten, og den, ingen havde set

`solr.kbharkiv.dk/solr/apacs_core/select` er åben og kræver hverken nøgle eller login.
Facetteres der på `collection_id`, er listen kortere og mere oplysende, end grænsefladen
antyder. **I alt 2.793.824 poster (efterprøvet sept. 2026):**

| id | Samling | Poster |
|---|---|---|
| 17 | Politiets registerblade 1890-1923 | 1.965.257 |
| 1 | Begravelsesprotokoller | 619.509 |
| **10** | **Borgerlige vielser** | **143.499** |
| 150 | Folkeregisterkort | 51.568 |
| 19 | Politiets efterretninger | 9.033 |
| 18 | Erindringer | 3.322 |
| 5 | Begravelsesprotokoller (lille rest) | 1.636 |

**Samling 10, borgerlige vielser, stod ikke i `kbh.py` og kommer ikke med i en almindelig
søgning.** Grænsefladen søger som standard kun i 1, 17, 18 og 19. Både 10 og 150 skal
skrives frem med `collection_id:` i selve forespørgslen.

Vielsesposterne har egne felter: `marriage_date`, `role` («Brud»/«Brudgom»), `civilstatus`,
`birthplace_free`, `residence_free` — og **tre trosfelter**: `current_denomination`,
`former_denomination` og `children_denomination`. Det sidste er guld ved blandede ægteskaber,
for parret skulle skriftligt erklære, i hvilken tro børnene skulle opdrages.

> **Rækkevidden er skæv, og det er vigtigere end tallet.** Bindet 1851-1875 er kun taget med
> i udpluk: hele vinduet **1851-1870 rummer 314 poster**, mens 1900-tallet er tæt.
> **Et nul før 1875 beviser derfor ingenting.** Dertil kommer, at borgerlig vielse først blev
> mulig i 1851 og længe mest blev brugt af dem, der *ikke* kunne vies i folkekirken.

### Begravelsesprotokollerne er bedre, end de ser ud

Samling 1 rækker fra 1805 til ind i 1900-tallet og giver på én post: `dateOfDeath`,
`ageYears`, `deathcauses` på latin, `deathplace`, `cemetary`, `addresses`, `civilstatus` —
og for gifte kvinder og børn **mandens eller faderens erhverv** i `positions`. Feltet
`comments` rummer tit et direkte AO-link til dødsattesten.

**Det er den hurtigste vej til et dødsfald i København mellem folketællingerne**, og den
slår kirkebogssweep hver gang: et dødsfald, der kun er indkredset til et årti, kan findes
på få minutter.

To forbehold. `comments` kan rumme en krydshenvisning af formen **«Se også nummer 847»**,
som peger på et andet løbenummer i samme bind — og det nummer er ikke nødvendigvis
indtastet, så henvisningen kan kun følges på den skannede side. Og **Assistens Kirkegård er
ikke med i gravstedsregistret** hos Brancheforeningen for Begravelseskultur, hvor de
kommunale kirkegårde ellers kan slås op, så et gravsted herfra kan ikke stedfæstes.


## Skifter i Arkivalieronline — og hvorfor København ikke er, hvor man leder

**Skifter ligger i to helt adskilte grene af Arkivalieronline, og den geografiske gren er
den ufuldstændige.**

### Den geografiske gren (samling 18) — bedrager

`geosoeg.py <navn> 18` og `bindsam.py <NgId> 18` søger i **samling 18, «Skifter, hele
landet»**. For «København, Staden» giver den **fireogtredive arkiver** — det ser
udtømmende ud. Men de er **godser, birk, amtstuer og provstier i oplandet**:
Amager Birk, Benzonsdal Gods, Københavns Universitets Gods, Vartov Hospitals Gods,
Sokkelund Herreds Provsti og så videre. **Den eneste egentlige skifteret er «Københavns
Byret, Skifteretten», hvis ældste bind er fra 1861.**

**Staden Københavns egne skifter fra før 1861 er slet ikke i den gren.**

### Den anden gren (tema 30) — her er de

```
python arkiv/aoandre.py "https://arkivalieronline.rigsarkivet.dk/da/collection/theme/30"
```

Tema 30 er «Skifter» og har fire indgange:

| Indgang | Sti |
|---|---|
| Skiftemateriale, Sønderjylland | `/da/geo/geo-collection/49` |
| **Skifter fra København** | **`/da/other/other-collection/16`** |
| Skifter, hele landet | `/da/geo/geo-collection/18` |
| Skifter, militære | `/da/other/other-collection/83` |

### Hvad «Skifter fra København» faktisk rummer

Fire arkivskabere, og **de dækker ikke det hele**:

| Arkivskaber | Periode | Bemærkning |
|---|---|---|
| **Hofretten** | 1676-1771 | skiftebreve, konceptskifter, skifte- og værgemålsdokumenter, samfrændeskifter, kommissionsskifter |
| **Borgretten** | 1682-1780 | skiftesessionsprotokol 1743-1780 **med alfabetisk navneregister** (kun 9 opslag, bsid 343971) |
| **Inkvisitionskommissionen** | 1773-1844 | justitsprotokol — en **kriminalret**, ikke en skifteret |
| Frederiksberg, Nordre og Søndre Birk | 1800-1937 | skifteprotokoller og registre |

> **HULLET ER 1771-1810, OG DET ER STORT.** Hofretten blev nedlagt i 1771. Skifter efter
> almindelige københavnske borgere gik derefter til **Hof- og Stadsretten**, og **den er
> ikke på Arkivalieronline.** Borgretten dækker godt nok 1777 — men dens navneregister
> viser, hvem den var til for: «Hofskildrer», «kgl. Løsvognskusk», «Berider», «Kusk hos
> Generalkrigskommissæren», «Pensionist». **Borgretten var kongens tjenestefolks ret.**

**Praktisk følge:** et skifte efter en københavnsk håndværker eller arbejdsmand mellem
**1771 og 1810** kan **ikke** findes maskinelt. Det kræver Rigsarkivets arkivdatabase
Daisy og en bestilling.

**Og til gengæld:** er den døde en af kongens folk, eller er året før 1771, ligger skiftet
frit tilgængeligt — og Borgrettens navneregister er så lille, at det kan læses helt igennem
på ni billeder.


## Fem ting, der ændrer hvordan man læser

### 1. Koppevaccinationens dato er en personlig markør — brug den

**Koppevaccination blev lovpligtig i Danmark i 1810**, og attesten fulgte personen livet
igennem. Den skulle fremvises **ved konfirmation**, **ved vielse** og **ved flytning mellem
sogne** — og præsten skrev datoen ind hver gang.

> **Det betyder, at den samme person står med samme vaccinationsdato i tre forskellige
> protokoller.** To identiske datoer binder to indførsler sammen langt stærkere end et navn.

**Sådan virker det i praksis (opdigtet eksempel):** en pige konfirmeret i et sogn i
Thy i 1823 og en kvinde med samme patronym, men en anden stavemåde af fornavnet, viet i
et nabosogn i 1836, har begge samme vaccinationsdato. **Samme dag, samme år.** Det afgør en
identitet, som navn og fødselsår alene kun gør sandsynlig.

**Rubrikken hedder «Naar og af hvem vaccineret»** og står yderst til højre i
konfirmationsprotokollerne. **Lægens navn står der også** — ofte den samme distriktslæge
i hundredvis af indførsler, hvilket i sig selv stedfæster vaccinationen.

**Se altid efter den rubrik, når to personer skal identificeres som én.**

### 2. En dødsattests fødselsdato er de efterladtes hukommelse — kontrollér den altid

Attester kan have fejl i datoen. Et opdigtet eksempel: en dødsattest angiver fødselsdagen
**21/3 1867**, mens kirkebogen har **21. januar 1867** — ét ciffer, skrevet mange år efter
fødslen af nogen, der ikke var til stede. Står der tilfældigvis et andet barn med samme
efternavn på den forkerte dato, kan man tage en fremmed ind i slægten.

> **Regel: en fødselsdato fra en dødsattest skal altid kontrolleres mod en kilde fra
> personens egen levetid.** **Folketællingerne fra 1901 og frem er det billigste sted** — de
> opgiver fuld fødselsdato, og personen har selv oplyst den.

**Til gengæld er dødsattestens FØDESTED guld.** Fødestedsrubrikken kan løse en oprindelse,
som ingen anden kilde giver.

### 3. Arkiveringsstedet er ikke hændelsesstedet

**Dødsattester er arkiveret under LÆGEKREDSEN**, ikke under dødsstedet. En attest kan
ligge under en købstad, selv om personen døde og blev begravet i et landsogn et helt andet
sted i lægekredsen.

**Det kan sende en eftersøgning gennem alle købstadens kirkebøger og nabosognets uden at
personen kan findes.** Slå dødsstedet op på selve attesten, og søg begravelsen dér.

### 4. Sogne uden egne kirkebøger — og bøger med spring

* **Nogle landsogne omkring en købstad har ingen egne kirkebøger før et bestemt år.** Deres
  fødsler står da i **købstadsognets** bøger. **Folketællingerne skelner mellem de to sogne;
  kirkebøgerne gør det ikke.**
* **`opslagid.py` melder «SPRING ved N opslag», og i et bind med spring holder
  `billed_id = grundtal + opslag` IKKE.** Et gammelt bind kan have flere spring.
  **Kalibrér da direkte på billed-id:** `gkasse.py 0 <id1>,<id2>,…` — med grundtal **0**
  bliver «opslagsnummeret» selve billed-id'et.
* **Kirkebøgerne nummererer efter DÅBSÅRET, ikke fødselsåret.** Et barn født 22. december
  1837 og døbt 6. januar 1838 står som **1838 nr. 3**. **Læs derfor altid ind i det følgende
  års numre**, når fødslen ligger sent på året.

### 5. Og to praktiske ting om værktøjerne

**Dansk Demografisk Databases gamle søgeformular på `ddd.dda.dk` er ændret**; et script, der
poster til den, får menusiden tilbage og melder nul rækker på enhver søgning, også brede (se
afsnittet om DDD længere nede — `ddd5.py` bruger det nye endepunkt).
**Folketællingerne kan også fejes direkte på Arkivalieronline** — eller søges gennem
**Danish Family Search**, som viser DDA's egne indtastninger med kildehenvisning
(`DDA-nummer`, `kipnr.`).

> **Men pas på:** DFS/DDA's viste post **gengiver ikke alle rubrikker**. I ét tilfælde manglede
> **fødestederne** helt i indtastningen — og det var netop dem, der åbnede den næste
> generation. **Læs originalsiden, når en post skal bære en slutning.**

**`gkasse.py` har fået `--kontrast`**, som strækker gråtonerne med
`ImageOps.autocontrast(cutoff=2)`. **Folketællingerne 1845 og 1850 er mikrofilmet i gråt på
gråt og ser ulæselige ud, indtil kontrasten strækkes.** Prøv aldrig at opskalere en svag
scanning — over ca. 1:1 bliver blæk til grød; stræk kontrasten i stedet.


---

## Tre kildeklasser, der let overses

### 1. Rytterdistrikternes fæstebreve — og de omskrevne fra før 1700

**Arkivalieronlines samling 55 hedder «Fæsteprotokoller og -breve»**, og den er ikke nævnt
andetsteds i denne fil. `geosoeg.py <ord> 55` søger i den, og
`bindsam.py <NgId> 55` lister bindene. Et rytterdistrikt ligger typisk under samme NgId, som
dets skifter ligger under i samling 18.

> **Forordningen af 23. juni 1719 bød alle fæstere indsende deres fæstebreve til
> omskrivning.** Derfor kan et rytterdistrikts bind med «omskrevne fæstebreve» rumme
> afskrifter af breve, der er **ældre end 1719 — helt tilbage til 1670'erne**. **Det er en
> pre-1700-kilde, der navngiver fæstere.**

**Hvad man skal vide om serierne:**

* **Fæstere og selvejeres adkomster** er ofte løse, stemplede fæstebreve, ikke et register.
  **Uden navneregister er de svære at søge i** — man må bladre.
* **De omskrevne fæstebreve** er også løse breve på kongeligt stemplet papir. **Håndskriften
  er vanskelig og papiret ofte revet.**
* **Fortegnelsen over rytterdistriktets fæstere (1721)** er en linjeret liste ordnet efter
  sogn og by, med nummererede gårde, fæsterens navn og hartkorn i fire kolonner — **men den
  er ikke nødvendigvis fuldstændig.** Et sogn kan have ganske få indførsler under én by,
  mens flere af sognets andre landsbyer slet ikke står der. Læs overskrifterne opslag for
  opslag, og se efter, hvor bogen slutter (et blankt opslag).

> **Rytterdistrikternes skifter og fæstebreve er sjældent uddraget af nogen.** Erik Brejls
> amtssider rummer som regel ikke rytterdistrikternes egne protokoller — et nul dér siger
> intet om en rytterbonde.

### 2. «Aabenbare afløste» — kilden, der navngiver uægte børns fædre

**Mange kirkebøger fra slutningen af 1600-tallet har et særskilt afsnit**, som ikke står i
nogen oversigt: **de offentligt afløste**.

Det er kvinder, der gjorde **kirkebod for lejermål** — og indførslen navngiver **den
udlagte barnefader**. Formlen er gennemgående:

> «… blef **N.N.** af [sted] **aabenbare afløst**, **som udlagde til barnefader** [navn] …»

En typisk indførsel (opdigtet, men i kildens form):

> «d. **14 Octobr:** blef **[kvindens navn]** aff **[landsby]** aabenbaer afløst, som
> **udlagd til barnfader en Soldat [navn]**, som hun tiente med hos **[gårdmand]**.»

**Se hvad den ene indførsel giver:** kvindens navn og landsby, **faderens navn og stilling**,
og **hvis tjeneste de var i, da det skete.** En dåbsindførsel havde givet ordet «uægte» og
intet andet. Samme side kan have en kvinde, der udlagde **«en Karl aff samme Byen»** som
barnefader.

> **For uægte børn i de år er det ofte den kilde, der giver faderens navn** — og tit hans
> stilling, hans kompagni og hvor parret tjente. **Dåbslisten skriver som regel kun
> «uægte».**

**Afsnitsrækkefølgen i et sådant bind** er værd at kende, for den kan forklare et hul.
Afsnittene står ikke nødvendigvis kronologisk: copulerede, begravede og afløste kan komme
først og de døbte bagest, tilbage til bindets ældste år. **Standser vielseslisten midt i et
år, og begynder næste bog først nogle år senere, er der et hul i rækken** — og en vielse i
de år findes da kun som **forloverattest**, hvis den findes. **Det er ikke en forbigåelse;
det er et hul i rækken.**

**Og begravelseslisten i sådanne bind kan være enestående rig for sin tid:** den kan give
**både begravelsesdag og dødsdag, ofte klokketimen, og alderen i år, måneder, uger og dage**
— undertiden fødselsdatoen: «som var fød d. 11 Aprilis [år] og død d. 3 Junii».

### 3. Sognehistoriers navneregistre — filtreret på årstal

**En trykt sognehistorie har som regel et navneregister bagest, hvor hver indførsel bærer
et årstal og et gårdnummer.** Det er den hurtigste vej til det, bogen rummer om 1600-tallet
— og det er nemt at overse.

**`reg1700.py <pdf> [fra] [til]`** trækker alle registerlinjer ud, hvis år er **før 1700**.
På en sognehistories register (ca. tyve sider) kan den med det samme give en håndfuld
linjer om én gård spredt over 1500- og 1600-tallet — **nok til at åbne flere nye slægtled.**

> **Husk: registrets sidetal er BOGENS, ikke PDF'ens.** Forskydningen er typisk én side,
> men den kan være større; find afsnittet med `pdfsoeg.py` på et navn fra registerlinjen i
> stedet for at stole på tallet.

**`pdfside.py <pdf> <første> [sidste]`** skriver en PDF's tekstlag ud side for side, når
man først har fundet siden.

### Og en tilføjelse om DDD

**Formularen på `soeg_person.asp` har fået to nye obligatoriske felter** —
`operator=3` («indeholder») og `navnelogik=OR`. Med dem alene **svarer serveren stadig med
nul rækker, også på et kontrolnavn**, fordi resultaterne nu hentes ad en anden vej end selve
POST'en. Løsningen står i afsnittet om DDD nedenfor (`ddd5.py`, `dddperson.py`).


---

## ronlev.dk — et helt bibliotek af danske kildeudgaver, frit som PDF

**En af de største enkeltgevinster i denne fil.**

    https://www.ronlev.dk/kildeskrifter.html

**«Claus Rønlevs bibliotek»** rummer flere hundrede danske kildeudgaver — hele bind,
scannet, med tekstlag, **frit tilgængelige som PDF** på adresser af formen
`ronlev.dk/bibliotek/<nr>.pdf`. Fordelt på fem perioder:

| afdeling | antal værker |
|---|---|
| Sagn og sagaer · Vikingetiden · Middelalderen | — |
| **Renæssancen (1536-1660)** | **118** |
| **Enevælden (1660-1848)** | **196** |
| Nyere tid (efter 1848) | — |

**De kan hentes med `pdfhent.py` og søges med `pdfsoeg.py` og `pdfside.py`** præcis som
slægtsbøgerne. **Et bind på 800 sider tager under et minut at hente.**

### Kancelliets Brevbøger 1551-1660 — komplet

**Alle kongebreve i uddrag, bind for bind.** Det er dér, kongelige udnævnelser,
mageskifter, fritagelser og befalinger står — **og navneregistret bagest i hvert bind gør
dem søgbare på person og sted.**

| årgange | fil | årgange | fil |
|---|---|---|---|
| 1551-1555 | `1615.pdf` | 1603-1608 | `1626.pdf` |
| 1556-1560 | `1616.pdf` | 1609-1615 | `1627.pdf` |
| 1561-1565 | `1617.pdf` | 1616-1620 | `1628.pdf` |
| 1566-1570 | `1618.pdf` | 1621-1623 | `1629.pdf` |
| 1571-1575 | `1619.pdf` | 1624-1626 | `1630.pdf` |
| 1576-1579 | `1620.pdf` | 1627-1629 | `1631.pdf` |
| 1580-1583 | `1621.pdf` | 1630-1632 | `1632.pdf` |
| 1584-1588 | `1622.pdf` | 1633-1634 | `1633.pdf` |
| 1588-1592 | `1623.pdf` | 1635-1636 | `1634.pdf` |
| 1593-1596 | `1624.pdf` | 1637-1639 | `1635.pdf` |
| 1596-1602 | `1625.pdf` | 1640-1641 | `1636.pdf` |

**Derefter ét bind per år eller to:** 1642-43 `1690.pdf` · 1644-45 `1691.pdf` · 1646
`1692.pdf` · 1647 `1693.pdf` · 1648 `1694.pdf` · 1649 `1695.pdf` · 1650 `1696.pdf` · 1651
`1697.pdf` og så fremdeles til 1660.

> **Prøvet og virket:** et bind på omkring 800 sider kan give **kongebreve om navngivne
> bønder** — om bestillinger, fritagelser og stridigheder — og **adelige mageskifter om
> hele landsbyer**, med dato og de involverede parter.

### Kronens Skøder 1535-1765

**Kronens køb og salg af jordegods**, fem bind plus navneregister:

| bind | fil |
|---|---|
| 1535-1648 | `1721.pdf` |
| 1648-1688 | `1722.pdf` |
| 1689-1719 | `1723.pdf` |
| 1720-1730 | `1724.pdf` |
| 1731-1765 | `1725.pdf` |
| **Navneregister** | `1726.pdf` |

> **PAS PÅ, HVAD DE IKKE RUMMER.** Kronens Skøder er **kronens egne handler** — ikke
> bøndernes. **Bøndernes egne skøder — også en bondes køb ved ryttergodsauktionerne i
> 1760'erne — står der ikke.** En søgning på en bondekøbers efternavn giver derfor nul.
>
> **Men bindet giver adressen på de rigtige papirer.** Forkortelseslisten forrest henviser
> til pakker med dokumenter vedrørende salget af de bortauktionerede rytterdistrikter og
> til de skødeprotokoller, hvor bøndernes køb blev ført. **Læs forkortelseslisten, før du
> opgiver bindet.**

### Andre nyttige værker

* **«De danske Landbrug fremstillet af Forarbejderne til Christian V.s Matrikel 1688»**
  (1928) — **`1275.pdf`**, 540 sider. **Statistisk, ikke navngivende:** den opgør gårde,
  huse, hartkorn og tøndeland **by for by og sogn for sogn**, ikke fæster for fæster.
* **«Sønderjydske Skatte- og Jordebøger fra Reformationstiden»** af Falkenstjerne og Hude,
  1895-99 — vejen for egne syd for Kongeåen.
* **«Samling af Kongens Rettertings Domme 1595-1604»** og **1605-1614** af V. A. Secher.
* **«Danske Domme 1375-1662»**, **«Forordninger, Recesser og andre kongelige Breve
  1558-1660»**, **«Aktstykker til Oplysning om Stavnsbaandets Historie»**,
  **«Skifter efter jydske Præster 1665-1685»**, **«Breve og andre Skriftstykker af Ribe
  Stiftsarkiv»**.

### Sådan findes en fil

Katalogsiderne hedder `ronlev.dk/kildeskrifter/<nr>-<periode>.html` (se listen længere nede), og
hvert værk har sin egen side, hvorfra PDF-linket peger på `bibliotek/<nr>.pdf`. **Nummeret
er stabilt** og kan skrives direkte i `pdfhent.py`.

> **Og husk forskydningen.** Bøgernes egne navneregistre henviser til **bogens** sidetal, ikke
> PDF'ens. Forskydningen kan være **+2** i ét bind og **+15** i et andet. **Find altid forskydningen på ét kendt opslag, før du stoler på et
> registertal.**


---

## Dansk Demografisk Database — søgningen er lagt om

*Efterprøvet sept. 2026.*

> **Et script, der poster til den gamle formular, returnerer nul rækker for ALT** — også for
> et navn som «Hansen» i 1845, hvor der findes tusindvis. **Det fejler tavst**, fordi svaret
> er selve søgesiden, og en `<tr>`-læser finder ingen rækker i den.

### Hvad der var sket

* **`soeg_person.asp` poster ikke længere til sig selv.** Søgeknappen er
  `<input type="button" id="btnSearch">` — ikke submit — og siden indlæser
  **`soegpersonudvidetajax.js`**.
* Det rigtige endepunkt er

      POST https://www.ddd.dda.dk/soegpersonudvidetajax.asp?action=search

  med formularen `#formkipfolder` serialiseret som krop.
* Formularen har fået **et nyt felt, `fødested`**, og `county`, `kilde`, `sorter` og
  `sorter2` skal have **rigtige standardværdier** (`alle`, `alle`, `a.navn`, `b.aarfra`),
  ikke tomme strenge.
* **AMT ER OBLIGATORISK.** JavaScriptet nægter selv at søge uden:

      if ($('#ddlCounty').val() == "alle") alert("Venligst vælg Amt");

  **Den avancerede søgning kan altså ikke bruges landsdækkende.** Skal man søge i hele
  landet, må man løbe amterne igennem — eller bruge den simple søgning på
  `soeg_person_enkel.asp`.
* **Svaret er ikke en tabel.** Det er afsnit med etiketterne `Navn:`, `Alder:`,
  `Civilstand:`, `Erhverv:`, `Fødested:`, `Fam.nr:`, `Matr.nr:`, `Stednavn:`, `Sogn:`,
  `Kilde:`, `KIPnr:`, `Lbnr:`.
* **Serveren viser højst 250 poster** og skriver selv «Kun 250 poster vises».

### De nye værktøjer

| script | gør hvad |
|---|---|
| **`ddd5.py`** `<navn> <amt> [år] [--fodested X] [--alder N] [--sogn X]` | søger og lister navn, alder, sogn, fødested, kilde |
| **`dddperson.py`** `<amt> <kipnr> <lbnr>` | **alle felter for én person — OG HELE HUSSTANDEN** |

`dddperson.py` bruger den lille formular, søgesvaret selv rummer:

    POST https://www.ddd.dda.dk/asp/alle_opl.asp
    felter: amt, indtastningsnr (KIP-nummeret), lbnr

**Den giver «Samtlige personer i husstanden» med navn, alder, status, stilling i familien,
erhverv og fødested** — altså hele familien på én forespørgsel. Der er også en knap til
dokumentationen for en hel indtastning: `asp/doku_dk.asp` med feltet `indtastningsnr`.

### Hvorfor det var arbejdet værd

**Databasen kan rette en forkert slutning.** En folketælling, der er gennembladet med øjnene
og erklæret fri for et bestemt efternavn, kan i databasen give flere husstande — fx fordi
tællingen er ført **på tysk**, og en familie er indtastet under en forvansket form af
efternavnet, mens hustruen står under sit eget pigenavn.

> **En folketælling læst med øjnene og en folketælling søgt i en database er to forskellige
> kilder.** Den første misser et navn, der er stavet forkert; den anden finder det, hvis man
> søger på *dele* af navnet.


---

## ronlev.dk — rettelse af katalognumrene, og hvad biblioteket IKKE har

*Efterprøvet sept. 2026.*

**De præcise katalogsider er:**

| side | periode | antal værker |
|---|---|---|
| `kildeskrifter/317-sagn-og-sagaer.html` | Sagn og sagaer | — |
| `kildeskrifter/316-vikingetiden.html` | Vikingetiden (ca. 800-1050) | — |
| **`kildeskrifter/312-middelalderen.html`** | Middelalderen (1050-1536) | **123** |
| **`kildeskrifter/313-renaessancen.html`** | Renæssancen (1536-1660) | **118** |
| **`kildeskrifter/314-enevaelden.html`** | Enevælden (1660-1848) | **195** |
| **`kildeskrifter/315-nyere-tid.html`** | Nyere tid (efter 1848) | **100** |

**I alt 536 værker**, og hvert værk har sin egen side, hvorfra PDF-linket peger på
`bibliotek/<nr>.pdf`.

### Hvad der IKKE er der

**Lensernes jordebøger er stort set ikke med.** En søgning på «jordeb» i hele kataloget
giver kun fire værker:

* «Kong Valdemar den Andens jordebog» af O. Nielsen, 1873 *(middelalderen)*
* «Studier over Kong Valdemars Jordebog» *(middelalderen)*
* «Fru Eline Gøye's Jordebog med tilhørende Brevuddrag» af A. Thiset, 1892 *(middelalderen)*
* **«Sønderjydske Skatte- og Jordebøger fra Reformationstiden»** af Falkenstjerne og Hude
  *(renæssancen)* — kun for egnene **syd** for Kongeåen

> **Et bestemt lens jordebøger, et rytterdistrikts gods og dets fæstebønder står som regel
> ikke i dette bibliotek.** De skal søges i Rigsarkivets egne protokoller — og mange af dem
> er ikke online. Søg på egnens købstad eller herred i titlerne; det tager et minut at se,
> om der er noget.

### Værktøjet

`ronlevsoeg.py <ord> [ord …]` henter de fem katalogsider og lister de værker, hvis titel
indeholder **alle** de givne ord. **Det tager under et minut at afvise et helt bibliotek.**


### DDD: `herred` er det andet døde felt

**`fødested` var kendt som virkningsløst. `herred` er det samme.** En søgning på et efternavn
i et bestemt herred i folketællingen 1860 giver **0 poster** — skønt et sogn i det herred
med sikkerhed har flere husstande med navnet det år.

**Feltet sendes med i formularen, og serveren ignorerer det.** Nullet ligner et svar og er
det ikke.

| felt | virker? | brug |
|---|---|---|
| `county` (amt) | **ja — og det er obligatorisk** | JS'en afviser «alle» med en alert |
| `parish` (sogn) | **ja** | kontrolprøvet: `--sogn <sogn>` med et almindeligt navn som «Hansen» giver træf |
| `herred` | **nej** | sendes, ignoreres |
| `fødested` | **nej** | sendes, ignoreres |

> **Kontrolprøven på kontrolprøven.** Giver `--sogn <sogn>` 0 i flere amter, er det
> nærliggende at slutte, at sognet ikke er indtastet. **Men først skal filteret selv
> efterprøves** — `--sogn <kendt sogn>` på et navn, der med sikkerhed findes. Giver det
> træf, er nullet ægte. **Prøv altid filteret, før du tror på det, det siger.**

**Husstandsvisningen giver til gengæld både amt, herred, sogn og stednavn gratis** i
overskriftslinjen — `dddperson.py`, i formen **«Amt, Herred, Sogn, Stednavn»**. **Find først
personen, så stedet.**


### DDD: `stednavn` er det tredje døde felt

**Prøvet (sept. 2026):** `stednavn=<landsby>` i et amt i 1860 giver
**0 poster** — skønt en husstandsvisning i samme tælling udtrykkeligt har
«<amt>, <herred>, <sogn>, **<landsby>**, Et Hus». **Feltet sendes og ignoreres.**

**Den samlede oversigt ser nu sådan ud:**

| felt | virker? |
|---|---|
| `county` (amt) | **ja — og obligatorisk** |
| `parish` (sogn) | **ja** |
| `navn`, `navn2`, `navnelogik` | **ja** |
| `alder`, `interval` | **ja** |
| `kilde` (år) | **ja**, og `alle` virker |
| `herred` | **nej** |
| `fødested` | **nej** |
| `stednavn` | **nej** |

> **Alle tre døde felter findes i formularen og returnerer 0 uden fejlbesked.** **Et nul fra
> dem betyder intet.** Kontrollér altid et filter på noget, du ved findes, før du tror på det.

**Landsbyer kan altså ikke søges.** Vil man vide, hvor i sognet en husstand lå, skal man
først finde personen på navn og derefter hente husstanden med `dddperson.py` — **stednavnet
står i overskriftslinjen.**

### Bovrup-kartoteket — DNSAP's medlemsliste (Danske Slægtsforskere)

| Hvad | Hvor | Virker |
|---|---|---|
| **Bovrup-kartoteket** | `slaegtsbibliotek.dk/bovrup/BovrupList.php` · værktøj **`arkiv/bovrup.py`** | **✔ VIRKER MASKINELT.** POST med felterne `fulltext`, `enavn`, `fnavn`, `stilling`, `bopael`, `omraade`. Svaret er én tabel: efternavn, fornavn, stilling, bopæl, område, side, fødselsdag, indmeldelsesdato. Højst 200 rækker vises; overskriften siger «… ud af i alt N fundne» |

18.670 personer af listens 22.792. Danske Slægtsforskere har renset basen, tilføjet
fødselsdatoer og efterprøvet, at alle har været døde i mindst ti år; foreningen har
ophavsretten. **Kun navnesammenfald uden fødselsdato er intet** — sammenhold altid
fødselsdato og bopæl med det, man ved om personen, før et træf regnes for et fund.

---

## Wads Sedler, DIS-fora og Slægt & Data (efterprøvet sept. 2026)

Tre kilder, der let overses. **Alle tre kan søges maskinelt**, og to af dem kan give fund,
der kan efterprøves i arkivalierne og skrives i træet.

### Wads Sedler — `sedler.dis-danmark.dk/wad` — **✔ VIRKER MASKINELT**

| | |
|---|---|
| **Navneliste** | `vis_navne.php?page_id=14&stil=1\|2&navn=<ord>&sort=e\|f\|s\|st\|i&ret=12` |
| **Seddel** | `vis_sedler.php?page_id=15&sort=e&vis=2&id_nr=<n>&navn=<Efter+For>` |
| **Billede** | `wad_data/<mappe>/<billednavn>.jpg` — 900 × 548 px |
| **Værktøj** | **`arkiv/wad.py`** |

Landsarkivar **G. L. Wads** sedler 1893-1924, **36.381 indtastede navne**
(basen opdateret 22. februar 2021). `stil=1` er «starter med», `stil=2`
«indeholder»; `sort` vælger register: **e** efternavn · **f** fornavn ·
**s** stednavn · **st** stilling · **i** billed-id. Jokertegn `_` og `%`.
**Kun navnene er indtastet** — seddelteksten skal læses på fotoet.

**Tre fælder:**

> **`navn` SKAL sendes sammen med `nr`/`id_nr`.** Uden navnet svarer serveren med
> en tilfældig seddel — **altid #384 «Bager»** — uden fejlmelding.

> **`nr` og `id_nr` er to forskellige nøgler.** Navnelisten giver `nr`;
> naboskabssøjlen på en seddelside giver `id_nr`. Byttes de om, får man en
> fremmed seddel — igen uden fejl.

> **Billedserveren kræver samme `Referer` som sedlernes egen visningsside.** Uden den svarer
> serveren 200 med et **1,3 kB pladsholderbillede** i stedet for de rigtige 130 kB.

**Og en genvej:** navnesøjlen på en seddelside **er** det alfabetiske register og
rummer **ét `id_nr` per forekomst**. Har et navn to sedler, står begge dér —
`wad.py`'s `alle_idnr()` bruger det til at hente dem alle.

**Dækningen er fynsk og standsmæssig.** Wad var landsarkivar i **Odense**, og
sedlerne handler om **præster, godsejere, forpagtere og embedsmænd**. En almuefamilie
fra Jylland eller Sjælland står sjældent i dem. **Et nul om en jysk eller sjællandsk
almuefamilie betyder derfor intet.**

**Inden for sin kreds er den derimod præcis.** Sedlerne om fynske embedsmænd og
præster har ofte **arkivhenvisninger**, som de trykte slægtsbøger mangler. En seddel
kan fx se sådan ud (opdigtet):

> «**[Efternavn].** Skifte **[dato og år]** efter **Hr. [navn] i [sogn]**.
> Enken **[navn]**. — *[Herred] g. Skifteprot. [årstal] f. [folio].*»

**Det er sedlernes egentlige værdi:** ikke nye navne, men **folioangivelsen i en
protokol, der ellers skulle bladres igennem.**

### De to slægtsforskerfora — **✔ VIRKER MASKINELT** — `arkiv/disforum.py`

**Det gamle DIS-Forum** (`dis-danmark.dk/forum`) er **Phorum**, lukket for nye
indlæg i 2012 og **stadig læsbart og søgbart**. Alene AneEfterlysning har
**42.036 tråde og 241.757 indlæg**; Hjælp til Tydning 45.491 tråde.

* Søgningen er **to skridt**. `search.php?forum_id=0&search=…` svarer «Din søgning
  er i gang» og et `<meta refresh>` til Phorums komma-form:
  `search.php?0,search=<ord>,page=<n>,match_type=ALL,match_dates=0,match_forum=ALL`.
  **Hent den anden adresse direkte**, ellers får man kun ventesiden.
* **`match_dates` står som standard på 30 dage** — og på et forum, der lukkede i
  2012, giver det **nul uden fejl**. Sæt altid `match_dates=0`.
* **Siderne er windows-1252.** Afkodes de som utf-8, forsvinder æøå.
* **Søgningen er «indeholder» uden ordgrænser.** Et kort efternavn giver
  hundredvis af træf på almindelige ord og stednavne, der rummer de samme
  bogstaver. **Læs titlerne, ikke tallet.**

**Det nye forum** (`forum.slaegt.dk`) er **SMF 2.1** og kan søges af gæster med et
rent GET: `index.php?action=search2&search=<ord>`. **Ingen session, ingen cookie**,
UTF-8. Svaret giver tråd, dato, forfatter, tavle og et uddrag med søgeordet
fremhævet i `<mark class="highlight">`.

> **Et forumindlæg er et SPOR, ikke en kilde.** De fund, der kom ud af dette, var
> alle henvisninger til Arkivalieronline og til Dansk Demografisk Database, som
> derefter blev slået op og læst. **Skriv aldrig et forumindlæg i træet som en
> kendsgerning.**

**Hvad fora kan, som ingen anden kilde kan:** de er ordnet efter **problem**, ikke
efter arkiv. En tråd med en familie og et sogn i titlen kan indeholde præcis den
husstand, man har eftersøgt forgæves i flere amter — fordi en anden slægtsforsker har
stået med det samme spørgsmål og fået svar. **Søg altid slægtens sjældne efternavn sammen med sognet, før en stor
gennemgang sættes i gang.**

### Slægt & Data — **✔ virker, men er et metodeblad**

**118 numre, 1987-1 til 2017-1**, frit tilgængelige som PDF **med tekstlag** via
Slægtsbibliotekets titelliste. Filerne ligger på `dis-danmark.dk/bibliotek/<nr>.pdf`
og `slaegtsbibliotek.dk/<nr>.pdf`; `sbib.py "Sl.gt.*Data"` finder dem alle.
**Hele rækken kan hentes og lægges i én søgbar tekstfil på 11,7 MB (~3.900 sider)
på under fem minutter.**

**Forvent ikke personalhistorie.** Bladet er et **metodetidsskrift**:
programanmeldelser, kursusannoncer, KIP-indtastningsstatus, foreningsstof.
Søgning på en snes sjældne slægtsnavne gav **nul** på dem alle.

**Men medlemmernes egne slægtshistorier står der**, og de er lokalhistorisk
guld, når de rammer ens eget sogn:

* **Artikler om et sogns fattiggård**, som nævner deres kilder: sognerådsprotokoller,
  fattiggårdsprotokoller, journaler i amtet og **politiets fotografiportrætter** fra
  omkring 1900 — en kildegruppe, man sjældent tænker på.
* **Artikler om lokale sognesider** bygget op **om bebyggelsesenheder og
  matrikelnumre**, med personalhistorie for hver ejendom. Et forbillede for, hvad
  lokale sognesider kan rumme.
* **1992-3 og 1991-3:** KIP-oversigterne fortæller, hvilke sogne og årgange der
  er indtastet.

**Sådan søges hele rækken:** hent PDF'erne én gang, træk tekstlaget ud med
`pypdf`, og skriv én linje per side i en fælles fil med bladets navn og sidetal
foran. **Derefter er 3.900 siders årgange et `grep`.**


## Riksarkivet i Sverige — kyrkoböcker og folkräkningar

**Frit materiale kan hentes maskinelt.** `arkiv\riksark.py` henter scannede svenske
kirkebøger over IIIF; billedserveren kræver samme Referer som arkivets egen fremviser
(`Referer: https://sok.riksarkivet.se/`). **Søgetjenesten er ALTCHA-beskyttet og bruges ikke
maskinelt** — opslagene i trin 1-3 herunder gør brugeren selv i browseren.

### Fra sognenavn til billed-id, i fire skridt

```
sok.riksarkivet.se/kyrkoarkiv?Arkivsok=<sogn>&AvanceradSok=True      -> referencekode SE/LLA/nnnnn
…&Arkiv=SE%2fLLA%2fnnnnn&tab=serie                                   -> alle bind med serie og år
   hver række har et link /bildvisning/<guid>
GET på det link omdirigerer til /bildvisning/<8 cifre>               -> BILLED-ID'ET
https://lbiiif.riksarkivet.se/arkis!<billedid>_<5 cifre>/info.json   -> manifest per opslag
```

Billed-id'et er det, `riksark.py` skal have. `arkiv\bid.py`-mønstret (følg omdirigeringen og
læs sidste led af URL'en) klarer oversættelsen fra guid.

### Hvad der er frit, og hvad der ikke er

**Kirkebøgerne er frie langt op i 1900-tallet** — en fødselsbog **1914-1959** kan læses
i fuld opløsning. **Men ikke alle bind:** församlingsböcker efter 1910 og flyttningslängder
efter 1916 svarer **HTTP 401** på IIIF, også med Referer. **Manifestet svarer altid**, så
`manifest` er ikke et bevis på adgang — prøv et opslag.

> **Omdirigeringen afslører det på forhånd.** Er et bind spærret, ender guid-linket på
> `/login?returnUrl=%2Fbildvisning%2F<id>` i stedet for på selve id'et. Så er bindet ikke
> frit, og det hentes ikke.

### Fælder

| | |
|---|---|
| **Fødselsårsfilteret ignoreres** | `FodelsearFran`/`FodelsearTill` og `Fodelseland` bliver stille lagt til side i folkräkningar-søgningen. Svaret ser afgrænset ud, men er det ikke. **Tæl træffene efter årstal, før du tror på et nul.** |
| **Sognenavnet skal være moderne** | Et sogn, som den gamle kirkebog staver anderledes (fx med et stumt H foran), giver **nul** under den gamle form; databasen bruger den moderne stavemåde. Kirkebogens egen stavemåde er ikke søgestrengen. |
| **Opslag 3-5 er tryksager** | Bøger trykt efter 1910 indledes med ministeriets regler og et **mønstereksempel med opdigtede navne og et fremmed sognenavn**. Det ligner et forkert bind. Titelbladet kommer bagefter. |
| **IIIF opskalerer ikke** | `/full/2000,/` på et udsnit, der kun er 1464 px bredt, giver **HTTP 400**. Klip den ønskede bredde til udsnittets egen. |
| **Første opslag er omslaget** | Bogens side 1 er opslag 2. Ryggens etiket fotograferes med og siger, hvilket bind man har fat i. |

### Vigselregister, Födelseregister og Dödregister dækker kun dele af landet

**Vigselregistret** dækker Blekinge, Gotland, Jämtland, Kristianstad, **Malmöhus** og
Västernorrland — og selv dér ikke alle sogne. Et nul betyder «ikke indtastet», ikke «ikke
viet»: en vielse kan stå i kirkebogen uden at stå **i registret**.
**Födelseregistret** dækker seks län og langt fra alle årgange. Gå til bindet.

### Folkräkningarnas husstandsvisning er gratis og fuldstændig

Et klik på et træf giver **hele husstanden med navn, fødeår og fødesogn for hver person**,
plus hemort, kontrakt, län, yrke, civilstånd og familiestilling. **Det er den billigste vej til
en hel svensk familie** — og søgningen kan bære på *fornavn + hemförsamling* alene, hvilket er
afgørende, når det netop er efternavnet, man leder efter.

**Post-id'et i adressen (`postid=Folk_<nummer>`) er stabilt** og kan skrives i en kilde.


### Hvad der typisk er frit og spærret i et svensk kyrkoarkiv (efterprøvet sept. 2026)

| bindtype | åbent? |
|---|---|
| Födelse- och dopböcker til langt op i 1900-tallet | **åbent** |
| Lysnings- och vigselböcker fra omkring 1900 | **åbent** |
| Inflyttnings- og utflyttningsböcker før ca. 1914 | **åbent** |
| Utflyttningslängder fra ca. 1914-1916 og frem | **spærret, 401** |
| Församlingsböcker efter 1910 | **kræver login** (guid-linket omdirigeres til /login) |

**Spærringen falder omkring 1914-1916 for de bøger, der rummer personlige oplysninger om flytninger;
fødsler og vielser er frie langt op i 1900-tallet.** Det er ikke en regel, man kan udlede af
bindtitlen: prøv et opslag i hvert bind, før du opgiver.

**Er udrejsen spærret, så find INDrejsen.** Den ligger i det samme bind som det, man ved hvor
personen kom til — og en indflytningsbok giver *hvorfra* (ofte sognet eller bydelen, ikke bare byen),
*hvorhen* i sognet (gårdnavn og nummer) og *hvilken side* i församlingsboken.

**Hemvistnummeret er et gårdnummer, og det binder indførsler sammen på tværs af år.** «N:o 12» i en
dåbsindførsel 1862 og «Hemmanet N:o 12» i en anden 1865 er samme gård og dermed samme familie —
stærkere end et navn, som i Sverige er et patronym og ændrer sig fra generation til generation.
