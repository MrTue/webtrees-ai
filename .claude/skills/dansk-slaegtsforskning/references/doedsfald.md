# Dødsfald — sådan finder du dem

Dødsfaldet er ofte det sværeste at finde, fordi det ligger sidst i livet og dermed tit
efter, at familien er flyttet. Rækkefølgen af kilder afhænger helt af årstallet.

## Hvilken kilde, hvornår

| Dødsår | Første valg |
|---|---|
| Før 1943 | Kirkebogens dødsliste i **hjemsognet** |
| 1943-1969 | `dodsregister.dk` — Sundhedsstyrelsens **komplette** register |
| Efter ca. 1970 | `findgravsted.dk`, derefter kirkegårdskontoret |
| Efter 2001 | Statstidendes proklama (kun hvis boet blev skiftet) |

**Slå det landsdækkende register op før kirkebogen, når dødsfaldet ligger efter 1943.**
Fyrre årgange gennemgået i det forkerte sogn koster mere end ét opslag i et register, der
dækker hele landet.

## I kirkebogen

**Dødslisten fører sognets egne folk, uanset hvor de døde.** Indførsler med dødssted
«Sygehuset i …» eller «Rigshospitalet, København» står alligevel i hjemsognets bog.

Finder du ikke personen i det sogn, hvor han sidst boede, betyder det derfor, at **familien
var flyttet** — ikke at han døde i et andet sogn. Så skal flytningen findes først, og
folketællingerne er vejen til den.

## findgravsted.dk

Begravelsesregistrene fra godt 1.700 danske kirkegårde. Intet login. Søg kirkegården frem,
vælg fanen **Begravede**, søg på navn. Hvert træf giver **gravstedsnummer, fulde navn,
fødselsdato og dødsdato**.

**Fødselsdatoen er det, der gør et træf sikkert** — den skal stemme på dagen med kirkebogen,
før navnet må regnes for den rigtige person.

**Gravstedsnummeret er guld værd: søg det op igen for at se, hvem der ellers ligger i
graven.** Familiegravsteder afslører forældre og ægtefæller, som ingen navnesøgning ville
finde.

### To fælder

**Søg på efternavnet alene, og rul HELE listen igennem.** Søgefeltet matcher ikke fornavn
og efternavn tilsammen — et fuldt navn kan give nul, mens efternavnet alene giver
snesevis. Listen er sorteret på **fornavn** og indlæses **30 rækker ad gangen**, så et navn
sent i alfabetet er usynligt, indtil du har rullet videre.

**Registret er ikke en historisk fortegnelse over alle begravede — det er et register over
gravsteder, der stadig består.** Et gravsted fra 1970'erne er nedlagt efter fredningstidens
udløb og dermed ude af registret. Kig på dødsårstallene i en søgning: ligger næsten alle
efter ca. 1985, dækker registret reelt ikke ældre begravelser, og et negativt resultat
betyder ingenting. Kun kirkegårde i Folkekirkens fælles system er med: Frederiksberg og
Gentofte kommuner driver deres egne og mangler, mens Københavns kommunale kirkegårde (Vestre,
Bispebjerg m.fl.) er med. Tjek selv dækningen for den kirkegård, du leder på.

Søgefeltet er en React-komponent, der ikke reagerer på programmatisk `value`-sætning — klik
i feltet og skriv.

## dodsregister.dk

Danske Slægtsforskeres samlede dødsregister slår op i flere kilder på én gang:

- **Sundhedsstyrelsen 1943-1969** — samtlige dødsfald i Danmark
- **Rigsarkivets indtastningsportal 1857-1943** — et udvalg
- **Københavns Stadsarkivs begravelsesprotokoller 1850-1945** — komplette
- **Statstidende m.fl. 1881 og frem**

Søg med så få felter som muligt: fødselsdato + efternavn rækker ofte.

**Fælde: Sundhedsstyrelsens navne (1943-69) er forkortet** til få bogstaver — «KAROLINE
AMALIE» står som «KAR AMA». Søg på de første bogstaver i den periode, ikke det fulde navn.

**Fornavnefeltet finder kun fornavne fra begyndelsen — aldrig mellemnavne.** Leder du efter
en person, familien kalder ved hans **andet** navn («Aage» i «Niels Aage»), så søg i
stedet på efternavn + fødselsårsinterval og skim træfferne. Ellers overser du ham lydløst.

**Siden går i baglås efter nogle søgninger i samme fane.** Efter fire-fem søgninger kan en
søgning, der lige har givet halvtreds træf, begynde at give nul — uden fejlmeddelelse.
Formentlig et ASP.NET-viewstate-problem, ikke IP-blokering: en **ny browserfane** løser det.
**Mistænk aldrig et ægte negativt resultat, før det er bekræftet i en frisk fane.**

## Statstidende

Alle dødsboer bekendtgøres ved proklama med afdødes navn, CPR-nummer og dødsdato. Frit
søgbart fra midten af 2001. Giver også sidste adresse.

Rent API, langt hurtigere end websøgningen:

```
https://www.statstidende.dk/api/messagesearch?t=<søgeord>&ps=100&page=<n>
```

Returnerer JSON med `pageCount`, `resultCount` og `results` (titel, `Dødsdato`,
`Retskreds`, meddelelsesnummer). Fritekst søger med OR — brug `t="ord i anførselstegn"` for
et nøjagtigt udtryk.

**Svarene indeholder fulde CPR-numre. Maskér dem i al output, og skriv dem aldrig i et
slægtstræ.**

## Hvorfor to registre kan svigte samtidig

`dodsregister.dk` og Statstidende hviler efter 1969 på **det samme**: Statstidendes
proklama. Et bo, der afsluttes som **boudlæg** (lille bo) eller **uskiftet bo**,
bekendtgøres aldrig.

**Nul træf i begge betyder derfor ikke, at dødsfaldet ikke fandt sted.** Det er en meget
almindelig situation for en enke eller enkemand, der sad i uskiftet bo. Gå til kirkegården
i stedet — kirkegårdskontoret har den fulde begravelsesprotokol, også for nedlagte
gravsteder.

## Aviserne

**Dødsannoncen navngiver de efterladte** og er derfor en af de bedste kilder til en
søskendeflok og til giftenavne. Se `kilder-online.md` for avisarkiverne.

Danske aviser bragte desuden indtil omkring krigen en **daglig redaktionel
begravelsesliste** for hovedstaden, ordnet efter kirke og kapel, med klokkeslæt efter hvert
navn. Den er ikke betalt af familien, så **alle** begravelser står der. For enhver, der er
begravet i København eller på Frederiksberg før krigen, er der en linje at hente.

## Døde han til søs?

**Dansk Søfarts Bibliotek** har digitaliseret hele rækken af årlige søulykkestatistikker
som PDF **med tekstlag**:

```
https://www.sbib.dk/files/bibliotek/statistik/<årstal>.pdf
```

Hver årgang gennemgår hvert forlis, hver kollision og hvert dødsfald i den danske handels-
og fiskerflåde — med dato, skib, rederiby og henvisning til søforhøret. **De omkomne
navngives** i en anmærkning, ofte med stilling om bord og hjemby.

Det er den rigtige kilde, når familien siger, at nogen «blev væk på havet». En årgang er
60-95 sider; ti årgange kan hentes og gennemsøges på et minut. **Husk at fjerne ordelinger
(`-\s*\n`) før du søger**, ellers glider navne igennem.

**Afgrænsningen:** statistikken dækker skibe under dansk registrering, som indberettede til
ministeriet. Danskere, der sejlede for de allierede under krigen (*udesejlerne*), står i
**Frihedsmuseets base «I allieret tjeneste»** (allieret.natmus.dk). De to supplerer
hinanden — men et skib, der blev **rekvireret af en fremmed magt**, falder uden for dem
begge og kan sejle under et helt andet navn.

## Til sidst

Både dødsregistrene og Statstidende oplyser **dødsdato, ikke dødssted**. Sæt derfor ikke et
sted på `DEAT` på grundlag af dem — kun på `BURI`, hvis kirkegården er kendt.
