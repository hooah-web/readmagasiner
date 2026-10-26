#!/usr/bin/env python3
"""Bygger udvalget på de kilder, Anders har udpeget som sandheden.

Kilderne ligger i data/kilder/:
  readly.json  21 titler  (Readlys danske grid)
  pling.json   57 titler  (Plings syv kategorisider)
  flipp.json   93 titler  (flipp.dk/magasiner, med DK/NO/SE-præfiks i id)
  wype.json    13 titler  (wype.dk/online-magasiner)

Scriptet:
  1. matcher kildernes titler mod kataloget (normaliseret navn + manuelle koblinger)
  2. opretter katalogsider for danske titler, vi mangler
  3. sætter udvalget: bekræftet for titler på listen, "nej" for titler der ikke er
  4. henter forsidebillede til nye sider
  5. skriver magasiner.json, availability.json og data/udvalg_taelling.json

Kør:  python3 scripts/build_udvalg.py
"""
import json
import pathlib
import re
import subprocess
import unicodedata
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
TJENESTER = ["Readly", "Flipp", "Pling", "Wype"]
UA = "Mozilla/5.0 (compatible; readmagasiner/1.0)"
IDAG = "2026-10-26"

# Titler hvor kildens navn afviger fra katalogets
MANUELLE = {
    "Readly": {},
    "Pling": {
        "femina Denmark": "ugeblad-femina",
        "Antik & Auktion Denmark": "magasin-antik-auktion",
        "BILLED-BLADET Royal": "ugeblad-royal",
    },
    "Flipp": {},
    "Wype": {},
}

# Danske Pling-titler der ikke findes i kataloget i forvejen
NYE_PLING = {"INDRET by femina DK", "Magasinet Lækkerier", "Ekstra Bladet"}


def unesc(s: str) -> str:
    return (
        s.replace("\\u0026", "&")
        .replace("\\u0027", "'")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
    )


def norm(s: str) -> str:
    s = unesc(s)
    s = re.sub(r"\s*\((DK|NO|SE)\)\s*$", "", s)
    s = re.sub(r"\s+(DK|Denmark)$", "", s)
    s = s.replace("–", "-").replace("—", "-")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())


def slugify(s: str) -> str:
    s = unesc(s).replace("&", "og").replace("–", "-")
    # æ/ø/å nedbrydes ikke af NFKD — oversæt dem først, ellers bliver de bindestrenge
    s = s.replace("æ", "ae").replace("Æ", "Ae").replace("ø", "oe").replace("Ø", "Oe")
    s = s.replace("å", "aa").replace("Å", "Aa")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def hent_cover(url: str, slug: str) -> str | None:
    out = ROOT / f"public/omslag/{slug}.webp"
    if out.exists():
        return f"/omslag/{slug}.webp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        tmp = pathlib.Path("/tmp/cover_dl")
        tmp.write_bytes(data)
        p = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp),
             "-vf", "scale=440:-1:flags=lanczos", "-quality", "84", str(out)],
            capture_output=True,
        )
        return f"/omslag/{slug}.webp" if p.returncode == 0 else None
    except Exception:
        return None


def main() -> None:
    mags = json.loads((ROOT / "data/magasiner.json").read_text(encoding="utf-8"))
    av = json.loads((ROOT / "data/availability.json").read_text(encoding="utf-8"))
    kilder = {
        t: json.loads((ROOT / f"data/kilder/{t.lower()}.json").read_text(encoding="utf-8"))
        for t in ("readly", "pling", "flipp", "wype")
    }
    kildenavn = {"readly": "Readly", "pling": "Pling", "flipp": "Flipp", "wype": "Wype"}

    by_norm = {}
    for m in mags:
        by_norm.setdefault(norm(m["navn"]), m)

    nye = 0
    udvalg: dict[str, set[str]] = {t: set() for t in ("Readly", "Pling", "Flipp", "Wype")}
    ubesvarede = {"Readly": [], "Pling": [], "Flipp": [], "Wype": []}

    for key, liste in kilder.items():
        tjen = kildenavn[key]
        for post in liste:
            navn = unesc(post["navn"])
            slug = MANUELLE[tjen].get(navn)
            m = by_norm.get(norm(navn))
            if slug:
                m = next((x for x in mags if x["slug"] == slug), None)
            if m is None and (
                (key == "pling" and navn in NYE_PLING)
                or (key == "flipp" and post["id"].startswith("DK"))
            ):
                slug = "magasin-" + slugify(navn)
                if any(x["slug"] == slug for x in mags):
                    slug += "-2"
                m = {
                    "navn": navn,
                    "slug": slug,
                    "forlag": None,
                    "type": "magasin",
                    "land": "DK",
                    "digitalt": [],
                    "digitalt_bekraeftet": [],
                    "ikke_digitalt": False,
                    "beskrivelse": None,
                }
                mags.append(m)
                by_norm[norm(navn)] = m
                nye += 1
            if m is None:
                ubesvarede[tjen].append(navn)
                continue
            udvalg[tjen].add(m["slug"])
            if not m.get("cover"):
                c = hent_cover(unesc(post["cover"]), m["slug"])
                if c:
                    m["cover"] = c
                    m["cover_kilde"] = tjen

    # udvalget pr. blad
    for m in mags:
        a = av.setdefault(m["slug"], {})
        kilder_map = a.setdefault("kilder", {})
        for tjen in ("Readly", "Pling", "Flipp", "Wype"):
            a[tjen] = "bekraeftet" if m["slug"] in udvalg[tjen] else "nej"
        a["tjekket"] = IDAG
        m["digitalt"] = sorted(t for t in TJENESTER if a.get(t) == "bekraeftet")
        m["digitalt_bekraeftet"] = list(m["digitalt"])

    (ROOT / "data/magasiner.json").write_text(json.dumps(mags, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "data/availability.json").write_text(json.dumps(av, ensure_ascii=False, indent=1), encoding="utf-8")

    taelling = {
        "total": {t: len(kilder[t.lower()]) for t in udvalg},
        "med_katalogside": {t: len(v) for t, v in udvalg.items()},
        "danske": {t: sum(1 for s in v if next(x for x in mags if x["slug"] == s).get("land") == "DK") for t, v in udvalg.items()},
        "kilder": {t: len(kilder[k]) for k, t in kildenavn.items()},
        "udenlandske": {t: len(kilder[k]) - sum(1 for s in udvalg[t] if next(x for x in mags if x["slug"] == s).get("land") == "DK") for k, t in kildenavn.items()},
        "tjekket": IDAG,
    }
    (ROOT / "data/udvalg_taelling.json").write_text(json.dumps(taelling, ensure_ascii=False, indent=1), encoding="utf-8")

    # hold tjenesteinfo i takt med listerne
    tj_path = ROOT / "data/tjenester.json"
    tj = json.loads(tj_path.read_text(encoding="utf-8"))
    for navn in ("Readly", "Pling", "Flipp", "Wype"):
        key = navn.lower()
        tj[key]["udvalg_i_alt"] = taelling["total"][navn]
        tj[key]["udenlandske_oplyst"] = taelling["udenlandske"][navn]
    tj_path.write_text(json.dumps(tj, ensure_ascii=False, indent=1), encoding="utf-8")

    print("nye katalogsider:", nye, "| katalog i alt:", len(mags))
    for t in ("Readly", "Pling", "Flipp", "Wype"):
        print(f"  {t:8} kilde={len(kilder[t.lower()]):>3}  danske={taelling['danske'][t]:>3}  "
              f"udenlandske={taelling['udenlandske'][t]:>3}  uden katalogside={len(ubesvarede[t])}")
    print("blade med omslag:", sum(1 for m in mags if m.get("cover")), "/", len(mags))


if __name__ == "__main__":
    main()
