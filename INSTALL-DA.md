# webtrees på en Synology-NAS

**Adresse:** `http://din-nas.dit-tailnet.ts.net:8081` (kræver Tailscale)
På hjemmenettet svarer NAS'ens lokale IP (fx `http://192.168.1.x:8081`) også, men brug
MagicDNS-navnet — det er den adresse, `BASE_URL` er sat til, og dermed den alle links peger på.

Eksemplerne nedenfor bruger `din-nas` som maskinnavn, `dit-tailnet` som tailnet-navn og
`aner` som træets navn. Skift dem ud med dine egne overalt — også i `docker-compose.yml`.

Stakken ligger i `/volume1/docker/webtrees`.

## Hvad er sat op

| | |
|---|---|
| Image | `ghcr.io/nathanvaughn/webtrees:latest` (webtrees 2.2.x) |
| Database | `mariadb:12` i egen container, named volume `webtrees_db` |
| Port | **8081** på NAS'en (vælg en anden, hvis 8081 allerede er optaget af en anden container) |
| Slægtsdata + media | bind mount → `/volume1/docker/webtrees/data` |
| UID/GID | `PUID`/`PGID` i compose-filen sættes til **din egen** DSM-brugers id'er, så `data/` kan læses direkte over SMB. Find dem over SSH med `id <brugernavn>` — på Synology er gruppen `users` typisk GID 100, og den første oprettede bruger typisk UID 1026, men tjek det. |

## ⚠ Skift kodeordene, før du starter

`docker-compose.yml` indeholder **pladsholdere** som `SKIFT-MIG-ud-med-et-langt-tilfaeldigt-kodeord`
for `MARIADB_PASSWORD` og `MARIADB_ROOT_PASSWORD`. De **skal** skiftes til lange, tilfældige
kodeord, før containeren startes første gang — MariaDB opretter brugerne med de kodeord, der
står der ved første opstart, og det er besværligt at ændre bagefter.

Brug det samme `MARIADB_PASSWORD` i opsætningsguiden og i backupscriptet nedenfor (her skrevet
som `<DB-KODEORD>`). Læg aldrig den udfyldte compose-fil i et offentligt repo.

## Genstart efter ændringer i denne fil

Container Manager → **Projekt** → `webtrees` → **Action** → **Build**.
Eller over SSH: `cd /volume1/docker/webtrees && sudo docker compose up -d`.

## Opsætningsguiden køres i browseren

Auto-opsætningen via `DB_*`/`WT_*` er bevidst slået fra — se kommentaren i
`docker-compose.yml`. Første gang åbnes `http://din-nas.dit-tailnet.ts.net:8081` i stedet, og
guiden udfyldes med:

**Sprog:** Dansk

**Databaseforbindelse:**

| Felt | Værdi |
|---|---|
| Server | `db` |
| Port | `3306` |
| Brugernavn | `webtrees` |
| Adgangskode | `<DB-KODEORD>` — det `MARIADB_PASSWORD`, du satte i compose-filen |
| Databasenavn | `webtrees` |
| Tabelpræfiks | `wt_` |

`db` er containernavnet på Docker-netværket — **ikke** `localhost` og ikke NAS'ens IP.
Databasen og brugeren er allerede oprettet af `mariadb`-containeren.

**Administrator:** vælg selv brugernavn, navn, e-mail og en kode.

## Bagefter

- **Opret et træ:** Kontrolpanel → *Træer* → *Opret et nyt slægtstræ* (fx med navnet `aner`),
  og importér din GEDCOM-fil derfra. Store GEDCOM-filer kan lægges i
  `/volume1/docker/webtrees/data` først, så kan de vælges direkte på serveren i stedet for at
  uploades.
- **Backup:** se afsnittet *Backup* nedenfor. Hyper Backup alene er **ikke** nok.
- **Temaer/moduler:** læg dem i containeren under `/var/www/webtrees/modules_v4/`.
  Bind-mount ikke en tom mappe derover — det skjuler de indbyggede moduler.

## Klienten til AI-assistenten

`webtrees_klient.py` i projektmappen opretter poster i træet ved at sende de samme
formularer som browseren — webtrees har ingen API. Den bruges til at lægge arkivfund ind
uden at taste dem i hånden.

**Bruger:** fx `ai`, rolle **Redaktør** på træet, med flueben i *Godkend ændringer
foreslået af denne bruger*. Uden det flueben bliver nye poster tomme skaller, og klienten
kan ikke slå familier op undervejs; den stopper med en fejl.

**Login:** `%USERPROFILE%\.webtrees\login.json` — oprettet i hånden af dig, aldrig på
NAS-sharet eller i projektmappen (som typisk kommer med i backuppen). Klienten nægter at
læse en login-fil derfra og maskerer kodeordet i al output.

```json
{"base_url": "http://din-nas.dit-tailnet.ts.net:8081", "tree": "aner", "username": "ai", "password": "…"}
```

```bash
python webtrees_klient.py --check                    # login + rettigheder
python webtrees_klient.py --dry-run poster\job.json  # vis hvad der ville blive sendt
python webtrees_klient.py poster\job.json            # kør
```

Jobformat og operationer: `poster\README-DA.md`. Hver kørsel logger til `poster\log.jsonl`,
og hver ændring bærer brugernavnet (`_WT_USER ai`) i sin `CHAN`, så alt kan spores i **Ændringsloggen**.

**Én ting at huske ved slægtskaber:** webtrees' *tilføj forælder* opretter altid en **ny**
familie. To forældre til samme person laves derfor som `add-parent` for den første og
`add-spouse-to-family` med `@FØRSTE.FAMS@` for den anden — ellers ender personen med to
forældrefamilier.

## Kort: "Kort over slægtninge" og Stedhierarkiet

webtrees gemmer stednavne som **ren tekst**. Koordinater ligger i en separat tabel og
redigeres i **Kontrolpanel → Kort → Geografiske data** (`/admin/map-data`). Er tabellen
tom, er kortene tomme — modulet virker, men har intet at tegne.

**AI-assistenten kan ikke gøre det.** Alle `/admin/`-ruter kræver administrator, og
assistentens bruger er redaktør. Importen skal derfor køres af dig.

### Importfilen

`webtrees-steder.csv` i projektmappen skal dække **alle stednavne i træet**, med
mellemniveauerne (land, amt, herred) og kirkens position som koordinat for hvert sogn.

Kontrolpanel → Kort → Geografiske data → **Importér fil** → vælg `webtrees-steder.csv`.

Formatet er webtrees' eget: semikolonsepareret, UTF-8 uden BOM, CRLF, med `E`/`N` foran
koordinaterne:

```
"Niveau";"Land";"Stat";"Amt";"By";"Længdegrad";"Breddegrad";"Zoom faktor";"Ikon";
3;Danmark;<Amt>;<Herred>;<Sogn>;E<længde>;N<bredde>;14;
```

Niveauet er antallet af led **under** landet. `<Sogn>, <Herred>, <Amt>, Danmark` er fire led
og dermed niveau 3. Brug de **historiske** inddelinger, og sognekirkens koordinat — ikke
landsbyens. `arkiv\kirkesoeg.py` og `arkiv\wdkoord.py` slår kirkens punkt op.

### Hvorfor ikke den færdige Danmarks-fil

Der findes en færdig pakke på <https://webtrees.net/downloads/geographic-data/denmark.zip>,
opdelt efter **historiske amter**. Den kan bruges, men den passer sjældent helt: den kan
kalde amtet *København*, hvor du skriver *Københavns Amt*, lægge et sogn i et andet herred
end det, du har slået op, eller bruge en anden form af sognenavnet. webtrees matcher på den
nøjagtige tekst, så de poster ville lande ved siden af. Med et overskueligt antal steder er
en håndlavet fil både hurtigere og præcis.

Pakkens koordinater er desuden ikke altid kirkens — tjek dem, før du stoler på dem.

### Hvad kortene så viser

**Kort over slægtninge** (Diagrammer-menuen) tager én person og tegner **fødestederne for
personens aner** ind, nummereret og farvet efter generation, med linjer fra barn til
forælder. Antallet af generationer vælges øverst på siden.

**Stedhierarki** (Slægtslister) viser alle steder i træet som et kort og en trævisning.

Kortbaggrunden er OpenStreetMap og hentes fra internettet; selve slægtsdataene forlader
ikke NAS'en.

## Metoden og AI-assistenten

`METODE.md` er metoden til arkivsøgning og registrering, og `AGENTS.md` er projektets regler.
Metoden kender navigationen i Arkivalieronline, hjælpescriptene i `arkiv/`,
webtrees-klienten og de fælder, der har kostet mest tid — at en fødsel registreres i
forældrenes sogn, at `add-parent` altid laver en ny familie, at dødsfald noteres i
fødselslisten.

Begge filer læses af de fleste AI-kodeassistenter:

- **Claude Code** læser `CLAUDE.md`, som henviser til `AGENTS.md`. Metoden findes også som
  underagenten `slaegtsforsker`: "brug slægtsforsker-agenten til at …".
- **Codex** og flere andre (Cursor, GitHub Copilot m.fl.) læser `AGENTS.md` direkte.
- **Gemini CLI** læser `GEMINI.md`, som henviser til `AGENTS.md`.

Assistenten skal kunne køre kommandoer, læse filer og **se billeder**, for afskrifterne
læses direkte fra scanningerne af håndskrift.

## Backup

**Hyper Backup af `/volume1/docker/webtrees` sikrer ikke slægtstræet.**

Selve træet — personer, familier, datoer, kilder, noter — ligger i MariaDB, i Docker-volumet
`webtrees_db` under `/volume1/@docker/volumes/`. Det er en systemmappe uden for de delte
mapper, så den kan hverken vælges i Hyper Backup eller ses i File Station. I `data/` ligger
kun medier, `config.ini.php` og cache.

Og selv hvis mappen kunne vælges, ville det ikke duge: en filkopi af en kørende databases
datafiler kan ramme midt i en skrivning og blive ubrugelig. Derfor dumpes databasen i
stedet — så beder man den om et konsistent øjebliksbillede.

### Planlagt dump

DSM → **Control Panel → Task Scheduler → Create → Scheduled Task → User-defined script**

| Fane | Værdi |
|---|---|
| General | Task: `webtrees database dump` · User: **root** |
| Schedule | Daily, 03:00 |
| Task Settings | Scriptet nedenfor |

```bash
mkdir -p /volume1/docker/webtrees/backup
docker exec webtrees-db mariadb-dump -u webtrees -p'<DB-KODEORD>' webtrees \
  > /volume1/docker/webtrees/backup/webtrees-$(date +\%u).sql
```

Erstat `<DB-KODEORD>` med dit `MARIADB_PASSWORD`. Scriptet ligger i DSM's Task Scheduler, som
kun root kan se — men læg det aldrig i en fil, der deles.

`\%u` er ugedagen 1-7, så filerne roterer over en uge af sig selv. Procenttegn **skal**
escapes i Task Scheduler. Sæt gerne *Send run details by email* med *only when the script
terminates abnormally* — en backup, der fejler i stilhed, opdages først den dag, den
skulle bruges.

Dumpet lander i `/volume1/docker/webtrees/backup/`, som Hyper Backup-opgaven allerede
dækker. Dermed er træet, medierne og konfigurationen med i én og samme sikkerhedskopi.

### Kontrollér at det virker

Kør opgaven manuelt (**Run**) og se på filen:

```bash
head -2 /volume1/docker/webtrees/backup/webtrees-*.sql   # MariaDB dump-header
tail -1 /volume1/docker/webtrees/backup/webtrees-*.sql   # "Dump completed on ..."
```

`Dump completed` skrives kun ved et fuldført dump. Mangler linjen, er filen ufuldstændig.
Er filen tom, er `docker` sandsynligvis ikke i PATH — brug `/usr/local/bin/docker` i stedet.

Udelad **`data/cache`** fra Hyper Backup via *Create file filters*. Den indeholder kun
midlertidige filer og kan vokse sig stor.

### Gendannelse

```bash
docker exec -i webtrees-db mariadb -u webtrees -p'<DB-KODEORD>' webtrees \
  < /volume1/docker/webtrees/backup/webtrees-6.sql
```

Medier og konfiguration lægges tilbage i `/volume1/docker/webtrees/data`, hvorefter
projektet bygges igen.

## ⚠ Privatliv: indstillingen forudsætter Tailscale

Adgang udefra sker via **Tailscale** — ingen porte er åbnet i routeren. Det er den
forudsætning, privatlivsopsætningen hviler på.

Under Kontrolpanel → *Træer* → **Privatliv** står:

| Indstilling | Værdi | Betyder |
|---|---|---|
| Vis slægtstræet | `Vis til gæster` | Man kan læse den historiske slægt **uden login** |
| Vis nulevende | `Vis til medlemmer` | Levende personer kræver login |

Formålet er to niveauer: fjerne slægtninge deles der bare en Tailscale-node med, og de
ser afdøde forfædre, kilder og attester uden at have en konto. Konti — og dermed adgang
til levende personer — gemmes til den nære kreds. `Vis nulevende` har kun to niveauer
(gæster/medlemmer), så en finere trappe findes ikke.

**Konsekvensen ved at gå offentligt:** `Vis til gæster` betyder bogstaveligt "enhver der
kan nå adressen". Så længe adressen kun findes inde i tailnettet, er det de inviterede.
Lægges siden på internettet, bliver det hele verden.

> **Åbnes siden nogensinde offentligt, skal `Vis slægtstræet` først sættes til
> `Vis til medlemmer`.**

## Tailscale: adgang udefra og ACL

NAS'en er en node (her `din-nas`) i dit tailnet. Slå **nøgleudløb** fra for den i
Tailscale-konsollen, så den ikke falder af netværket efter 180 dage.

Familien får adgang med **node sharing** — `Machines → din-nas → Share` — ikke med
brugerkonti i tailnettet. De beholder deres eget tailnet, ser kun denne ene maskine,
kan ikke dele den videre, og adgangen kan trækkes tilbage med ét klik.

### Politikken (Access controls → JSON editor)

Indsæt NAS'ens Tailscale-IP (100.x.y.z, står under *Machines*) i stedet for pladsholderen:

```json
{
	"hosts": {
		"nas": "100.x.y.z",
	},

	"grants": [
		// Egne enheder: adgang til alt
		{"src": ["autogroup:member"], "dst": ["*"], "ip": ["*"]},

		// Exit node (kun hvis du har en)
		{"src": ["autogroup:member"], "dst": ["autogroup:internet"], "ip": ["*"]},

		// Delte brugere: kun webtrees, intet andet
		{"src": ["autogroup:shared"], "dst": ["nas"], "ip": ["tcp:8081"]},
	],

	"ssh": [
		{
			"action": "check",
			"src":    ["autogroup:member"],
			"dst":    ["autogroup:self"],
			"users":  ["autogroup:nonroot", "root"],
		},
	],
}
```

**Den vigtigste linje er den, der ikke står der.** Standardpolitikken indeholder
`{"src": ["*"], "dst": ["*"], "ip": ["*"]}`, som tillader alt for alle — også delte
brugere. Grants er en liste over hvad der *tillades*, ikke hvad der forbydes, så en
snæver regel har ingen virkning, så længe den brede står der. Den skal **erstattes**,
ikke suppleres.

`autogroup:shared` dækker automatisk enhver, der senere deles med. Der skal ikke
tilføjes navne per person.

### Verifikation

Bed den nye bruger prøve begge dele fra sin egen maskine:

| Adresse | Forventet |
|---|---|
| `http://din-nas.dit-tailnet.ts.net:8081` | webtrees kommer frem |
| `https://din-nas.dit-tailnet.ts.net:5001` | **timeout** — DSM må ikke svare |

Kommer DSM's loginside frem, er den brede regel ikke fjernet.

## Hvis den skal på internettet

Læs de to afsnit ovenfor først — privatlivsindstillingen skal ændres, før noget andet.

`BASE_URL` skal rettes til det rigtige domæne (fx `https://slaegt.dit-domaene.dk`) og `HTTPS`
sættes til `1` — webtrees bygger alle sine links ud fra `BASE_URL`, så login og navigation
går i stykker hvis den ikke passer. Sæt DSM's reverse proxy (Kontrolpanel → Login-portal →
Reverse Proxy) op mod `localhost:8081` og lad den håndtere certifikatet. Byg projektet
igen bagefter.

Husk desuden, at webtrees-image'et derefter skal holdes opdateret, så længe siden står
offentligt — `:latest` opdaterer ikke sig selv.

## Databasekodeord

Kodeordene står **kun** i din lokale `docker-compose.yml` og i DSM's Task Scheduler — ikke
her, og ikke i et repo. Opbevar dem i din adgangskodeadministrator.
