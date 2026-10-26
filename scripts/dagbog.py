#!/usr/bin/env python3
"""Skriver en ny post øverst i docs/DAGBOG.md.

Bruges ved afslutningen af en arbejdsfase — ikke pr. kommando. Posten skal svare på
tre ting: hvad blev ændret, hvad blev besluttet, hvad mangler der stadig.

Eksempler
---------
    # brødtekst fra en fil
    python3 scripts/dagbog.py --titel "Wypes udvalg hentet" --fil /tmp/post.md

    # brødtekst fra stdin (husk at afslutte med Ctrl-D)
    python3 scripts/dagbog.py --titel "Rettet prisfejl" <<'EOF'
    - Pling stod med 0 kr. som hovedpris ...
    EOF

    # se resultatet uden at skrive
    python3 scripts/dagbog.py --titel "Test" --fil /tmp/post.md --torrkoer
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STANDARD = ROOT / "docs/DAGBOG.md"
SEPARATOR = "\n---\n"

MÅNEDER = ["januar", "februar", "marts", "april", "maj", "juni", "juli",
           "august", "september", "oktober", "november", "december"]


def dansk_dato(d: dt.date) -> str:
    """26. oktober 2026 — strftime giver engelske månedsnavne i denne container."""
    return f"{d.day}. {MÅNEDER[d.month - 1]} {d.year}"


def skriv(post: str, sti: pathlib.Path) -> str:
    tekst = sti.read_text(encoding="utf-8")
    if SEPARATOR not in tekst:
        raise SystemExit(f"{sti} har ikke en '---'-separator efter headeren")

    header, rest = tekst.split(SEPARATOR, 1)
    nyt = f"{header}{SEPARATOR}\n{post.strip()}\n{SEPARATOR}{rest.lstrip(chr(10))}"
    sti.write_text(nyt.rstrip() + "\n", encoding="utf-8")
    return nyt


def main() -> None:
    p = argparse.ArgumentParser(description="Skriv en post i dagbogen")
    p.add_argument("--titel", required=True, help="kort overskrift, fx 'Wypes udvalg hentet'")
    p.add_argument("--dato", help="ISO-dato, standard er i dag")
    p.add_argument("--fil", help="fil med brødtekst (markdown). Udelades: læs stdin")
    p.add_argument("--sti", default=str(STANDARD), help="dagbogsfil (til test)")
    p.add_argument("--torrkoer", action="store_true", help="vis resultatet, skriv intet")
    a = p.parse_args()

    krop = pathlib.Path(a.fil).read_text(encoding="utf-8") if a.fil else sys.stdin.read()
    if not krop.strip():
        raise SystemExit("tom brødtekst — der er ikke noget at skrive")

    dato = a.dato or dt.date.today().isoformat()
    dansk = dansk_dato(dt.date.fromisoformat(dato))

    post = f"## {dansk} — {a.titel}\n\n{krop.strip()}\n"
    sti = pathlib.Path(a.sti)

    if a.torrkoer:
        print(f"--- ville skrive til {sti} ---\n")
        print(post)
        return

    skriv(post, sti)
    print(f"skrev post i {sti}: {a.titel}")


if __name__ == "__main__":
    main()
