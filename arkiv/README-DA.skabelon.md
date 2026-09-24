# Arkivjournal — hvad der er søgt i, og hvad der kom ud af det

> Kopiér denne fil til `arkiv/README-DA.md` og før din egen journal dér.
> Den rigtige journal holdes ude af git (`.gitignore`), fordi den handler om din slægt.

Kirkebøgerne på Arkivalieronline er **fotografier af håndskrift**. Der findes ingen
tekstgenkendelse og intet tekstlag. Afskrifterne i webtrees' kilder er **læst af
AI-assistenten direkte fra scanningerne** og er altså ikke officielle transskriptioner. De kan indeholde
læsefejl og bør efterprøves mod billedet, når der er tvivl.

Journalen skal spare dig for at finde navigationen forfra hver gang: hvordan hvert bind er
ordnet, hvilke opslag der dækker hvilke måneder, og **hvad der er udelukket**. Et negativt
resultat koster lige så meget arbejde som et positivt, og det er lige så let at glemme.

## Sådan navigerer man

Kirkebøgerne ligger i samling 5, "Kirkebøger fra hele landet":
<https://arkivalieronline.rigsarkivet.dk/da/geo/geo-collection/5>

Hvert bind har et `bsid`. Et opslag har en adresse af formen:

```
https://arkivalieronline.rigsarkivet.dk/da/billedviser?bsid=<bsid>#<bsid>,<billed-id>
```

Billed-id'erne er **som regel** fortløbende, så `billed-id = grundtal + opslagsnummer`. Hvor
de springer, giver `arkiv\opslagid.py` de rigtige. Selve billedet kan hentes i fuld opløsning:

```
https://api.rigsarkivet.dk/ao/v1/images/<billed-id>
```

## Bind

| Sogn | Periode | bsid | grundtal | Opslag | Opbygning |
|---|---|---|---|---|---|
| *(eksempel)* Sogn, Herred, Amt | 1814-1850 | 123456 | 12345678 | 1-320 | fødte 5-110 · konfirmerede 111-150 · viede 151-200 · døde 201-300 |

## Søgninger

For hver søgning: **dato · hvem · hvilke bind/årgange · hvilke opslag · resultat**. Skriv det
også ned, når intet blev fundet, og skriv præcis *hvad* der er udelukket.

### ÅÅÅÅ-MM-DD — *(person, hændelse)*

- **Søgt:** …
- **Fundet / udelukket:** …
- **Næste skridt:** …
