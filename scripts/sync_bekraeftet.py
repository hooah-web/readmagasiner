#!/usr/bin/env python3
"""Synkroniserer magasiner[].digitalt_bekraeftet med availability.json.

availability.json er kilden til sandhed: står en tjeneste som "bekraeftet" på et
blad, skal bladet også stå i bladets digitalt_bekraeftet-liste. Ellers kan
tællingerne på tjenestesiderne og forsiden vise noget andet end det, vi faktisk
har verificeret.

Kør efter hver opdatering af udvalgsdata:

    python3 scripts/sync_bekraeftet.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TJENESTER = ["Readly", "Flipp", "Pling", "Wype"]


def main() -> None:
    mags = json.loads((ROOT / "data/magasiner.json").read_text(encoding="utf-8"))
    av = json.loads((ROOT / "data/availability.json").read_text(encoding="utf-8"))

    ændret = 0
    for m in mags:
        a = av.get(m["slug"], {})
        bekræftet = sorted(t for t in TJENESTER if a.get(t) == "bekraeftet")
        if (m.get("digitalt_bekraeftet") or []) != bekræftet:
            m["digitalt_bekraeftet"] = bekræftet
            ændret += 1

    (ROOT / "data/magasiner.json").write_text(
        json.dumps(mags, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    tælling = {t: sum(1 for m in mags if t in (m.get("digitalt_bekraeftet") or [])) for t in TJENESTER}
    print(f"opdateret: {ændret} blade")
    print("bekræftet pr. tjeneste:", tælling)


if __name__ == "__main__":
    main()
