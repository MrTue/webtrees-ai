# Kilder uden for Arkivalieronline

Arkivalieronline er originalen, men den har ingen navnesøgning. Ofte har nogen allerede
skrevet materialet af — og så er vejen kortere.

> **Vend rækkefølgen om.** Før du fejer en kirkebog opslag for opslag, så spørg:
> **0)** Har nogen allerede skrevet slægten eller sognet af?
> **1)** Hvilke bind findes overhovedet?
> **2)** Optræder navnet i en indtastet base?
> **3)** *Derefter* originalen — og gem skanningen.
>
> Skanningen er stadig beviset. Men den skal komme til sidst, ikke først.

## Sall Data — et alternativt indeks til hele Arkivalieronline

```
http://ao.salldata.dk/index.php?type=<kategori>&n1=<amt>&n2=<myndighed>
```

Ren HTTP, ingen JavaScript, og den giver **bsid direkte** — hvor Arkivalieronlines egen
navigation kræver flere klik gennem autocomplete-felter.

Otteogtyve kategorier, blandt andre: `kb` (kirkebøger) · `ft` (folketællinger) ·
`personregister` · `borgerlige` · `udvandring` · `notarial` · `faeste` · `borgerskab` ·
`skifter` · `justits` · `laegd` · `stamb` · `flaaden` · `milits` · `matrikel` · `bygning` ·
`tingbog` · `brand` · `gods` · `retsbetjent` · `told` · `rejsende` · `selskaber` · `amt` ·
`kommune` · `medicin`.

Dertil en række opslagsværktøjer:

| Adresse | Indhold |
|---|---|
| `salldata.dk/sogne/` | **Sogn → herred → amt for hele landet.** Uundværlig |
| `salldata.dk/laege/` | Hvilke sogne hører til hvilken lægekreds |
| `salldata.dk/laegd/` | Lægdsrullernes inddeling |
| `salldata.dk/skifter/` | Skifteretternes jurisdiktioner |
| `salldata.dk/matrikel/`, `/ejerlav/` | Matrikel og ejerlav |
| `salldata.dk/gader/` | Gadenavne i købstæderne |
| `salldata.dk/Sted/`, `/Kort/` | Stednavne og kort |

Siderne er HTML-tabeller med **HTML-entiteter** — kør `html.unescape` på teksten, før du
søger i den, ellers matcher ø og æ ikke.

## Erik Brejl — skifteuddrag

`brejl.dk` — knap to hundrede HTML-sider med transskriberede skifteuddrag og tingbøger fra
hele landet, gjort tilgængelige gratis. Et skifte navngiver **samtlige arvinger** og er
derfor den korteste vej til en søskendeflok i 1700-tallet.

Formatet er fast:

| Forkortelse | Betyder |
|---|---|
| `E:` | enke eller enkemand |
| `B:` | børn |
| `FM:` | formynder |
| `LV:` | lavværge |

**Formynderen og lavværgen er slægtninge** — som regel farbror eller morbror. De er ofte
det led, der mangler.

**To fælder:** filnavnene følger ikke herredernes navne (et sogn kan ligge i en fil opkaldt
efter et gods eller et amt), så søg på tværs af alle siderne frem for at gætte filen. Og
**kodningen er blandet** — nogle sider er utf-8, andre windows-1252. Afkod med begge og
vælg den, der giver færrest erstatningstegn:

```python
kand = []
for enc in ("utf-8", "windows-1252"):
    s = raw.decode(enc, "replace")
    kand.append((s.count("�") + s.count("Ã"), s))
tekst = min(kand, key=lambda x: x[0])[1]
```

## Slægtsforskernes Bibliotek

```
slaegtsbibliotek.dk/online-lister/alle-online
slaegtsbibliotek.dk/<nummer>.pdf
dis-danmark.dk/bibliotek/<nummer>.pdf
```

Titusindvis af digitaliserede slægtsbøger, sognehistorier, trykte kirkebogsudgaver og
utrykte slægtsstudier — **som PDF med tekstlag**, altså fuldtekstsøgbare med `pypdf` eller
lignende.

Det er her, man skal se efter, **før** man begynder at bladre i en kirkebog. En trykt
udgave af et sogns kirkebog fra 1600-tallet kan gennemsøges på sekunder og rummer ofte
gårdfortegnelser, nekrologer og præstens egne optegnelser, som slet ikke står i de
almindelige lister.

Værkerne har sjældent et kendt udgivelsesår, men altid et **bibliotekssnummer** — brug det
som det stabile håndtag, når du navngiver en lokal kopi.

## Aviserne

### Mediestream (Det Kgl. Bibliotek)

```
https://labs.statsbiblioteket.dk/labsapi/api/aviser/hits?query=…
```

Årstal skal ind i **selve søgningen** som `py:[1870 TO 1890]`; `startTime`/`endTime`
ignoreres. Flerordsudtryk **skal** i anførselstegn, ellers OR-søges der. Andre felter:
`lplace:<udgivelsessted>`, `familyId`.

Fuldtekst kan kun eksporteres for materiale **ældre end 140 år**.

### Avisernes egne e-arkiver

De store dagblade har egne digitale arkiver bag abonnement, typisk fuldtekstsøgbare fra
1880'erne. De er ofte bedre end Mediestream for nyere stof.

> **Kun den fede navnelinje i en dødsannonce kommer igennem OCR'en.**
>
> Den dødes navn er sat i halvfed antikva i 12-14 punkt og læses rent. De efterladtes
> underskrifter står i kursiv seks punkt og bliver til grød. **Søg derfor på den dødes
> navn, aldrig på de efterladtes** — og læs de efterladte af billedet, ikke af indekset.
>
> Og regn med, at **ø sjældent overlever**: et navn med ø kan give nul træf, mens samme
> navn stavet med o giver tusindvis af irrelevante.

Gamle avissider er skannet i omkring 2560 punkters bredde for hele broadsheetformatet. En
annonce sat i seks punkt ligger derfor på grænsen af det læselige, og et enkelt ciffer i en
dato kan være uafgørligt. Sig det, i stedet for at vælge det pæneste.

For **nyere årgange** har avisernes egne e-arkiver som regel en **artikel-tilstand**, der
giver artiklens rigtige tekst i stedet for OCR. Brug den — afskriften bliver ordret, og det
går hurtigere end at læse skanningen.

### Distriktsaviser findes, men ikke på nettet

Mediestream rummer godt 500 avistitler, og de er de store dagblade. **Lokale ugeaviser og
distriktsblade er stort set ikke digitaliseret.**

> **Et nul i Mediestream betyder derfor ikke, at avisen ikke findes.** Den står på papir i
> Statens Avissamling.

Det Kgl. Bibliotek har en **registrant over distriktsaviser** — 271 sider, aviser fra 1866
og frem, omkring 31.200 bind. For hver titel står årgangene og et **magasinnummer**
(`H-129` og lignende), og det er præcis dét, biblioteket skal bruge ved en kopibestilling:

```
kb.dk/find-materiale/samlinger/avissamlingen/lister/
    liste-over-distriktsaviser/liste-over-distriktsaviser.pdf
```

**Rækkefølgen er ikke alfabetisk** — titlerne står som i «Lokalpressen»s titelregister, så
en avis kan gemme sig under en anden hovedtitel. Registrantens egen vejledning siger det
rent ud: *«Søg og du skal finde!»* Søg på flere stavemåder og på stedets navn. Og fjern
PDF'ens punktlinjer (`\.{3,}`) før du søger i tekstlaget, ellers klæber årstallene sig til
titlen og intet matcher.

**Hvorfor det er umagen værd:** lokalaviserne skrev om almindelige mennesker — skolefester,
foreningsliv, sølvbryllupper, portrætter af folk i kvarteret. Det er stof, de store
dagblade aldrig bragte, og for hvert led efter ca. 1900 er der en distriktsavis, der
dækkede netop den gade.

## Stadsarkiverne

**Københavns Stadsarkiv** har et åbent Solr-endepunkt:

```
https://solr.kbharkiv.dk/solr/apacs_core/select?wt=json&q=…
```

Samlingerne rummer blandt andet politiets registerblade 1890-1923 (knap to millioner
poster), begravelsesprotokoller, borgerlige vielser, folkeregisterkort og politiets
efterretninger.

> **Det, der virkelig virker, er at søge på FØDSELSDATO i stedet for navn:**
> `dateOfBirth:"1846-03-17T00:00:00Z"`. Navne staves forskelligt i hver kilde; en
> fødselsdato gør ikke.

Andre byer har tilsvarende lokalarkiver, mange samlet på **arkiv.dk**, som rummer
fotografier og arkivalier fra hundredvis af lokalhistoriske arkiver. Billeder dér er ofte
beskrevet med navne og årstal, men vær opmærksom på rettighederne.

## Tænk ud af boksen

Når kirkebogen ikke rækker, findes personen ofte i noget helt andet:

- **Ejendom:** matrikelkort, brandforsikringsprotokoller, fæsteprotokoller, skøde- og
  panteprotokoller. En gård kan følges gennem ejere i to hundrede år.
- **Erhverv:** borgerskabsprotokoller (en håndværksmester skulle løse borgerskab i
  købstaden, **og protokollen navngiver som regel hjemstavnen**), lavsarkiver, vejvisere.
- **Bevægelse:** til- og afgangslister i kirkebogen (**de holder op i forskellige sogne på
  forskellige tidspunkter mellem 1875 og 1900 — findes de ikke, er der ingen erstatning**),
  udvandrerprotokoller, lægdsruller.
- **Militær:** lægdsrullerne 1789-1864 rummer **kun landlægder**. Værnepligten hvilede før
  1849 på bondestanden; mænd født i købstæderne blev slet ikke indskrevet. En dreng fra
  landet blev derimod indskrevet i **faderens** lægd og fulgte den rulle hele livet, med
  opholdssted noteret ved hver flytning. **En lægdsrulleindførsel giver faderens navn og
  drengens fødested i samme linje.**
- **Retten:** tingbøger, justitsprotokoller, fattigvæsen, arrestjournaler.
- **Vidner:** faddere, forlovere, formyndere og lavværger er næsten altid slægtninge. En
  fadder, der er rejst hundrede kilometer, er ikke en bekendt.

## Sønderjylland er en arkivgren for sig

Efter Genforeningen i 1920 blev fødsler, vielser og dødsfald i Sønderjylland ført af
**personregisterføreren**, ikke af sognepræsten, og de ligger i en egen samling — ikke i
kirkebogssamlingen. Den, der leder efter en sønderjysk fødsel efter 1920 i kirkebøgerne,
finder ingenting.

**Og enklaverne ligger, hvor man ikke venter:** sogne nord for Kongeåen, der administrativt
hørte under hertugdømmet, er filet under «Slesvig» — også i folketællingerne. Skemaerne er
da **tyske**, og fødestedskolonnen hedder *Geburtsort* med stednavnene i tysk stavemåde.
