"""Konu için kaynak toplar: Wikipedia (tr + en) özeti + web araması + sayfa metni. Kredisiz.

Kullanım:
  .venv/bin/python scripts/research.py "Lake Peigneur" [--n 5] > kaynaklar.md

Çıktı yalnızca ham malzemedir: iddiaları en az iki bağımsız kaynakla doğrula, kaynakça kartına yalnızca
gerçekten kullandığın kaynakları yaz.
"""
import argparse

import trafilatura
import wikipediaapi
from ddgs import DDGS

UA = "megerse-reels/1.0 (research script)"

p = argparse.ArgumentParser()
p.add_argument("topic")
p.add_argument("--n", type=int, default=5)
a = p.parse_args()

for lang in ("tr", "en"):
    page = wikipediaapi.Wikipedia(user_agent=UA, language=lang).page(a.topic)
    if page.exists():
        print(f"## Wikipedia ({lang}): {page.title}\n{page.fullurl}\n\n{page.summary[:1500]}\n")

print("## Web\n")
for r in DDGS().text(a.topic, max_results=a.n):
    print(f"### {r['title']}\n{r['href']}\n")
    html = trafilatura.fetch_url(r["href"])
    body = trafilatura.extract(html) if html else None
    print((body or r.get("body", ""))[:1200], "\n")
