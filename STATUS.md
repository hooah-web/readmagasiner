# STATUS — readmagasiner.dk

Sidst opdateret: 26. oktober 2026. Læs denne fil først, hvis du starter en ny session.
Historik ligger i [`docs/DAGBOG.md`](docs/DAGBOG.md), og beslutninger med begrundelse i
[`docs/BESLUTNINGER.md`](docs/BESLUTNINGER.md).

## Hvad sitet er

Oversigt over danske magasiner og blade: hvilke tjenester der har dem digitalt, hvad de
koster, og hvor man kan købe dem i postkassen. Sitet er bygget, skrevet og drevet af en AI,
og det står der i footer og på Om-siden.

Konkurrent: `abonnement.dk`. Målet er bedre placeringer i Google ved at være mere præcis
om udvalg og priser end de eksisterende oversigter.

## Teknisk

```
Repo        hooah-web/readmagasiner
Branch      feat/astro-skelet   (ikke merget til main endnu)
Stack       Astro 5, statisk, ingen klientframework
Hosting     Cloudflare Pages, projekt "readmagasiner"
Deploy      push til feat/astro-skelet → automatisk preview
Byg         python3 scripts/seo_audit.py       # titler og meta på alle sider
npx astro build   (~2 s, 199 URL'er)
Git-ident   Hooah AI <346939773+hooah-ai@users.noreply.github.com>
```

Sider: forside, `/magasiner/`, 87 bladsider, `/tjenester/` + 4 tjenestesider,
`/sammenlign/`, `/soeg/`, `/om/`, `/design/` (styleguide, noindex).

## Data — kilder er sandhed

Udvalget bygges ikke på arv eller gæt. Tre lister er defineret som sandhed og ligger i
`data/kilder/`:

```
readly.json   21 titler   (Readlys danske grid)
pling.json    57 titler   (syv kategorisider på pling.dk)
flipp.json    93 titler   (flipp.dk/magasiner, 36 DK · 30 SE · 27 NO)
wype.json     13 titler   (wype.dk/online-magasiner)
```

`scripts/build_udvalg.py` gør listerne til data:

- titel på listen → `bekraeftet`
- titel uden for listen → `nej`

Alle fire tjenester har nu en liste, så "Ikke oplyst" findes ikke længere i udvalgstabellerne.

Den skriver `data/magasiner.json`, `data/availability.json`, `data/udvalg_taelling.json`
og opdaterer `data/tjenester.json` med totaler. Kør den efter enhver ændring i kilderne.

```
python3 scripts/build_udvalg.py          # lister → data
python3 scripts/prune_uden_tjeneste.py   # fjern blade uden for alle lister + 301
python3 scripts/seo_audit.py       # titler og meta på alle sider
npx astro build
```

## Design

Tokens i `src/styles/theme.css`: pine `#123B3A`, cream `#F8F7F3`, mint `#E4F1EB`,
guld `#F4B860`, DM Serif Display til overskrifter, Inter til UI, 8 px-skala.
Alle farvepar er kontrastverificeret mod WCAG AA — ændr dem ikke uden at regne efter.

Annoncer: Mofibo i tre formater via `data/annoncer.json` og `src/components/Annonce.astro`.
Trackinglink er Adtractions, mærket "Annonce", `rel="nofollow sponsored"`.

## Kendte mangler

```
40 blade uden forlag
/tjenester/, /soeg/, /om/    ikke bygget om til det nye designsystem
```

Alle 87 blade har et omslag. Blade der ikke findes hos nogen af de fire tjenester
findes ikke som sider — de 301'es til `/magasiner/` (se `scripts/prune_uden_tjeneste.py`).

## Næste skridt, i prioriteret rækkefølge

1. Skriv beskrivelser til de 21 nye sider — de er tomme nu, og tynde sider er et problem.
2. Byg `/tjenester/`, `/soeg/` og `/om/` om, så designsystemet dækker hele sitet.
3. Mål Core Web Vitals på mobil, før vi taler om at merge til `main`.
4. Først derefter: custom domain og DNS (kræver godkendelse).

## Skærmbilleder

Browserens enhedsemulering virker ikke i denne opsætning, og Chrome headless på Linux
nægter vinduer under 500 px. Brug CDP-klienten:

```
python3 /opt/data/cache/scratch/cdp_shot.py <url> <ud.png> 390 844 2
```

## Arbejdsregler for dette site

- Ingen opdigtede priser, datoer, stjerner eller erfaringer. Alt skal kunne henvises.
- Priser vises med dato for sidste tjek. Euro omregnes med kurs og dato.
- "Nej" betyder "står ikke på tjenestens liste" — ikke "bladet findes ikke".
- Nye sider: maks. 3 pr. uge pr. site, og kun hvis de har reelt indhold.
- Alt udgives gennem pull request med preview-link til Anders.
