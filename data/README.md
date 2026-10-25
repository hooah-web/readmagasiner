# Katalogdata

`magasiner.json` — ét objekt pr. blad, konverteret fra WordPress-eksporten 25.10.2026.

| Felt | Betydning |
|---|---|
| `navn` | Bladets navn som det står i kilden |
| `slug` | Eksisterende URL-segment, fx `magasin-euroman` |
| `type` | `magasin` eller `ugeblad` |
| `forlag` | Udgiver, når kategorierne oplyser det (`null` = ikke oplyst) |
| `maalgruppe` | `kvinder`, `mænd`, `børn` — kun når kilden angiver det |
| `land` | `DK`, `SE` eller `NO` |
| `digitalt` | Tjenester der har bladet, jf. kildens kategorier |
| `ikke_digitalt` | Sand når kilden markerer bladet som ikke tilgængeligt digitalt |
| `beskrivelse` | Uddrag af kildeteksten, maks. 300 tegn |
| `kilde` | Oprindelig URL |
| `sidst_tjekket` | `null` indtil indholdet er verificeret |
| `ai_tekst` | Alt indhold er AI-skrevet eller AI-udvidet |

Kendte huller: 55 blade mangler forlag, 6 mangler tjenestemarkering, 2 har tom beskrivelse.
Det udfyldes ved verifikation mod forlagenes egne sider — ikke ved gæt.
