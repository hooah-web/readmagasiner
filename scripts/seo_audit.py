#!/usr/bin/env python3
"""SEO-gennemgang af det byggede site.

Tjekker titler og meta-beskrivelser på alle sider i dist/:
- titel maks 60 tegn
- beskrivelse 130-158 tegn
- ingen dubletter
- rapporterer noindex-sider

    python3 scripts/seo_audit.py
"""
from __future__ import annotations

import collections
import glob
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def hoved(tekst: str, mønster: str) -> str:
    m = re.search(mønster, tekst, re.S)
    return html.unescape(m.group(1)) if m else ""


def main() -> int:
    sider = []
    for sti in glob.glob(str(ROOT / "dist/**/index.html"), recursive=True):
        tekst = pathlib.Path(sti).read_text(encoding="utf-8")
        sti_kort = sti.replace(str(ROOT / "dist"), "").replace("/index.html", "") or "/"
        sider.append({
            "sti": sti_kort,
            "titel": hoved(tekst, r"<title>(.*?)</title>"),
            "beskrivelse": hoved(tekst, r'<meta name="description" content="(.*?)"'),
            "noindex": "noindex" in tekst,
        })

    indekserbare = [s for s in sider if not s["noindex"]]
    print(f"sider: {len(sider)} · indekserbare: {len(indekserbare)}")

    for navn, felt, lav, høj in (
        ("titel", "titel", 0, 60),
        ("beskrivelse", "beskrivelse", 130, 158),
    ):
        forventet = indekserbare if navn == "titel" else indekserbare
        forkerte = [s for s in forventet if not lav <= len(s[felt]) <= høj]
        print(f"{navn:12} uden for {lav}-{høj} tegn: {len(forkerte)}")
        for s in forkerte:
            print(f"   {s['sti']:28} {len(s[felt]):>3}  {s[felt][:90]}")

    for felt in ("titel", "beskrivelse"):
        tælling = collections.Counter(s[felt] for s in indekserbare)
        dubletter = [k for k, v in tælling.items() if v > 1]
        print(f"{felt:12} dubletter: {len(dubletter)}")
        for d in dubletter[:3]:
            print(f"   {d[:80]}")

    noindex = [s["sti"] for s in sider if s["noindex"]]
    print("noindex:", noindex or "ingen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
