#!/usr/bin/env python3
"""Omskriver bladbeskrivelser til en fast, nutidig struktur — uden at opfinde fakta.

Bruger OpenRouter. Kildeteksten er den gamle beskrivelse; modellen må kun
bruge det, der står der, og skal levere fire korte afsnit:
  1. Hvad er det for et blad
  2. Hvem er det til
  3. Hvad finder man i det
  4. (valgfrit) Udgivelse/frekvens, hvis kilden nævner det

Output skrives til data/rewritten.json som {slug: {"tekst": "...", "model": "..."}}
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "/opt/data/build/readmagasiner"
CATALOG = os.path.join(BASE, "data", "magasiner.json")
OUT = os.path.join(BASE, "data", "rewritten.json")
MODEL = "openai/gpt-4o-mini"

SYSTEM = """Du skriver korte, saglige beskrivelser af danske blade til et sammenligningssite.
Regler:
- Brug KUN oplysninger fra kildeteksten. Digt ikke nye fakta, priser, oplag eller udgivelsesfrekvens.
- Skriv på dansk, nutidigt og stramt. Ingen sælgende adjektiver, ingen "oplev magien".
- Struktur: 3-4 afsnit adskilt af en tom linje. Hvert afsnit 1-2 sætninger.
  1) Hvad bladet er. 2) Hvem det henvender sig til. 3) Hvad man finder i det.
  4) Kun hvis kilden nævner det: hvor ofte det udkommer.
- Maks 110 ord i alt. Ingen overskrifter, ingen punktopstilling, ingen markdown.
- Hvis kilden er meget kort, skriv kortere — find ikke på indhold."""


def env(name):
    for line in open("/opt/data/.env", encoding="utf-8"):
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"\'')
    return None


KEY = env("OPENROUTER_API_KEY")


def rewrite(item):
    if not item.get("beskrivelse") or len(item["beskrivelse"]) < 80:
        return None
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Blad: {item['navn']}\nKildetekst:\n{item['beskrivelse']}"},
        ],
        "temperature": 0.3,
        "max_tokens": 400,
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read().decode())
            txt = d["choices"][0]["message"]["content"].strip()
            return {"tekst": txt, "model": d.get("model", MODEL)}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503):
                time.sleep(3 * (attempt + 1))
                continue
            return {"fejl": f"HTTP {e.code}: {e.read().decode()[:120]}"}
        except Exception as e:
            time.sleep(2)
            if attempt == 2:
                return {"fejl": f"{type(e).__name__}: {str(e)[:80]}"}
    return {"fejl": "opgav efter 3 forsøg"}


def main(limit=None):
    if not KEY:
        print("OPENROUTER_API_KEY mangler")
        return 1
    catalog = json.load(open(CATALOG, encoding="utf-8"))
    done = {}
    if os.path.exists(OUT):
        done = json.load(open(OUT, encoding="utf-8"))

    todo = [m for m in catalog if m["slug"] not in done and m.get("beskrivelse")]
    if limit:
        todo = todo[:limit]
    print(f"skal omskrives: {len(todo)} (i alt {len(catalog)})")

    with ThreadPoolExecutor(max_workers=4) as pool:
        for item, res in zip(todo, pool.map(rewrite, todo)):
            if res and "tekst" in res:
                done[item["slug"]] = res
            elif res:
                done[item["slug"]] = res

    json.dump(done, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok = sum(1 for v in done.values() if "tekst" in v)
    print(f"færdige: {ok} | fejlede: {len(done) - ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else None))
