# Beslutninger — readmagasiner.dk

Hvad vi har besluttet, hvornår, og hvorfor. Skriv her når en beslutning træffes i dialog,
så den ikke skal genopdages. Nyeste først.

---

## 26. oktober 2026

**Tjenesternes egne lister er sandheden for udvalget.**
Readly 21 titler, Pling 57, Flipp 93. Titler på listen = "Ja · bekræftet", titler uden for
listen = "Nej". Wype undtaget indtil vi har en fuld liste fra dem.
*Hvorfor:* Anders udpegede listerne som sandhed. Før arvede vi flag fra det gamle site, og
tallene passede ikke (Readly stod med 71).
*Ligger i:* `data/kilder/*.json`, `scripts/build_udvalg.py`.

**Wypes liste er også sandhed — 13 titler.**
`wype.dk/online-magasiner` viser 13 danske titler. Dermed har alle fire tjenester en
komplet liste, og "Ikke oplyst" er afskaffet som svar.
*Hvorfor:* Anders udpegede siden som sandheden. Før stod Wype som "ukendt" overalt, fordi vi
kun havde delvise data.

**Ekstra Bladet er med som side, selvom det er en avis.**
*Hvorfor:* Den står på Plings liste, og et "nej" er et dårligere svar end en side.
*Ligger i:* `data/magasiner.json` (slug `magasin-ekstra-bladet`).

**Forsider hentes fra tjenesternes CDN og gemmes lokalt.**
440 px webp, ~50 kB pr. styk, i `public/omslag/`.
*Hvorfor:* Hotlinks knækker hvis tjenesten skifter CDN, og vi vil styre cache og størrelse.
Har vi ikke et rigtigt omslag, vises et farvet omslag med titlen i serif.

**"Nej" må skrives, når listerne er komplette.**
Tidligere regel var at vi aldrig skrev "Nej" uden udtrykkelig dokumentation. Med de tre
lister er fraværet dokumentationen.
*Konsekvens:* Teksten på bladsiderne blev ændret, så den forklarer, at "Nej" betyder
"står ikke på tjenestens liste".

**Dagbog og STATUS.md er fast rutine.**
Én post pr. arbejdsfase, ugentlig automatisk kørsel fredag kl. 15:30 for alle repos.
*Hvorfor:* En ny session skal kunne sætte sig ind i projektet på minutter.

---

## 25. oktober 2026

**Designretningen er Anders' mockup, ikke det første CVI-forslag.**
Pine `#123B3A`, cream `#F8F7F3`, mint `#E4F1EB`, guld `#F4B860`, DM Serif Display til
overskrifter, Inter til UI.
*Hvorfor:* Mockuppen føltes som et redaktionelt forbrugerværktøj; det første forslag lignede
en generisk affiliateblog. Alle farvepar er kontrastverificeret mod WCAG AA.

**Kun danske udgivelser er i fokus.**
Udenlandske titler nævnes som tal pr. tjeneste, ikke som sider.
*Hvorfor:* "Vi fokuserer kun på de danske. Så ok, at vi ikke er specifikke på de udenlandske."

**Ingen tekst om "det tidligere website".**
Vi står ved den nuværende løsning. Ingen sætninger om arv, overtagelse eller gamle data.
*Hvorfor:* Anders' korrektion: "Vi skal stå ved vores nuværende løsning."

**Affiliate-links peger direkte på tjenesterne.**
De gamle redirect-URL'er 301'es til vores egen tjenesteside, så de ~59.000 registrerede
klik ikke går tabt.
*Hvorfor:* Der var ingen indtægt i de gamle links.

**AI-mærkning overalt.**
Sitet er bygget, skrevet og drevet af en AI. Det står i footer og på Om-siden, i tonen uden
undskyldning. Vi påstår aldrig at have læst, testet eller abonneret.

**Annonceformater: 300×600 sticky i rail, 930×180 i flow, 300×250 på mobil.**
Maks. to enheder pr. side, fast reserveret højde mod layoutskift, "Annonce"-mærkning og
`rel="nofollow sponsored"`. Vises kun i produktion.

**Priser: ordinær pris er den store, kampagne den lille.**
Readly opkræver i euro, så vi viser euro og omregnet kroner med kurs og dato.
*Hvorfor:* Pling viste "0 kr." som hovedpris — det var første måneds pris.

**Navnet er readmagasiner.dk.**
Wordmark i tekst plus et enkelt symbol til favicon. Ikke MagasinFinder.

**Konkurrenten er abonnement.dk.**
Målet er bedre placeringer i Google gennem præcision om udvalg og priser. Derfor tjekkes
priser løbende, og hver pris viser dato for sidste kontrol.

---

## Sådan træffes beslutninger her

- Anders godkender udgivelser, DNS, nye sider og større redesign.
- Er jeg i tvivl om niveauet, behandler jeg det som det næste niveau op.
- Beslutninger der træffes i dialog skal skrives her samme dag — ellers findes de ikke
  i næste session.
