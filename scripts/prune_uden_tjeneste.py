#!/usr/bin/env python3
"""Fjerner katalogsider for blade, der ikke findes hos nogen af de fire tjenester.

Udvalget bygges på tjenesternes egne lister (se build_udvalg.py). Blade uden for alle
fire lister har ingen værdi for læseren: de kan kun sige "findes ingen steder", og de
svækker resten af sitet. Derfor fjernes de, og deres URL'er 301'es til kataloget.

Kør efter build_udvalg.py, når listerne er opdateret:

    python3 scripts/prune_uden_tjeneste.py [--torrkoer]
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REDIRECTS = ROOT / "public/_redirects"
MARKER = "# Blade uden for alle fire tjenestelister — 301 til kataloget"


def main() -> None:
    torrkoer = "--torrkoer" in sys.argv

    mags = json.loads((ROOT / "data/magasiner.json").read_text(encoding="utf-8"))
    av = json.loads((ROOT / "data/availability.json").read_text(encoding="utf-8"))

    behold = [m for m in mags if m.get("digitalt")]
    fjern = [m for m in mags if not m.get("digitalt")]

    med_print = [m for m in fjern if m.get("print")]
    print(f"katalog: {len(mags)} → {len(behold)}  (fjerner {len(fjern)})")
    if med_print:
        print("  advarsel — disse har print-aftale og fjernes også:",
              ", ".join(m["navn"] for m in med_print))

    if torrkoer:
        print("\n(tørkørsel — intet skrevet)")
        for m in fjern[:40]:
            print(f"  /{m['slug']}/ → /magasiner/")
        return

    for m in fjern:
        av.pop(m["slug"], None)

    (ROOT / "data/magasiner.json").write_text(
        json.dumps(behold, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "data/availability.json").write_text(
        json.dumps(av, ensure_ascii=False, indent=1), encoding="utf-8")

    linjer = [MARKER]
    for m in sorted(fjern, key=lambda x: x["slug"]):
        linjer.append(f"/{m['slug']}/  /magasiner/  301")
        linjer.append(f"/{m['slug']}   /magasiner/  301")

    eksisterende = REDIRECTS.read_text(encoding="utf-8") if REDIRECTS.exists() else ""
    if MARKER in eksisterende:
        hoved, _, _ = eksisterende.partition(MARKER)
        eksisterende = hoved
    REDIRECTS.write_text(eksisterende.rstrip() + "\n\n" + "\n".join(linjer) + "\n", encoding="utf-8")

    print(f"skrev {len(linjer) - 1} redirect-regler til public/_redirects")


if __name__ == "__main__":
    main()
