#!/usr/bin/env python3
"""Verificerer hvilke blade tjenesterne faktisk har — så langt det er muligt.

Ingen af de fire tjenester udstiller hele deres katalog maskinlæsbart:
  - Wype: /online-magasiner/ viser et kurateret udvalg (13 titler), ikke hele kataloget
  - Pling: sitemap indeholder partner- og brand-sider, ikke hele udvalget
  - Flipp: ingen katalogside, ingen sitemap
  - Readly: SPA, geo-omdirigerer vores server

Derfor kan vi kun *bekræfte* det, vi finder på tjenestens egen side. Alt andet
forbliver "ukendt" — vi gør aldrig fravær til et "nej".

Output: data/availability.json
  { "<slug>": { "wype": "bekraeftet"|"ukendt", ... , "kilder": {...}, "tjekket": "..." } }
"""

import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0 Safari/537.36")
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(BASE, "data", "magasiner.json")
OUT = os.path.join(BASE, "data", "availability.json")

SOURCES = {
    "Wype": {
        "url": "https://wype.dk/online-magasiner/",
        "pattern": r'href="(?:https://wype\.dk)?/online-magasiner/([a-z0-9\-]+)/?"',
    },
    "Pling": {
        "url": "https://pling.dk/index-sitemap.xml",
        "pattern": r"<loc>https://pling\.dk/partner-forside/(?:internationale-brands/)?([a-z0-9\-]+)/</loc>",
    },
}


def norm(s: str) -> str:
    s = s.lower().strip()
    for a, b in (("æ", "ae"), ("ø", "oe"), ("å", "aa"), ("é", "e"), ("&", "og")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]", "", s)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "da-DK,da;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def main():
    catalog = json.load(open(CATALOG, encoding="utf-8"))
    slugs = {norm(re.sub(r"^(magasin|ugeblad)-", "", c["slug"])): c["slug"] for c in catalog}

    result = {c["slug"]: {"kilder": {}} for c in catalog}
    found_total = {}

    for service, cfg in SOURCES.items():
        try:
            doc = fetch(cfg["url"])
        except Exception as e:
            print(f"{service}: kunne ikke hentes ({type(e).__name__})")
            continue
        found = sorted(set(re.findall(cfg["pattern"], doc)))
        found_total[service] = found
        matched = 0
        for f in found:
            key = norm(f)
            slug = slugs.get(key)
            if slug:
                result[slug][service] = "bekraeftet"
                result[slug]["kilder"][service] = cfg["url"]
                matched += 1
        print(f"{service}: {len(found)} titler på kilden, {matched} matcher kataloget")

    tjekket = datetime.now(timezone.utc).date().isoformat()
    for slug, v in result.items():
        for s in SOURCES:
            v.setdefault(s, "ukendt")
        v["tjekket"] = tjekket

    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    bekr = sum(1 for v in result.values() if any(v.get(s) == "bekraeftet" for s in SOURCES))
    print(f"\nblade med mindst én bekræftet tjeneste: {bekr} af {len(result)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
