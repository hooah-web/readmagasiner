#!/usr/bin/env python3
"""Fjerner katalogsider, der ikke skal være der.

To regler:

1. Blade uden for alle fire tjenestelister. De kan kun sige "findes ingen steder".
2. Blade der ikke er danske. Vi fokuserer på det danske udvalg; udenlandske titler
   nævnes som tal på tjenestesiderne, ikke som sider.

URL'erne 301'es til /magasiner/. Redirect-blokken genopbygges, men regler fra tidligere
kørsler bevares, så de ikke forsvinder når nye kommer til.

    python3 scripts/prune_uden_tjeneste.py [--torrkoer]
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REDIRECTS = ROOT / "public/_redirects"
MARKER = "# Katalogsider der er fjernet — 301 til kataloget"


def eksisterende_regler(tekst: str) -> list[str]:
    """Behold redirect-linjer fra tidligere kørsler, så de ikke tabes."""
    return [l.strip() for l in tekst.splitlines() if l.startswith("/") and "301" in l]


def main() -> None:
    torrkoer = "--torrkoer" in sys.argv

    mags = json.loads((ROOT / "data/magasiner.json").read_text(encoding="utf-8"))
    av = json.loads((ROOT / "data/availability.json").read_text(encoding="utf-8"))

    def skal_væk(m: dict) -> bool:
        return (not m.get("digitalt")) or m.get("land") != "DK"

    behold = [m for m in mags if not skal_væk(m)]
    fjern = [m for m in mags if skal_væk(m)]
    udenlandsk = [m for m in fjern if m.get("digitalt")]

    print(f"katalog: {len(mags)} → {len(behold)}  (fjerner {len(fjern)}, "
          f"heraf {len(udenlandsk)} udenlandske med tjeneste)")

    if torrkoer:
        print("\n(tørkørsel — intet skrevet)")
        for m in fjern:
            print(f"  /{m['slug']}/ → /magasiner/")
        return

    for m in fjern:
        av.pop(m["slug"], None)

    (ROOT / "data/magasiner.json").write_text(
        json.dumps(behold, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "data/availability.json").write_text(
        json.dumps(av, ensure_ascii=False, indent=1), encoding="utf-8")

    tekst = REDIRECTS.read_text(encoding="utf-8") if REDIRECTS.exists() else ""
    regler = set(eksisterende_regler(tekst))
    for m in fjern:
        regler.add(f"/{m['slug']}/  /magasiner/  301")
        regler.add(f"/{m['slug']}   /magasiner/  301")

    hoved = tekst.split(MARKER, 1)[0].rstrip()
    krop = "\n".join([MARKER] + sorted(regler))
    REDIRECTS.write_text((hoved + "\n\n" if hoved else "") + krop + "\n", encoding="utf-8")

    print(f"redirects i alt: {len(regler)}")
    print("danske blade tilbage:", sum(1 for m in behold if m.get("land") == "DK"))


if __name__ == "__main__":
    main()
