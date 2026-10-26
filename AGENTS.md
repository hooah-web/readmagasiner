# readMAGASINER — sitebrief

## Idé

Danmarks eneste sammenligning af **digitale magasintjenester** og **fysiske bladabonnementer** på samme side.
En læser søger på et blad — fx "Euroman abonnement" — og får ét svar: hvor bladet kan læses digitalt,
hvad det koster i postkassen, og hvad det koster i løssalg.

Sitet er ikke et magasin om magasiner. Det er et værktøj.

## Målgruppe

Danske læsere, 30-65 år, der overvejer at skifte fra løssalg eller papirabonnement til digital læsning —
eller som vil finde det billigste papirabonnement på et bestemt blad. De søger på et bladnavn eller på
"abonnement" plus bladnavn, ikke på "magasintjeneste".

## Hvad der gør os bedre, fordi vi er en AI

- **Katalogdækning**: 147 blade med forlag, målgruppe, land og digital tilgængelighed — bygget fra data, ikke håndskrevne indlæg
- **Priser der tjekkes dagligt** af et script, med synlig "sidst tjekket"-dato på hver pris
- **Beregning** pr. blad: pris pr. nummer, besparelse mod løssalg, samlet pris over 12 måneder
- **Ærlighed om huller**: vi viser også, når et blad *ikke* findes digitalt, i stedet for at skjule det

## Tone

Kort, konkret, dansk. Ingen sælgende adjektiver, ingen "oplev magien". Tal og datoer frem for påstande.
Vi skriver "vi", når vi mener sitet, og vi påstår aldrig at have læst, testet eller abonneret personligt.

## Teknik

- Astro 5, statisk output, Cloudflare Pages
- `trailingSlash: 'always'`, `build.format: 'directory'` — bevarer eksisterende URL'er
- Al indhold læses fra `data/magasiner.json` og `data/prices_current.json`; sider genereres, håndskrives ikke
- Ingen klientside-framework. Interaktivitet som små inline-scripts
- Billeder: WebP/AVIF, flere størrelser, lazy loading, maks. 250 KB pr. fil

## Design (CVI)

| Rolle | Farve |
|---|---|
| Primær | Marineblå `#123456` |
| Accent (knapper, store tal) | Klar blå `#0875D1` |
| Accent som tekstfarve | `#0A63AE` (kontrast 5,84:1) |
| Positiv | `#147A42` (kontrast 5,12:1) |
| Baggrund | `#F7F9FC` |
| Kort og paneler | Hvid `#FFFFFF` |

Typografi: Inter. Ordmærke i tekst — `read` fed + `magasiner` normal, marineblå, blåt punktum.
Favicon: to opslag side om side (SVG). Ingen illustreret logo.

Annonceformater: 300×600 sticky i højre skinne på desktop (fra 1180 px), 930×180 i flow, 300×250 på mobil.
Fast reserveret højde, mærket "Annonce", aldrig i preview-deploys.

## Priser og data

- Priser hentes fra tjenesternes egne sider af `scripts/price_check.py`, dagligt kl. 06:15
- Tre pristyper skal vises, når de findes: ordinær, introduktionspris, kampagnepris
- Readly opkræver i EUR: vis både euro og omregnet DKK med kursdato
- En pris uden dato vises aldrig

## AI-åbenhed

Alle sider er skrevet af en AI. Det står i footeren på hver side og forklares på "Om"-siden.
Tekst, der er udvidet af os, markeres som AI-skabt i data (`ai_tekst: true`).
Vi opfinder aldrig anmeldelser, bedømmelser eller erfaringer.

## URL-regler

- Eksisterende URL'er bevares eller 301'es — aldrig ændret uden redirect
- Nye sider: `/magasin/<navn>-abonnement/`, `/tjeneste/<navn>/`, `/soeg/`
- Gamle affiliate-redirects (`/flipp`, `/pling`, `/wype`, `/readly`) 301'es til vores egen tjenesteside
