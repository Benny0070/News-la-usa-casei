"""
Aduce stiri din ultimele ~2 zile pe cateva domenii de interes, prin Google News RSS,
traduce titlul si un scurt rezumat in romana (pentru sursele in engleza) si scrie
totul in news.json, care e citit apoi de index.html.

Ruleaza automat zilnic prin .github/workflows/update-news.yml (GitHub Actions),
gratuit, fara cheie API si fara cont Claude.
"""

import datetime
import html
import json
import re

import feedparser
from deep_translator import GoogleTranslator

# Fiecare categorie = un feed RSS Google News.
# "translate": True inseamna ca sursa e in engleza si trebuie tradusa in romana.
FEEDS = {
    "ro_politica": {
        "label": "Politică România",
        "url": "https://news.google.com/rss/search?q=politica+Romania+when:2d&hl=ro&gl=RO&ceid=RO:ro",
        "translate": False,
    },
    "economie": {
        "label": "Economie / Business",
        "url": "https://news.google.com/rss/search?q=economie+business+when:2d&hl=ro&gl=RO&ceid=RO:ro",
        "translate": False,
    },
    "tech": {
        "label": "Tehnologie",
        "url": "https://news.google.com/rss/search?q=technology+when:2d&hl=en-US&gl=US&ceid=US:en",
        "translate": True,
    },
    "international": {
        "label": "Internațional",
        "url": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en",
        "translate": True,
    },
    "sport": {
        "label": "Sport",
        "url": "https://news.google.com/rss/search?q=sport+when:2d&hl=ro&gl=RO&ceid=RO:ro",
        "translate": False,
    },
    "politica_mondiala": {
        "label": "Politică mondială",
        "url": "https://news.google.com/rss/search?q=world+politics+when:2d&hl=en-US&gl=US&ceid=US:en",
        "translate": True,
    },
}

MAX_PER_CATEGORY = 15
TRANSLATE_CHAR_LIMIT = 450  # limita practica a traducatorului gratuit per apel
RUN_COUNTER_FILE = "run_count.txt"


def next_run_number():
    try:
        with open(RUN_COUNTER_FILE, "r", encoding="utf-8") as f:
            current = int(f.read().strip() or "0")
    except (FileNotFoundError, ValueError):
        current = 0
    new_value = current + 1
    with open(RUN_COUNTER_FILE, "w", encoding="utf-8") as f:
        f.write(str(new_value))
    return new_value


def clean_html(raw):
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def safe_translate(text, translator):
    if not text:
        return ""
    try:
        return translator.translate(text[:TRANSLATE_CHAR_LIMIT])
    except Exception:
        # daca traducerea pica (limita atinsa, retea etc.), pastram originalul
        # ca sa nu pierdem stirea din pagina
        return text


def main():
    translator = GoogleTranslator(source="auto", target="ro")
    all_items = {}

    for key, cfg in FEEDS.items():
        feed = feedparser.parse(cfg["url"])
        items = []
        for entry in feed.entries[:MAX_PER_CATEGORY]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "")
            source = ""
            src = entry.get("source")
            if src is not None:
                source = getattr(src, "title", "") or (src.get("title", "") if isinstance(src, dict) else "")
            summary_raw = clean_html(entry.get("summary", ""))
            published = entry.get("published", "")

            if cfg["translate"]:
                title_ro = safe_translate(title, translator)
                summary_ro = safe_translate(summary_raw, translator)
            else:
                title_ro = title
                summary_ro = summary_raw

            items.append(
                {
                    "title": title,
                    "title_ro": title_ro,
                    "summary_ro": summary_ro,
                    "link": link,
                    "source": source,
                    "published": published,
                }
            )
        all_items[key] = items

    output = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "run_number": next_run_number(),
        "categories": {k: {"label": v["label"]} for k, v in FEEDS.items()},
        "items": all_items,
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in all_items.values())
    print(f"Scrise {total} stiri in news.json")


if __name__ == "__main__":
    main()
