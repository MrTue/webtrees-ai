---
name: slaegtsbog
description: Opskrift på at skrive, udvide og sætte en slægtsfortælling som bog-PDF i dette projekt — SLAEGTSHISTORIEN*.md med tegnede slægtstavler (```tavle), billedklip fra webtrees' mediemappe og mdpdf.py --bog. Brug den, når nogen beder om en slægtshistorie, slægtsfortælling, slægtsbog, en ny PDF, en ny tavle, et klip fra en kirkebog eller dødsannonce i fortællingen, eller om at «bygge PDF'en igen».
---

# Slægtsbog — opskriften

Følg trinene i rækkefølge. **Spring ikke kontrollen i trin 7 over**, og gæt aldrig et navn,
et årstal eller en koordinat — alt har et sted, det skal slås op.

Skriv dansk. Python kaldes `python` (eller det, `$env:PYTHON` peger på). Kør kommandoer i PowerShell (bash-heredocs
med backticks går i stykker her). Skriv intet til webtrees; denne opskrift læser kun.

## 0. Hvad der findes i forvejen

| Fil | Rolle |
|---|---|
| `SLAEGTSHISTORIEN.md` | hovedpersonens slægt (proband, fx **X1**) |
| `SLAEGTSHISTORIEN-<navn>.md` | en anden persons slægt, fx en anden grens bog — hver proband sin fil. **Brug den mest ryddelige som forbillede** |
| `arkiv\mdpdf.py` | markdown → PDF. `--bog` giver titelblad, indhold, delsider, sidehoved |
| `arkiv\bogdata.py` | anetavle, børneflokke, mediefiler og **tavle-udkast** ud af `facit.json` |
| `arkiv\klip.py` | finder koordinaterne til et billedklip |
| `byg-pdf.ps1` | bygger hver `SLAEGTSHISTORIEN*.md` i roden til en PDF med samme basisnavn |
| `arkiv\tekstkontrol.py` | ord- og faktakontrol af en omskrevet fortælling mod dens backup |
| `AABNE-SPOERGSMAAL.md` | (lokal, oprettes selv) arbejdslisten over det, der endnu ikke er fundet — hører ikke til i bøgerne |
| `.claude\skills\slaegtsbog\STILARK.md` | **loven for hver sætning i en fortælling** |

En ny fortælling for en anden person hedder `SLAEGTSHISTORIEN-<NAVN>.md`. `byg-pdf.ps1`
finder den selv og bygger `SLAEGTSHISTORIEN-<NAVN>.pdf` ved siden af — der skal ikke rettes
i scriptet.

## 1. Hent råstoffet — fra træet, ikke fra hukommelsen

```
python arkiv\facit.py                                  # frisk facit.json (logger ind; tager et par minutter)
python arkiv\bogdata.py X1 5 | Out-File $env:SLAEGT_ARBEJDSMAPPE\bogdata-X1.txt -Encoding utf8
```

Er `SLAEGT_ARBEJDSMAPPE` ikke sat, så giv stien med `--facit <sti til facit.json>`. Find en
persons xref ved at søge på navnet i `facit.json` (kommandoen står i `AGENTS.md` under «En
hurtig kontrol»).

`bogdata` giver fire afsnit: **1. anetavle** (med tomme pladser), **2. familier** med hele
børneflokken, **3. medier** per ane (kandidater til klip), **4. tavler** som færdige udkast.
**Læs filen, før du skriver en linje.** Kilderne til en oplysning står i træet (kildens
`1 TEXT` er afskriften); slå dem op i `facit.json`, når du skal citere.

## 2. Skelettet

```markdown
# Slægtshistorien — <Navn>s slægt

<!-- forside: media/billeder/<fil>.jpg "klip=…" -->        (valgfri; udelad hellere end at gætte)

Ét afsnit: hvem bogen handler om, hvad den bygger på, hvor langt tilbage den når.

---

## Sådan læses dokumentet          ← kopiér fra en eksisterende fortælling og tilpas eksemplet

## Slægten i korte træk            ← tavlerne fra bogdata, én per bedsteforælder-gren, hver med
                                     en fed etiket over: **Faderens far — Eksempelsen**

# Første del: <sted eller slægtsnavn>
## <en overskrift, der lover en historie — ikke «Generation 4»>
…
# Sidste del: Det, vi ikke ved       ← åbne spørgsmål som tabel: Spørgsmål | Hvor det kan findes
## Om dokumentet
```

- Titlen **skal** være første `# `. Står der ` — ` i den, bliver det efter stregen til
  undertitel på titelbladet; ellers sæt `<!-- undertitel: … -->` på egen linje.
- **`# ` er en «del»** og åbner en ny side med stor titel. Skriv dem `# Første del: Mariager`
  — så bliver «FØRSTE DEL» en lille etiket over «Mariager». Fire til otte dele.
- **`## ` er et kapitel** og kommer i indholdsfortegnelsen. `### ` kun i PDF-bogmærkerne.
- **Nyt stof hører hjemme i den del, det handler om — ikke i bunden af filen.** Alt efter den
  sidste `# ` får dens navn i sidehovedet.

## 3. Sådan skrives teksten

**Stilarket er `STILARK.md` i denne mappe. Læs det helt, før du skriver en linje** — det er
loven for hver sætning, og det er også det, agenter skal have udleveret. I korthed:

1. **Mennesket, ikke jagten.** Intet om, hvordan nogen kom frem til et resultat: ingen
   søgninger, gennemgåede registre, udelukkelser, arkivnavne, «træet», «opslag», «blev
   fundet», «ikke læst på siden», ingen datering af dokumentet, ingen tællinger af databasen.
   Kilden må optræde som en ting i verden — «præsten skrev i margenen», «i avisen stod» —
   aldrig som noget, nogen har slået op. Metoden hører hjemme i `arkiv\README-DA.md`.
2. **Tredje person, datid.** Aldrig «du», «din», «dig», «vi», «jeg». «Anders' mormor», ikke
   «din mormor». Fortælleren er usynlig.
3. **Ingen bokse.** Usikkerhed siges i sætningen: «formentlig», «ingen ved, om …». Det,
   der slet ikke vides, udelades eller nævnes i en bisætning — **aldrig en liste over huller**.
   Blokcitatet (`> `) er kilden selv, aldrig en kommentar.
4. **Scener frem for rækker.** Åbn et kapitel med et sted, en dag, en ting eller et menneske
   i færd med noget. Børnelister og kildesammenligninger opløses i prosa; en tabel bliver kun,
   hvor en stor børneflok skal kunne overskues.
5. **Opfind intet.** Skønlitterært betyder rytme, udvalg og rækkefølge — ikke fiktion. Ikke
   vejr, ikke følelser, ikke replikker. **Og fjern intet menneske og ingen dato.**
6. **De farverige enkeltheder skal med** — patentet på den nye plov, isenkræmmerens annoncer,
   bødeforlægget for krybskytteri. Står de i træet, skal de også stå her.
7. **Fortællingerne er til privat brug** (tilpas reglen, hvis jeres ikke er det): alle, der står
   i træet, må nævnes ved navn, også nulevende. Et spor, som ejeren har markeret som
   ubekræftet — fx en familieoverlevering, ingen kilde bekræfter — står kort og **udbygges ikke**.
8. **Den samtidige kilde slår den senere.** Aldre i dødebøger og folketællinger er skøn —
   skriv «omkring». Er en håndskrift usikker at læse, siges det kort.
9. Citér med `«…»`, fremhæv navne med `**fed**` første gang i et kapitel. `[[X123]]` sættes
   lille og gråt — brug det sparsomt.

**Åbne spørgsmål hører ikke til i bogen.** Det, der endnu ikke er fundet, og vejen til det,
står i `AABNE-SPOERGSMAAL.md` i roden (en lokal fil, som git ikke følger). Hver bog har sit
afsnit dér.

**Bøgerne må ikke blande sig.** Hver `SLAEGTSHISTORIEN*.md` rummer én probands slægtsgrene, og
det skal stå klart, hvilke slægtsnavne og egne der hører til hvilken bog. **Kun probanderne selv
og deres fælles børn nævnes i flere bøger — alle andre kun i én.** Skriv listen over grene per
bog ned (fx øverst i `AABNE-SPOERGSMAAL.md`), før du flytter stof. Ellers ender kapitler om én
grens slægt i en anden grens bog og må flyttes bagefter.

## 4. Slægtstavler — ```` ```tavle ````

Aldrig ASCII-kunst. Én linje per generation, **de ældste øverst**:

```
Far; undertekst ∞ Mor  ||  Far ∞[1853] Mor; undertekst     to par side om side
Søn (1856-1931); rebslager ∞[1882] Datter (1859-1937)       de to pars børn gifter sig
søskende[12 børn, 8 fundet]: A (1883) · ^B (1890) · C       mange søskende i ét felt
børn: Evald (ca. 1917); landbetjent || ^Magna ∞ Olfert      få børn i hver sin boks
Ole Opdigtsen (f. 1949) — Karen (siden 1991)                — er samliv, ∞ er ægteskab
Peder Påfundsen; gårdmand (formodet) <-- femtipoldefar      randnote
```

| Tegn | Betydning |
|---|---|
| `\|\|` | skiller enheder (par eller enkeltpersoner) i samme generation |
| `;` | indleder en undertekst under navnet; flere `;` giver flere linjer |
| `Navn (1852-1917)` | en afsluttende parentes kommer på egen linje under navnet |
| `∞` / `∞[1882]` / `∞[gift 22. oktober 1803]` | ægteskab; tegnes «∞», «∞ 1882», «gift 22. oktober 1803» |
| `—` | samliv (stiplet). **Mellemrum på begge sider** af `∞` og `—` |
| `^` | foran den person, slægtslinjen går **gennem**. Uden `^`: den førstnævnte |
| `søskende[tekst]:` | navne adskilt af ` · `; `^` foran den, linjen fortsætter fra |
| `børn[tekst]:` | enheder adskilt af `\|\|`; `^` på den enhed, næste linje nedstammer fra |
| `<-- tekst` | randnote til højre for linjen |

Sådan forbindes linjerne: **to enheder over ét par** → venstre enhed til venstre ægtefælle,
højre til højre. **Lige mange enheder over og under** → parvis. **Én over én** → til
`^`-personen, ellers den førstnævnte. **Én over flere** → kun til enheden med `^`.
Passer tallene ikke, standser bygningen med en fejl og et linjenummer — **ret tavlen, ikke
`mdpdf.py`**.

Tommelfingerregler: højst **to par** i bredden (fire bokse) · højst 7-8 generationer per
tavle, ellers del den · korte undertekster (erhverv, sted, ét årstal) · `VERSALER` for det
slægtsnavn, afsnittet handler om (`EKSEMPELSEN`) · tag udkastet fra `bogdata` og ret
**ordlyden**, ikke navne og år. Er en ane usikker, så skriv `(formodet)` i underteksten.

## 5. Billedklip — få, og kun dem brugeren har peget på

**Brugeren udpeger selv klippene.** Foreslå gerne (bogdatas afsnit 3), men sæt ikke nye ind uden
et ja. Højst ét klip per kapitel; en bog på 100 sider bærer 10-15.

```
python arkiv\klip.py kirkeboger/1868-eksempelsogn-fodte-maend-opslag-51.jpg --gitter
```

1. **Se gitterbilledet** (Read-værktøjet på den fil, scriptet nævner). Find indførslen —
   nummer, navn, dato — og aflæs `x0 x1 y0 y1` på de røde 10 %-linjer.
2. `python arkiv\klip.py <fil> 0.215 0.572 0.868 0.958` → **se prøveklippet.** Ret, til
   indførslen står hel uden sort kant og uden halve nabolinjer. Scriptet udskriver den færdige
   markdown-linje.
3. Sæt linjen ind **på sin egen linje med en blank linje over og under**, lige efter det
   afsnit, der omtaler kilden:

```markdown
![Eksempelsogn, fødte mandkøn 1868, nr. 23: «3die Marts · Anders Eksempelsen»](media/kirkeboger/1868-….jpg "klip=0.215 0.572 0.868 0.958")

![Dagbladet, 3. marts 1950](media/dodsannoncer/1950-….jpg "side=højre bredde=0.42")
```

| Valg | Virkning |
|---|---|
| `klip=x0 x1 y0 y1` | brøkdele af billedet, **x først, så y** (samme som `gkasse.py`). Udelades for færdige udklip |
| `side=højre` / `side=venstre` | de næste (op til tre) almindelige afsnit løber rundt om billedet. Til dødsannoncer og randnoter |
| `bredde=0.42` | andel af satsbredden. Standard: 1.0 i fuld bredde, 0.42 med `side=` |
| `kontrast` | strammer en bleg side op |

- **Billedteksten er alt-teksten** og skal nævne kilde, år og nummer — og kun det, du kan læse
  på klippet. Ingen `"` i den.
- En kirkebogsindførsel er typisk en **strimmel**: fuld bredde, uden `side=`. Går indførslen
  over begge sider af opslaget, så klip venstre side (nr., dato, navn, forældre) for sig —
  en strimmel i forholdet 10:1 bliver ulæselig.
- Dødsannoncerne i `media/dodsannoncer/` er færdige udklip: `side=højre bredde=0.42`, evt. et
  let `klip=` for at fjerne naboannoncer.
- **Skriv aldrig et udklip til disk** — hverken i mediemappen, i `dokumenter\` eller i
  projektet. `mdpdf` beskærer i hukommelsen ved hver bygning. (Reglen i `AGENTS.md`: ingen fil
  må ligge to steder eller under to navne.)
- `media/…` er webtrees' mediemappe, som `mdpdf` finder via miljøvariablen `WEBTREES_MEDIA`
  (fx `\\<NAS>\docker\webtrees\data\media`). Er NAS'en væk, kommer der en advarsel og en grå
  pladsholder; PDF'en bygges alligevel. **Sig det til brugeren**, aflevér ikke.

## 6. Byg

```
python arkiv\mdpdf.py --bog SLAEGTSHISTORIEN-<NAVN>.md $env:SLAEGT_ARBEJDSMAPPE\proeve.pdf    # prøve
.\byg-pdf.ps1                                                                          # de rigtige, i roden
```

Byg altid **prøven i scratch først**. Overskriv først PDF'erne i roden, når trin 7 er bestået.
Uddata skal slutte med `skrevet: …` og må ikke indeholde `ADVARSEL` eller `FEJL`.

| Melding | Årsag og rettelse |
|---|---|
| `FEJL i tavle, linje N: …` | syntaksfejl i tavlen på md-linje N — oftest manglende mellemrum om `∞`, eller en tom person |
| `… linjer oppefra kan ikke fordeles på … enheder` | antallet af enheder passer ikke mellem to generationer — brug `^`, `børn:` eller del tavlen |
| `ADVARSEL: billedet kunne ikke laeses` | forkert sti (tjek stavning mod bogdatas afsnit 3) eller NAS'en er væk |
| `ADVARSEL: markup kunne ikke saettes` | skævt indlejret `**`/`*` i et afsnit — ret markdownen, så fed og kursiv lukkes i omvendt rækkefølge |
| `ADVARSEL: ingen skrift kan tegne: …` | et særtegn, hverken Palatino eller Segoe UI Symbol har — erstat det |
| `PermissionError` på PDF'en | den er åben hos brugeren — sig til, og byg til et andet navn |

## 7. Kontrol — før noget afleveres

1. **Se siderne.** Rendér til PNG og åbn dem med Read-værktøjet — mindst: titelbladet,
   indholdsfortegnelsen, **hver tavle**, **hvert klip**, én delside, én formodningsboks.

```
python -c "import fitz,sys; d=fitz.open(sys.argv[1]); [d[int(n)-1].get_pixmap(dpi=80).save(sys.argv[1][:-4]+'-s'+n+'.png') for n in sys.argv[2].split(',')]" $env:SLAEGT_ARBEJDSMAPPE\proeve.pdf 1,2,4,5
python -c "import fitz,sys; d=fitz.open(sys.argv[1]); print([i+1 for i,p in enumerate(d) if sys.argv[2] in p.get_text()])" $env:SLAEGT_ARBEJDSMAPPE\proeve.pdf "Dagbladet, 3. marts"
```

2. **Hver tavle mod bogdatas afsnit 1 og 2 — navn for navn, år for år.** Peger hver linje på
   den rigtige ægtefælle? Står noget uden for margenen? Ligner to bokse et par, som ikke er det?

2b. **Ord- og faktakontrol med `arkiv\tekstkontrol.py`**, når teksten er skrevet om:

```
python arkiv\tekstkontrol.py SLAEGTSHISTORIEN-<NAVN>.md SLAEGTSHISTORIEN-<NAVN>.md.bak-ÅÅÅÅ-MM-DD
python arkiv\tekstkontrol.py <del>.md SLAEGTSHISTORIEN.md.bak-ÅÅÅÅ-MM-DD 40 380
```

   Den finder både forbudte ord og datoer, årstal og navne, der er faldet ud. **Alt, der er
   væk, skal forklares** — enten hørte det til et fjernet redaktionelt afsnit, eller også skal
   det ind igen. Linjeskift midt i en dato giver falske udslag; efterprøv hvert enkelt.
   **En omskrivning taber datoer — regn med det, og led efter dem.** Det sker let i flere
   dele af samme omskrivning og er kun til at se, fordi kontrollen bliver kørt.
3. **Hvert klip:** er det den rigtige indførsel, hel, læselig, og siger billedteksten det samme
   som klippet?
4. **Indholdsfortegnelsen:** ligger hvert kapitel under den rigtige del?
5. **Formodninger:** står hver slutning i en boks — og intet dokumenteret i en?
6. Søg teksten igennem for arbejdsgang: `fundet`, `søgning`, `opslag`, `bsid`, `journal`,
   `.py`, `facit` — og fjern, hvad der handler om jagten.
7. Er tavler **rettet** i en eksisterende fil: lav først `<fil>.bak-ÅÅÅÅ-MM-DD`, og sammenlign
   bagefter ord for ord, at intet navn eller årstal er faldet ud.

Vis derefter PDF-filen for brugeren, sig hvilke sider tavler og klip står på, og
**sig ærligt, hvad der ikke blev kontrolleret**. Før til sidst `arkiv\README-DA.md` ajour med
en kort note, hvis værktøjerne eller syntaksen er ændret — fortællingens indhold hører ikke til dér.

## 8. Det, der går galt

- **En tavle skrevet efter hukommelsen.** Navne og år kommer fra `bogdata` eller `facit.json`.
  «En xref-liste er ikke en navneliste» gælder også her: slå børnene op ved navn.
- **`∞` uden mellemrum** (`Far∞Mor`) læses som ét navn. **`—` i et navn** læses som samliv —
  skriv `-` eller `,` i stedet.
- **Klip med y og x byttet om.** Rækkefølgen er `x0 x1 y0 y1`.
- **Et klip af den forkerte indførsel**, fordi filnavnet lovede noget. Filnavnet siger, hvad
  siden rummer — ikke hvor på siden. Se efter nummeret og navnet i gitterbilledet.
- **Billedlinjen midt i et afsnit** eller uden blank linje omkring: så bliver den til tekst.
- **`side=højre` foran en overskrift, liste, tabel eller boks:** der er ingen afsnit at løbe
  rundt om, og billedet sættes i stedet for sig selv. Flyt linjen op foran et almindeligt afsnit.
- **Nyt kapitel hængt på i bunden.** Det ender under den sidste del. Sæt det ind, hvor det hører til.
- **BOM.** `SLAEGTSHISTORIEN.md` begynder med en UTF-8 BOM. Bevar den, som den er; `mdpdf`
  læser begge dele. Gem aldrig filen i en anden tegnkodning end UTF-8.
- **Ret ikke `mdpdf.py` for at få én tavle til at passe.** Skal værktøjet virkelig ændres, så
  byg bagefter **alle** dokumenter, der sættes med den (hver `SLAEGTSHISTORIEN*.md` med
  `--bog`, og eventuelle fortløbende dokumenter uden) og se dem igennem.
