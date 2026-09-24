# Gør manuelt i webtrees

> Kopiér denne fil til `GOER-MANUELT.md`. Den rigtige liste holdes ude af git.

Her står **alt det, AI-assistenten ikke selv kan eller må gøre**, i den rækkefølge det skal gøres:
import af stedfilen (kræver `/admin`), kædninger, der ikke er pakket ind i klienten
(`link-spouse-to-individual`, `link-family-to-individual`), sammenlægning af dubletter og til
sidst sletninger. Detaljerne under sletningerne står i `SLET-MANUELT.md`. **En opgave må kun
stå ét af de to steder.**

For hver opgave: **xref på både posten og familien** og **kildecitatet**, så det kan ses, *hvorfor*.

1. **Importér `webtrees-steder.csv`** (Kontrolpanel → Geografiske data → Importér fra fil,
   «Tilføj ny, og opdatér eksisterende oplysninger»). Nye rækker siden sidst: …
2. **Kæd X… til familien X…** — *(kilde og begrundelse)*
3. **Slå X… og X… sammen** (ikke slet): *(hvad der står på hver)*
