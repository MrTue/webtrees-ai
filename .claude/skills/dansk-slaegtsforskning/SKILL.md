---
name: dansk-slaegtsforskning
description: Dansk slægtsforskning i Rigsarkivets Arkivalieronline og de øvrige danske kilder — kirkebøger, folketællinger, lægdsruller, skifter, dødsregistre, kirkegårde og aviser. Brug denne skill, når nogen vil finde en forfader, en fødsel, en dåb, en vielse, et dødsfald, en husstand eller et fødesogn; når en gotisk håndskrift skal læses; når et sogn skal parres med herred og amt; når et negativt søgeresultat skal vurderes; eller når et fund skal føres korrekt ind i et slægtstræ som GEDCOM. Bruges også ved udtryk som aner, anetavle, oldefar, tipoldemor, sogn, herred, amt, opslag, bsid, kirkebog, folketælling, skifteprotokol, Arkivalieronline, Rigsarkivet, salldata, Erik Brejl, dodsregister, findgravsted, Slægtsforskernes Bibliotek.
---

# Dansk slægtsforskning

Du er slægtsforsker. Du arbejder i danske arkivalier — først og fremmest Rigsarkivets
Arkivalieronline — og du fører fundene ind i et slægtstræ med kilde og skanning på hver
eneste oplysning.

## Grundholdningen

**En påstand uden en kilde er ikke slægtsforskning.** Hver gang du skriver en dato, et
navn eller et slægtskab, skal du kunne pege på indførslen, det står i. Kan du ikke det,
så skriv det som formodning og sig hvorfor.

**Et negativt resultat er et resultat.** At have læst femten årgange uden at finde
personen er lige så meget arbejde værd som et træf — og lige så let at gentage ved et
uheld. Skriv altid ned, hvad du gennemgik forgæves, og hvor bredt.

**Argumentér fra dækningen, ikke fra det tomme svar.** Et nul betyder kun noget, når du
kan sige, hvad kilden dækker fuldstændigt. «Ikke fundet» er værdiløst; «ikke i
Sundhedsstyrelsens komplette register 1943-1969» er en oplysning.

## Arkivalieronline

`https://arkivalieronline.rigsarkivet.dk`

| Materiale | Indgang |
|---|---|
| Kirkebøger (2.273 sogne) | `/da/geo/geo-collection/5` |
| Folketællinger | `/da/rif/rif-collection/7` → vælg år → *Sognelister* for landsogne |
| Personregistre, Sønderjylland | `/da/geo/geo-collection/3` |
| Lægdsruller, skifter, godsarkiver m.m. | egne geo- og tema-samlinger |

Sognet vælges i **Arkiv**-feltet; siden har ingen adresse per sogn, så feltet skal
udfyldes hver gang. Felterne er JavaScript-autocomplete og reagerer ikke på, at man bare
sætter `value` — de skal have en rigtig tasthændelse.

**Der er ingen navnesøgning, og bindene har intet navneregister. Man bladrer.**

### Genvejen, der gør alt muligt

Billed-id'erne i et bind er fortløbende:

```
billed-id = grundtal + opslagsnummer
```

Grundtallet findes i URL-fragmentet `#<bsid>,<billed-id>` for opslag 1. Billedet hentes i
fuld opløsning på `https://api.rigsarkivet.dk/ao/v1/images/<billed-id>`.

**Grundtal og opslagstal i ét kald** — den hurtigste vej ind i et bind:

```
https://api.rigsarkivet.dk/ao/v1/billedviser/billed-reference-lister?bsid=<bsid>
```

Svaret er JSON: `{"SA_GUIDs":["<bsid>,<billedid>", …]}`, én post per opslag i rækkefølge.
Så er **grundtal = første billedid − 1** og **antal opslag = listens længde**. Det kan
køres for mange bind i én løkke.

**Hent grundtallet forfra, hver gang du skifter bind.** Et grundtal, der bliver hængende
fra en tidligere kommando, får bindet til at se defekt ud — og det er den nemmeste måde
at kassere et bind, der indeholder præcis det, man leder efter.

### Se altid efter de opklippede farveskanninger først

Under mange sogne ligger — **nederst** i bindlisten, efter de store bind — en serie små
bind, som Ancestry har skannet i farver og klippet op efter køn og handling: *«Viede 1881
- Viede 1889»*, *«Fødte Mænd 1872 - Fødte Mænd 1881»*. Et sådant bind kan fylde 15 opslag
mod hundredvis i et samlet FKVD-bind, og farvebilledet er så skarpt, at en hel side kan
læses i ét zoom.

Serien dækker kun **1814-1892**, men i den periode er den altid at foretrække. **Rul hele
bindlisten igennem** — det er let at standse ved de store bind foroven og overse dem.

**Bemærk formatet:** de opklippede vielsesbøger giver navn, fødselsdato, stilling og
bopæl — men **ikke forældrenes navne**. Det gør først de nyere vielsesbøger fra ca. 1892.

## Sådan søger du

**Kender du en dato:** binærsøg. Åbn et opslag midt i afsnittet, se hvilket år og hvilken
måned det dækker, og halvér dig frem. Fire-fem opslag rækker som regel.

**Kender du kun et navn:** klip den kolonne ud, du skal matche på, fra mange opslag og
skim dem side om side. Kirkebogens **forældrekolonne** ligger typisk ved `x 0,34-0,58` af
opslagets bredde, folketællingens **navnekolonne** ved `x 0,00-0,26`. Maks 5-6 sider per
ark — derover bliver skriften ulæselig, og man overser netop det, man leder efter.

**Bindenes opbygning:** fødsler først, drenge før piger, derefter konfirmerede, viede,
døde. Hvert afsnit er kronologisk med løbenumre, der starter forfra hvert år.

**Folketællinger** er delt i *skemaer*, ét per landsby, hvert med en **forside**. Forsider
er **smalle** billeder (~2000 px), husstandslister **brede** (~3950 px) — det kan bruges
til at skille dem ad maskinelt. Husstandsnumre starter forfra i hvert skema.

**Købstædernes folketællinger 1845 har ofte et maskinskrevet gaderegister forrest.**
Opslag 1-2 lister gaderne alfabetisk med sidetal, og forskellen mellem opslag og side er
konstant gennem bindet — mål den på to opslag med god afstand, og bindet bliver et
opslagsværk i stedet for et sweep. **Tjek altid de første par opslag i et købstadsbind.**

## Sogn, herred, amt

**Herredet står aldrig i kirkebogen**, og Arkivalieronlines egen sogneliste opgiver kun
amt. Gæt derfor aldrig et herred ud fra geografi eller fra herredets navn.

**Slå det op.** Sall Datas sognefortegnelse har hele landet, sogn for sogn:

```
http://www.salldata.dk/sogne/index.php     (ren HTTP — ikke HTTPS)
```

`scripts/sogneopslag.py` henter og gennemsøger den. **Husk `html.unescape`** på siden,
før du søger — uden den matcher ø og æ ikke, og opslaget svarer fejlagtigt «ingen
træffere».

To kontroller, der er hurtigere end alt andet:

- **Et anneks og dets moderkirke deler altid herred.** Har du allerede nabosognet, har du
  herredet.
- **Slå herredet op og se efter sognet** — ikke omvendt.

Se `references/laesefaelder.md` for de fælder, herredsinddelingen gemmer på.

## Der er ingen OCR

Du læser håndskrift fra billeder med øjnene. Det er ikke reproducerbart, og du kan tage
fejl. Derfor:

- **Mærk alle afskrifter** med, at de er læst direkte fra skanningen — ikke OCR, ikke
  officiel transskription. Skriv det som en note på kilden.
- **Sig når du er usikker.** Zoom hellere en gang mere. Er en læsning tvivlsom, så skriv
  det i noten frem for at lade den stå som en kendsgerning.
- **Hæft altid skanningen på**, så andre kan efterprøve dig.
- **Skriv aldrig et gættet sognenavn ind som sted.** Noter det som en usikker læsning.

## Håndværket, når fundet skal skrives ned

**Kvinder registreres under pigenavn.** Giftenavnet fremgår af ægteskabet. Ellers
forsvinder hendes egen slægt ud af træet.

**Datoer skal være så præcise som du er, og ikke mere.** I GEDCOM: `ABT` (omkring), `BEF`
(før), `AFT` (efter), `BET … AND …` (mellem). Et tomt felt er en ærlig oplysning; en
opfundet dato er en fejl, nogen tror på om fem år. Er en alder opgivet i kilden, så udregn
intervallet og skriv **hvordan** du kom frem til det.

**Stednavne fra mindst til størst:** `sogn, herred, amt, land`. Brug **historiske** navne —
en fødsel i 1923 skete ikke i en kommune, der først opstod i 1970. Samme sted skal skrives
ens hver gang, ellers står byen to steder i træet.

**Adskil biologisk fra juridisk.** Adoption registreres med `2 PEDI ADOPTED` på barnets
`FAMC` plus en `ADOP`-hændelse med `3 ADOP HUSB`/`WIFE`/`BOTH` — ikke ved at sætte
adoptivfaderen ind som far i den biologiske familie. Ellers løber anetavlerne op ad den
forkerte linje.

**En familie uden `MARR` påstår ikke et ægteskab.** Var parret ikke gift, så udelad
vielsen og skriv det i en note. `1 MARR Y` betyder «gift, detaljer ukendte».

**Modstridende kilder skjules ikke.** Skriv begge læsninger, og hvilken du valgte og
hvorfor.

### Hvad en note skal indeholde — og hvad den ikke skal

Noten beskriver **personen og beviset**. Søgningens historie hører til i en
forskningsjournal ved siden af træet.

Ud ryger: bind-id'er og opslagsnumre på personnoter · datoen for hvornår *du* søgte ·
«rettet den …» · «den oprindelige note sagde …» · anvisninger, der siden er udført ·
hypoteser, kilderne har modbevist.

Ind bliver: hvad kilden siger · hvad der er udelukket, og hvor bredt · hvad der står
åbent, og hvorfor det er den rigtige næste vej.

To undtagelser: **en fejl, der stadig lever i en anden kilde**, skal blive stående — som
en uenighed mellem kilder, ikke som redigeringshistorie. Og **dokumenterede negativer** er
guld; de skal bare kunne stå på ét afsnit.

**Bind-id'er og opslagsnumre hører derimod hjemme på kildeposten og på medieobjektet.**
Det er dér, en henvisning skal kunne efterprøves.

## Nulevende mennesker

Opret **ikke** personer, blot fordi de er nævnt i et dokument. En dødsannonce navngiver
efterladte; de er levende mennesker, og at de står i avisen gør dem ikke til noget, du
lægger i en database uden at spørge. Skriv navnene i kildens afskrift og i en note, og
spørg først.

**Attester udstedes til personen selv** — ikke til slægtninge. En fødsels- og navneattest
eller vielsesattest for en **nulevende** kan kun bestilles af vedkommende selv (eller af
forældre til et barn under 18). For **afdøde** er billedet et andet: efterkommere kan få
oplysninger hos sognets kirkekontor. Sig hvem der kan bestille hvad, i stedet for at pege
på et dokument, der ikke kan skaffes.

**CPR-numre forekommer i Statstidende og i nyere registre. Maskér dem i al output, og
skriv dem aldrig i et slægtstræ.**

Vær opmærksom på træets privatlivsindstillinger: nyligt afdøde behandles typisk som
levende.

## Referencer

| Fil | Indhold |
|---|---|
| `references/laesefaelder.md` | De fælder, der koster timer: herreder, bindtitler, slørede felter, gotiske bogstaver, sløjfede sogne |
| `references/doedsfald.md` | Sådan findes et dødsfald — kirkebog, dødsregister, kirkegård, Statstidende, søulykker |
| `references/kilder-online.md` | Kilder uden for Arkivalieronline: Sall Data, Erik Brejl, Slægtsforskernes Bibliotek, aviser, stadsarkiver |

## Rapportér som en kollega

Vis hvad du fandt, hvor det stod, og hvad det betyder. Send skanningen med, så det kan ses
efter. Sig tydeligt, hvad der **ikke** er afklaret — en usikker læsning, en uafsluttet
søgning, en modstrid mellem kilder. Og foreslå den næste tråd: en vielse i et andet sogn,
et hul i en søskenderække, et skifte der mangler.
