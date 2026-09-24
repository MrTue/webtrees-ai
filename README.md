# webtrees + AI — dansk slægtsforskning med en AI-assistent

Et arbejdsrum til slægtsforskning, hvor en AI-assistent i terminalen — fx
[Claude Code](https://claude.com/claude-code), Codex eller Gemini CLI — både
**læser i de danske arkiver** og **skriver fundene ind i dit eget slægtstræ** i
[webtrees](https://webtrees.net), med kilde, afskrift og scanning på hver oplysning.

Det består af tre dele:

| Del | Hvad det er |
|---|---|
| **webtrees i Docker** | `docker-compose.yml` og `INSTALL-DA.md`: webtrees + MariaDB på en NAS eller en hjemmeserver, eventuelt nået over Tailscale. |
| **Skrivevejen ind i træet** | `webtrees_klient.py`. webtrees har intet API, så klienten logger ind som en almindelig redaktør og sender de samme formularer som browseren. Et helt fund beskrives som ét *job* i JSON (`poster/`), og det kan altid tørkøres først. |
| **Læsevejen ud af arkiverne** | Omkring 120 små scripts i `arkiv/` til Arkivalieronline (kirkebøger, folketællinger), Dansk Demografisk Database, Mediestream, arkiv.dk, dødsregistret, kirkegårdsregistre, Københavns Stadsarkiv, Kraks Vejviser, Riksarkivet, Find a Grave m.fl. `arkiv/KILDER-ONLINE.md` beskriver, hvad der kan hentes maskinelt, og hvad der ikke kan. |

Oven på dem ligger metoden, skrevet til en hvilken som helst AI-assistent:

- **`AGENTS.md`**: projektets regler. De fleste assistenter læser filen automatisk.
- **`METODE.md`**: søgemetode, kildekritik og webtrees-fælder.
- **`.claude/skills/dansk-slaegtsforskning/`**: den samme metode som selvstændig skill.
- **`.claude/skills/slaegtsbog/`**: skriv en slægtsfortælling og sæt den som bog-PDF med tegnede slægtstavler (`arkiv/mdpdf.py`).

Alt er skrevet på dansk.

## Hvilken AI-assistent?

| Assistent | Hvad den læser |
|---|---|
| **Claude Code** | `CLAUDE.md`, som henviser til `AGENTS.md`. Metoden findes også som underagenten `slaegtsforsker`, og de to skills findes automatisk. |
| **Codex**, Cursor, GitHub Copilot m.fl. | `AGENTS.md` direkte. |
| **Gemini CLI** | `GEMINI.md`, som henviser til `AGENTS.md`. |
| Andre | Bed den læse `AGENTS.md` og `METODE.md`, før den går i gang. |

Skills-formatet (`SKILL.md`) er åbent, men hvor hvert værktøj leder efter skills, er
forskelligt. Finder dit værktøj dem ikke af sig selv, så peg det på mappen.

**Assistenten skal kunne tre ting:**

1. **Se billeder og læse håndskrift.** Der findes ingen tekstgenkendelse af kirkebøgerne;
   hele metoden hviler på, at assistenten selv læser gotisk håndskrift fra scanningerne. Små
   lokale modeller kan det sjældent godt nok. **Prøv din model af på en side, du selv kan
   læse, før du stoler på dens afskrifter.**
2. **Køre kommandoer og læse filer**, altså arbejde som agent i terminalen og ikke kun chatte.
3. **Følge reglen om at tørkøre først og spørge, før den skriver i træet.** Klientens
   `--dry-run` og dens manglende slettefunktion beskytter træet uanset assistent, men resten
   afhænger af, at assistenten overholder `AGENTS.md`.

**Valgfrit: FamilySearch.** FamilySearch kræver login og blokerer scripts. Vil du bruge det,
så log selv ind i din browser. En assistent, der kan arbejde i en browserfane, kan derefter
søge i den fane. Den ser aldrig dit kodeord. Metoden står i `METODE.md`.

## Kom i gang

**1. Installér webtrees.** Følg `INSTALL-DA.md`. **Skift de to kodeord i `docker-compose.yml`**,
før du starter containerne første gang, og ret `BASE_URL`, så den passer til din adresse.

**2. Opret en bruger til AI-assistenten** i webtrees, fx `ai`, med rollen *redaktør* på dit træ.
Giv den aldrig administratorrettigheder.

**3. Læg loginfilen uden for projektmappen.** Kopiér `login.eksempel.json` til
`%USERPROFILE%\.webtrees\login.json` (på Mac/Linux `~/.webtrees/login.json`), og udfyld den.
Assistenten må aldrig selv åbne filen; det gør kun klienten. Klienten nægter at læse loginfilen fra
projektmappen.

**4. Installér Python 3.10+ og afhængighederne:**

```
pip install -r requirements.txt
```

**5. Opret dine lokale arbejdsfiler** ud fra skabelonerne. `.gitignore` holder dem ude af git:

```
copy arkiv\README-DA.skabelon.md arkiv\README-DA.md
copy GOER-MANUELT.skabelon.md GOER-MANUELT.md
copy SLET-MANUELT.skabelon.md SLET-MANUELT.md
copy webtrees-steder.eksempel.csv webtrees-steder.csv
```

**6. Sæt to miljøvariabler** (valgfrit, men anbefalet):

| Variabel | Betydning | Standard |
|---|---|---|
| `WEBTREES_MEDIA` | webtrees' mediemappe, som scripts og PDF-sætning kan se (fx over SMB) | `//NAS/docker/webtrees/data/media` |
| `SLAEGT_ARBEJDSMAPPE` | arbejdsmappe til `facit.json`, kontaktark og andre mellemresultater | systemets temp-mappe |

**7. Prøv forbindelsen:**

```
python webtrees_klient.py --check
python webtrees_klient.py --dry-run poster\eksempel.json
```

**8. Åbn mappen i din AI-assistent**, og bed den om at finde nogen: *"Find min tipoldefar Anders
Eksempelsen, født omkring 1850 i Give sogn"*. Agenten søger, viser dig tørkørslen og skriver
først i træet, når du har sagt ja.

## Dine data bliver hos dig

Repoet indeholder **kun værktøj og metode**. Dit træ, dine jobfiler, din arkivjournal, dine
slægtshistorier, hentede billeder og loginfilen er udelukket i `.gitignore`. Se filen, før du
tilføjer noget nyt.

## Licens

MIT. Se `LICENSE`. webtrees selv er GPL og indgår ikke i repoet; det hentes som
Docker-image.
