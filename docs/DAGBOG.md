# Dagbog — readmagasiner.dk

Nyeste post øverst. Én post pr. arbejdsfase, ikke pr. kommando.
Skriv hvad der blev ændret, hvad der blev besluttet, og hvad der stadig mangler.
Tal skal være talt op, ikke husket.

---

## 26. oktober 2026 — beskrivelser skrevet om

**Hvad der skete**
- Alle 87 blade har nu en ny beskrivelse. 41 sider havde ingen tekst; 46 havde arvet tekst.
- Første runde skrev alle 87, men 36 af de 46 eksisterende blev kortere end originalen.
  De blev sendt til en ny runde med krav om mindst 150 tegn mere.
- Nu: median 1.183 tegn, maks 1.710. Ingen er kortere end den oprindelige tekst.

**Fejl fundet og rettet**
- 20 udgivelsesfrekvenser og vurderinger ("månedligt", "18 gange om året", "kortere
  anmeldelser frem for dybdegående kritik") stod ikke i kildeteksten. Fjernet.
  Tilbage er kun frekvenser der står i den oprindelige tekst, eller som er alment kendte.
- `bladTekst()` foretrak `data/rewritten.json` frem for `magasiner.json`, så de gamle
  tekster blev ved med at vises efter den nye runde. Filen er slettet, og funktionen
  læser nu kun magasiner.json. Det var tæt på at gå ubemærket hen — jeg fandt det ved at
  tjekke den deployede side frem for kun at tjekke bygget.

**Mangler stadig**
- 40 blade uden forlag.
- `/tjenester/`, `/soeg/` og `/om/` er ikke bygget om til designsystemet.

---
## 26. oktober 2026 — kun danske blade

**Hvad der skete**
- De 13 udenlandske sider er fjernet. Kataloget er nu 87 danske blade, alle fundet hos
  en af de fire tjenester, alle med omslag.
- Redirect-blokken blev udvidet til 202 regler, og scriptet bevarer nu tidligere kørslers
  regler i stedet for at overskrive dem.
- 0 interne links peger på fjernede sider. Søgeindekset er 87 poster. Sitemap 98 URL'er.

**Beslutninger**
- Kun danske blade har sider. Udenlandske titler nævnes som tal på tjenestesiderne.

**Mangler stadig**
- 41 blade uden beskrivelse, 40 uden forlag.
- `/tjenester/`, `/soeg/` og `/om/` er ikke bygget om til designsystemet.

---
## 26. oktober 2026 — 88 blade fjernet

**Hvad der skete**
- Kataloget gik fra 188 til 100 sider. De 88 blade, der ikke findes hos nogen af de fire
  tjenester, er fjernet, og deres URL'er 301'es til `/magasiner/` (176 regler).
- 0 interne links pegede på de fjernede sider. Sitemap går fra 199 til 111 URL'er.
- Alle 100 tilbageværende blade har et omslag — de kommer alle fra en tjenesteliste.

**Beslutninger**
- Kun blade vi selv har fundet findes som sider. Tomme "findes ingen steder"-sider er væk.
- Sitet påstod 171 danske blade. Det reelle tal er 87 danske og 13 udenlandske.

**Mangler stadig**
- 41 blade uden beskrivelse (de 21 nye sider har ingen tekst endnu), 40 uden forlag.
- TopModel er fjernet sammen med de andre, men har en print-aftale hos Egmont. Anders bør
  tage stilling til om den skal tilbage som ren print-side.

**Fejl undervejs**
- Ingen, men tørkørslen viste advarslen om TopModel, som ellers var let at overse.

---
## 26. oktober 2026 — Wypes udvalg hentet

**Hvad der skete**
- Hentet Wypes udvalg fra `wype.dk/online-magasiner`: 13 danske titler, alle matchet kataloget.
- Wype er nu fjerde sandhedsliste. `build_udvalg.py` kører fire kilder, og "Ikke oplyst"
  findes ikke længere i udvalgstabellerne.
- To manglende omslag hentet fra Wypes CDN (I FORM, Woman). 100 af 188 blade har nu omslag.

**Beslutninger**
- Alle fire tjenester har komplette lister. "Nej" betyder nu undtagelsesfrit "står ikke på
  tjenestens liste", og det er dokumenteret med dato.

**Mangler stadig**
- 41 sider uden beskrivelse, 95 uden forlag.
- `/tjenester/`, `/soeg/` og `/om/` er ikke bygget om til designsystemet.

**Fejl undervejs**
- Min deploy-polling matchede "en nyere deploy end den forrige" i stedet for commit-hashen,
  så jeg verificerede en gammel preview og konkluderede forkert i et par minutter.
  Poll nu på commit-hash.

---
## 26. oktober 2026 — beslutningerne skrevet ned

**Hvad der skete**
- Gennemgang af hele samtaletråden (127 beskeder fra Anders) for at finde beslutninger der
  kun fandtes i dialogen. De er nu skrevet ned i `docs/BESLUTNINGER.md` — 13 beslutninger
  med dato og begrundelse.
- `USER.md` og `MEMORY.md` er skrevet direkte på disken, fordi memory-værktøjet fejler.

**Beslutninger**
- Beslutninger der træffes i dialog skal skrives i `docs/BESLUTNINGER.md` samme dag.
  Ellers findes de ikke i næste session.
- De tre dokumenter har hver sin rolle: STATUS.md = tilstand nu, BESLUTNINGER.md = hvorfor,
  DAGBOG.md = hvad der skete hvornår.

**Mangler stadig**
- Wypes udvalg, beskrivelser til de 21 nye sider, redesign af /tjenester/, /soeg/ og /om/.

---
## 26. oktober 2026 — udvalget bliver sandhed

**Hvad der skete**
- Tjenesternes egne kataloger er nu den eneste kilde til udvalg: Readly 21 titler,
  Pling 57 (syv kategorisider), Flipp 93 (`flipp.dk/magasiner/`).
- Kataloget voksede fra 167 til 188 sider, fordi listerne indeholder danske titler vi
  ikke havde: Ekstra Bladet, Jumbobog, Rasmus Klump, VILD MED LØB, INDRET by femina,
  Magasinet Lækkerier, Anders And Classic, Disney Prinsesser m.fl.
- 98 af 188 blade har nu et rigtigt forsidebillede hentet fra tjenesternes CDN.
- Forsiderne er skaleret til 440 px webp (1,1 MB for 21 Readly + 15 Pling).

**Beslutninger**
- Listerne er sandhed: titel på listen = "Ja · bekræftet", titel uden for listen = "Nej".
  Wype har vi ingen fuld liste fra, så der står "Ikke oplyst" indtil videre.
- Vi opretter katalogsider for danske titler, også når de ikke er magasiner i snæver
  forstand (Ekstra Bladet er en avis).
- Forlag sættes ikke på nye sider, fordi vi ikke kan dokumentere det.

**Fejl fundet og rettet**
- `udvalgsStatus()` tjekkede aldrig om availability sagde "nej" → alt viste "Ikke oplyst".
- `tjenester.json` blev ikke opdateret sammen med listerne → Flipp stod med 87 mod 93.
- "Se hos Flipp"-knappen blev vist, selv når Flipp ikke havde bladet.
- Forside-forslagene pegede på `/euroman/`, men slugs har præfiks (`magasin-euroman`).
- Mobil-CTA hed "Se alle magasiner" og gik til kataloget i stedet for at søge.

**Mangler stadig**
- 90 blade uden omslag, 95 uden forlag, 41 uden beskrivelse.
- Wypes udvalg er ikke hentet som liste.
- `/tjenester/`, `/soeg/` og `/om/` er ikke bygget om til det nye designsystem.

---

## 26. oktober 2026 — nyt designsystem

**Hvad der skete**
- Anders' mockup blev implementeret: pine `#123B3A`, cream `#F8F7F3`, mint `#E4F1EB`,
  guld `#F4B860`, DM Serif Display til overskrifter og Inter til UI.
- Ny forside, katalog med cover-grid, bladside med stort omslag og tilgængelighedsrækker,
  tjenesteside med prispanel og faktakort, sammenligning med scenarie-chips.
- Alle farvepar kontrastverificeret mod WCAG AA (pine 11,4:1, muted 5,68:1, hvid på pine 12,3:1).

**Beslutninger**
- Omslag: rigtigt forsidebillede hvor vi har det, ellers farvet omslag med titlen i serif.
- På billeder med ægte forside skjules påskriften, fordi titlen allerede står på bladet.

**Værktøj**
- Browserens enhedsemulering holdt op med at virke, og Chrome headless på Linux nægter
  vinduer under 500 px. Løsningen blev `cdp_shot.py` (CDP over WebSocket, rigtig viewport).

---

## Tidligere — chokolademuffin.dk

- Migreret fra WordPress til statisk Astro på Cloudflare Pages, 49 opskrifter, 75 redirects.
- Produktion `737b0cb2`, sitemap uden fejl, www → 301.
- Mofibo- og AdSense-annoncer i produktion, morgenrapport kl. 07:00 via cron.
