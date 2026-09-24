# webtrees_klient — jobs

`webtrees_klient.py` opretter poster i webtrees ved at sende de samme formularer som
browseren. Den logger ind som en redaktørbruger (fx `ai`) (Redaktør med automatisk godkendelse).

## Login-fil (oprettes af dig, aldrig af AI-assistenten)

`%USERPROFILE%\.webtrees\login.json` (fx `C:\Users\<dig>\.webtrees\login.json`):

```json
{"base_url": "http://din-nas.dit-tailnet.ts.net:8081", "tree": "aner", "username": "ai", "password": "…"}
```

Filen må **ikke** ligge på NAS-sharet (det monterede netværksdrev) eller i projektmappen —
begge kommer typisk med i backuppen. Scriptet nægter at
læse den derfra. Kodeordet maskeres i al output.

## Kommandoer

```
python webtrees_klient.py --check                          # kun login + rettigheder
python webtrees_klient.py --dry-run poster\job.json        # vis præcis hvad der sendes
python webtrees_klient.py poster\job.json                  # kør
python webtrees_klient.py poster\job.json --verbose        # vis hvert HTTP-kald undervejs
python webtrees_klient.py poster\job.json --set KILDE=S12  # spring en allerede oprettet op over
```

Hver kørsel skriver `job.result.json` (id → xref) og én linje per op i `log.jsonl`. Stopper ved
første fejl; genkør med `--set` for de ops, der allerede lykkedes.

## Jobformat

```json
{"ops": [
  {"id": "KILDE", "op": "create-source", "title": "…", "abbreviation": "…", "author": "…", "publication": "…", "text": "…"},
  {"id": "MOR",   "op": "add-parent", "child": "X6", "lines": ["1 SEX F", "1 NAME Karen Marie /Eksempelsen/", "1 BIRT", "2 DATE 4 FEB 1921", "2 SOUR @KILDE@"]},
  {"id": "FAR",   "op": "add-parent", "child": "@MOR@", "lines": ["1 SEX M", "1 NAME Anders Peter /Eksempelsen/"]},
  {"id": "MORMOR","op": "add-spouse-to-family", "family": "@FAR.FAMS@", "lines": ["1 SEX F", "1 NAME Maren /Prøvesdatter/"]}
]}
```

Et komplet, opdigtet job — kilde, person med fødsel og dåb, far og mor — ligger i
`poster/eksempel.json`. Prøv `python webtrees_klient.py --dry-run poster\eksempel.json`;
tørkørslen logger ikke ind og sender intet.

| op | peger på | opretter |
|---|---|---|
| `create-source` | – | kilde; `@ID@` bliver `@S12@` i `2 SOUR` |
| `add-unlinked` | – | person uden relationer |
| `add-parent` | `child` (xref) | ny person **og ny familie** med barnet |
| `add-spouse-to-family` | `family` (xref) | ny person som HUSB/WIFE i eksisterende familie |
| `add-child` | `family` | ny person som barn |
| `add-spouse` | `individual` | ny person + ny familie med vedkommende |
| `add-fact` | `target` | tilføjer én hændelse til eksisterende post |
| `link-child-to-family` | `child` (xref) | **opretter intet** — kæder en eksisterende person ind i en eksisterende familie som barn |

**To forældre til én person:** `add-parent` for den første, derefter `add-spouse-to-family`
med `@FØRSTE.FAMS@` for den anden. `add-parent` to gange giver **to** familier.

**Alle `add-*`-ops opretter NYE poster.** Skal en person, der allerede findes, hæftes på en
familie som barn, er der **to** veje, og de sender nøjagtig den samme formular:

```json
{"id": "K1", "op": "link-child-to-family", "child": "X234", "family": "X567", "pedi": ""}
```

Op'en tager **ingen `lines`** — den kæder kun to poster sammen — og `pedi` lades tom for et
biologisk barn (`BIRTH`, `ADOPTED`, `FOSTER`, `SEALING`, `RADA` er de øvrige). Resultatfilen
får barnets eget xref tilbage, for der oprettes intet nyt. **Brug op'en, når kædningen hører
med til en større registrering**, så den havner i `poster/log.jsonl` sammen med resten.

**Til ét enkelt klik uden jobfil** er det enklere at bruge værktøjet — det viser
familiens medlemmer først og efterprøver `FAMC` bagefter:

```
python ..\arkiv\haeftbarn.py <barn-xref> <familie-xref> [PEDI] [--gør]
```

Uden `--gør` viser den kun, hvad der ville blive sendt. `PEDI` lades tom for et biologisk
barn. Bag kulisserne er det `POST /tree/<træ>/link-child-to-family/<xref>` med felterne
`famid` og `PEDI`; der findes tilsvarende ruter `link-spouse-to-individual` og
`link-family-to-individual`, som endnu ikke er pakket ind i et værktøj.

Linjer er GEDCOM: `"niveau TAG værdi"`. Person-ops kræver præcis én `1 SEX` og en `1 NAME`.
`@ID@` erstattes med xref fra en tidligere op; `@ID.FAMS@` / `@ID.FAMC@` slås op i webtrees.

## Find et xref

Åbn personen i webtrees og læs adressen: `…/tree/aner/individual/`**`X6`**`/Anders-Eksempelsen`.
Familier: `…/family/`**`X12`**.

Det kan betale sig at notere de xref'er, man bruger hele tiden — dig selv, dine forældre og
de hyppigst citerede kilder — i projektets egne noter, så et job kan skrives uden opslag.

## Rette en eksisterende kendsgerning

`add-fact` **tilføjer**. Skal noget rettes, bruges `edit-fact`, som udpeger den
kendsgerning, der skal erstattes, ved dens første linje:

```json
{"id": "FOEDSEL", "op": "edit-fact", "target": "X123", "match": "1 BIRT",
 "lines": ["1 BIRT", "2 DATE 2 MAY 1908", "2 PLAC …", "2 SOUR @KILDE@"]}
```

`match` skal ramme **præcis én** kendsgerning — rammer den nul eller flere, stopper
klienten uden at sende noget. Er der to navne på personen, så gør match mere præcis:
`"1 NAME Carl"` frem for `"1 NAME"`.

**`match` er ikke begrænset til første linje.** `find_fact_id` bruger `startswith` på hele
kendsgerningens tekst, så et **flerlinjet** match skiller to ens hændelser ad:

```json
{"op": "edit-fact", "target": "X456", "match": "1 DEAT\n2 DATE BEF 4 FEB 1931", "lines": ["1 NOTE …"]}
```

Det er vejen til at fjerne en kendsgerning, som en kilde siden har overhalet: `lines` behøver
ikke bevare tagget, så en løs `1 DEAT` kan skrives om til en `1 NOTE` med det, kilderne
faktisk siger. Noten skriver det rigtige, ikke at der før stod noget forkert; selve rettelsen
og grunden til den hører hjemme i journalen (se `AGENTS.md`).

`lines` **erstatter hele kendsgerningen**, ikke kun de linjer der nævnes. Alt der skal
bevares, skal skrives med — også kildecitater. Er alle værdier tomme, ville webtrees
slette kendsgerningen; det nægter klienten at gøre.

## Medieobjekter (scanninger)

`create-media` **uploader ikke** — den peger på en fil, der allerede ligger i webtrees'
mediemappe. Læg filen der først, fx over SMB:

```
\\din-nas\docker\webtrees\data\media\kirkeboger\1919-eksempelsogn-...-opslag-35.jpg
```

og angiv så stien *relativt til `data/media/`*:

```json
{"id": "SCAN", "op": "create-media",
 "file": "kirkeboger/1919-eksempelsogn-kirkebog-fodte-kvindekon-opslag-35.jpg",
 "title": "Eksempel Sogn, kontraministerialbog 1918–1927, opslag 35",
 "type": "manuscript",
 "note": "Rigsarkivet, Arkivalieronline, bsid 123456, opslag 35"}
```

Findes filen ikke på serveren, svarer webtrees ikke med JSON, og klienten fejler med
en besked om netop det.

**Filnavne:** årstal først, små bogstaver, ingen mellemrum, ingen æøå — navnet indgår i
en URL og lever i backuppen i mange år. Mapper: `attester/`, `billeder/`, `boger/`, `dodsannoncer/`, `folketaellinger/`, `kirkeboger/`.

`boger/` er til hele trykte værker som PDF. De hænger ikke på et menneske, men på
en **kilde** — og en kilde er en post i træet på lige fod, så den kan bære sit eget
`1 OBJE`. Filnavnet bærer Slægtsbibliotekets nummer i stedet for et årstal, fordi
værkerne sjældent har et kendt udgivelsesår, men altid har et bibliotekssnummer.

### Hvad ligger hvor — og hvad ligger ikke to steder

| Sted | Indhold |
|---|---|
| `\\din-nas\docker\webtrees\data\media\` | **Alt, der hænger på en person i træet.** Ikke et valg: medieobjektet gemmer sin sti relativt til denne mappe, og filnavnet må derfor ikke ændres bagefter. |
| `<projektmappe>\dokumenter\` | **Råmateriale, der ikke er et medieobjekt** — hele avissider, slægtsbøger som PDF, scanninger under arbejde. |

> **Ingen fil må ligge begge steder.** Når et udsnit er klippet ud og lagt i
> mediemappen, slettes arbejdskopien. Og en fil må aldrig bære to forskellige navne
> i de to mapper — så kan man ikke se, at det er den samme.
>
> Dobbelte filer opstår let, og ligger de under hvert sit navn, opdager man det
> ikke. Skriv i stedet kæden fra råmateriale til medieobjekt ned i projektets egne
> noter: hvilken hel side udsnittet er klippet af, og hvad udsnittet hedder nu.

**`type`** er GEDCOM-værdien, ikke den danske etiket: `manuscript` (kirkebog, håndskrevet
protokol), `certificate` (attest), `photo`, `document`, `map`, `newspaper`, `tombstone`,
`book`, `electronic`.

**Hæft scanningen på kilden, ikke på personen** — `1 OBJE @SCAN@` på kildeposten. Så følger
billedet med hver eneste gang kilden citeres, uanset hvor mange personer den dækker.

## Sletning

Klienten har med vilje **ingen** slette-funktion. Skal en post væk, gøres det i
webtrees: åbn posten → **redigér** → *Slet*. Slet familier til sidst, så børn og
ægtefæller ikke efterlades med henvisninger til noget, der ikke findes.
