#!/usr/bin/env python3
"""Laver 301-regler for de URL'er, den gamle WordPress-side havde.

Kilden er WXR-eksporten (content_index.json), som indeholder alle 240 offentliggjorte
indlæg og sider. Uden disse regler ville de gamle URL'er give 404 den dag domænet
flyttes, og den trafik ville være tabt.

Reglerne lægges i public/_redirects under en markør, så de kan genberegnes.

    python3 scripts/gamle_urls.py [--torrkoer]
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REDIRECTS = ROOT / "public/_redirects"
KILDE = pathlib.Path("/opt/data/cache/scratch/readmagasiner/content_index.json")
MARKER = "# Gamle WordPress-URL'er — 301 til nærmeste side på det nye site"

# Rækkefølgen betyder noget: første match vinder
REGLER = [
    ("alternativ", "/sammenlign/"),
    ("sammenlign", "/sammenlign/"),
    ("flipp", "/tjenester/flipp/"),
    ("pling", "/tjenester/pling/"),
    ("readly", "/tjenester/readly/"),
    ("wype", "/tjenester/wype/"),
    ("pris", "/sammenlign/"),
    ("anmeldelse", "/tjenester/"),
    ("test", "/tjenester/"),
    ("udvalg", "/magasiner/"),
    ("magasin", "/magasiner/"),
    ("avis", "/om/"),
    ("podcast", "/om/"),
    ("ordbog", "/om/"),
    ("kontakt", "/om/"),
]


def find_maal(sti: str, magasiner: dict[str, str], eksisterende: set[str]) -> str:
    if sti in eksisterende:
        return f"/{sti}/"
    # 1) findes bladet som side?
    for kandidat in (f"magasin-{sti}", f"ugeblad-{sti}", f"blad-{sti}"):
        if kandidat in magasiner:
            return f"/{kandidat}/"
    # 2) nøgleord
    for noegle, maal in REGLER:
        if noegle in sti:
            return maal
    # 3) sammensatte bladnavne, fx danske-skaebner-eventyr
    dele = set(sti.split("-"))
    bedst, score = None, 0
    for slug in magasiner:
        uden_praefiks = slug.split("-", 1)[1] if "-" in slug else slug
        s = len(dele & set(uden_praefiks.split("-")))
        if s > score:
            bedst, score = slug, s
    if bedst and score >= 2:
        return f"/{bedst}/"
    return "/magasiner/"


def main() -> None:
    torrkoer = "--torrkoer" in sys.argv
    mags = json.loads((ROOT / "data/magasiner.json").read_text(encoding="utf-8"))
    magasiner = {m["slug"]: m["navn"] for m in mags}

    gamle = []
    for post in json.loads(KILDE.read_text(encoding="utf-8")):
        sti = post["link"].replace("https://readmagasiner.dk", "").strip("/")
        if sti:
            gamle.append(sti)

    sider = {p.parent.relative_to(ROOT / "dist").as_posix() for p in (ROOT / "dist").glob("*/index.html")}
    eksisterende = {p for p in sider if p and p != "."}

    linjer, fordeling = [], {}
    for sti in sorted(set(gamle)):
        if sti in eksisterende:
            continue
        maal = find_maal(sti, magasiner, eksisterende)
        fordeling[maal] = fordeling.get(maal, 0) + 1
        linjer.append(f"/{sti}/  {maal}  301")
        linjer.append(f"/{sti}   {maal}  301")

    print(f"gamle URL'er: {len(set(gamle))} · regler: {len(linjer)//2}")
    for maal, antal in sorted(fordeling.items(), key=lambda x: -x[1]):
        print(f"  {maal:24} {antal}")

    if torrkoer:
        print("\n(tørkørsel — intet skrevet)")
        for l in linjer[:20]:
            print("  " + l)
        return

    # korte aliaser: /hjemmet/ → /ugeblad-hjemmet/, så gamle links og gæt virker
    alias = []
    for slug in magasiner:
        kort = slug.split("-", 1)[1] if "-" in slug else slug
        if kort and kort not in eksisterende and f"/{kort}" not in {l.split()[0].rstrip("/") for l in linjer}:
            alias.append(f"/{kort}/  /{slug}/  301")
            alias.append(f"/{kort}   /{slug}/  301")
    print(f"korte aliaser: {len(alias)//2}")
    linjer += alias

    tekst = REDIRECTS.read_text(encoding="utf-8") if REDIRECTS.exists() else ""
    hoved = tekst.split(MARKER, 1)[0].rstrip()
    REDIRECTS.write_text(hoved + "\n\n" + MARKER + "\n" + "\n".join(linjer) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
