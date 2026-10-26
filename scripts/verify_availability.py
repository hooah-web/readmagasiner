#!/usr/bin/env python3
"""Verificerer hvilke blade tjenesterne faktisk har.

Maskinelt brugbare kilder:
  - Flipp: /magasiner/<slug> svarer 200 med titlen "<Blad> | Flipp" når bladet findes
  - Wype:  /online-magasiner/ lister et kurateret udvalg (13 titler)

Ikke brugbare:
  - Pling: ingen katalogside i sitemap, ingen gætbar URL-struktur
  - Readly: SPA, geo-omdirigerer vores server

Alt andet forbliver "ukendt". Vi gør aldrig fravær til et "nej".
"""

import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

BASE = "/opt/data/build/readmagasiner"
CATALOG = os.path.join(BASE, "data", "magasiner.json")
OUT = os.path.join(BASE, "data", "availability.json")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0 Safari/537.36")


def slugify(navn):
    s = navn.lower().strip()
    for a, b in (("æ", "ae"), ("ø", "oe"), ("å", "aa"), ("é", "e"), ("&", "og")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "da-DK,da;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", errors="replace")


def check_flipp(m):
    slugs = [slugify(m["navn"])]
    alt = re.sub(r"-og-", "-", slugs[0])
    if alt != slugs[0]:
        slugs.append(alt)
    for s in slugs:
        url = "https://flipp.dk/magasiner/" + s
        try:
            status, doc = fetch(url)
        except urllib.error.HTTPError:
            continue
        except Exception:
            return None
        if status == 200:
            t = re.search(r"<title>(.*?)</title>", doc, re.S)
            title = html.unescape(t.group(1)) if t else ""
            if m["navn"].lower()[:6] in title.lower() and "flipp" in title.lower():
                return url
    return False


def pling_list():
    """Pling viser danske og internationale brands på deres partner-sider."""
    slugs = set()
    for cat in ("danske-brands", "internationale-brands"):
        try:
            _, doc = fetch("https://pling.dk/partner-forside/" + cat + "/")
        except Exception:
            continue
        slugs |= set(re.findall(r'href="/partner-forside/' + cat + r'/([a-z0-9\-]+)/"', doc))
    return slugs


def _pling_key(slug):
    """Pling bruger '--' for '&' og udelader 'og'. Normaliser begge veje."""
    x = slug.replace("--", "-")
    x = re.sub(r"(^|-)og(-|$)", "-", x)
    return x.strip("-")


def wype_list():
    try:
        _, doc = fetch("https://wype.dk/online-magasiner/")
    except Exception:
        return set()
    return set(re.findall(r'href="(?:https://wype\.dk)?/online-magasiner/([a-z0-9\-]+)/?"', doc))


def main():
    catalog = json.load(open(CATALOG, encoding="utf-8"))
    wype = wype_list()
    print("Wype: %d titler offentliggjort" % len(wype))

    pling = pling_list()
    print("Pling: %d brands offentliggjort" % len(pling))

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(check_flipp, catalog))
    hits = {m["slug"]: r for m, r in zip(catalog, results) if r}
    print("Flipp: %d blade bekræftet via /magasiner/<slug>" % len(hits))

    pling_keys = {_pling_key(x) for x in pling}
    tjekket = datetime.now(timezone.utc).date().isoformat()
    avail = {}
    for m in catalog:
        bekr = []
        kilder = {}
        if m["slug"] in hits:
            bekr.append("Flipp")
            kilder["Flipp"] = hits[m["slug"]]
        if _pling_key(slugify(m["navn"])) in pling_keys:
            bekr.append("Pling")
            kilder["Pling"] = "https://pling.dk/partner-forside/danske-brands/"
        if slugify(m["navn"]) in wype:
            bekr.append("Wype")
            kilder["Wype"] = "https://wype.dk/online-magasiner/"
        m["digitalt_bekraeftet"] = sorted(bekr)
        m["kilder"] = kilder
        m["udvalg_tjekket"] = tjekket
        avail[m["slug"]] = {
            "Flipp": "bekraeftet" if "Flipp" in bekr else "ukendt",
            "Wype": "bekraeftet" if "Wype" in bekr else "ukendt",
            "Pling": "bekraeftet" if "Pling" in bekr else "ukendt",
            "Readly": "ukendt",
            "kilder": kilder,
            "tjekket": tjekket,
        }

    json.dump(catalog, open(CATALOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(avail, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    bekr = sum(1 for m in catalog if m["digitalt_bekraeftet"])
    print("blade med mindst én bekræftet tjeneste: %d af %d" % (bekr, len(catalog)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
