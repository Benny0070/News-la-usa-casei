"""
Aduce stiri din ultimele ~2 zile pe zeci de categorii, prin Google News RSS,
traduce in romana ce vine in engleza si scrie totul in news.json, care e citit
de index.html. Ruleaza automat zilnic prin GitHub Actions.

Ca sa adaugi o categorie noua, adauga o linie in lista CATEGORIES de mai jos.
"""

import datetime
import html
import json
import re
import time
from urllib.parse import quote_plus

import feedparser
from deep_translator import GoogleTranslator

RO = "hl=ro&gl=RO&ceid=RO:ro"
EN = "hl=en-US&gl=US&ceid=US:en"


def ro(query):
    """Cautare in presa romaneasca, ultimele 2 zile."""
    return f"https://news.google.com/rss/search?q={quote_plus(query + ' when:2d')}&{RO}"


def en(query):
    """Cautare in presa internationala (engleza), ultimele 2 zile; se traduce in romana."""
    return f"https://news.google.com/rss/search?q={quote_plus(query + ' when:2d')}&{EN}"


WORLD_TOPIC = f"https://news.google.com/rss/headlines/section/topic/WORLD?{EN}"

# (cheie, eticheta afisata, grup, url, de_tradus, implicit_activa)
CATEGORIES = [
    # --- Actualitate & Politică ---
    ("ro_politica", "Politică România", "Actualitate & Politică", ro("politica Romania"), False, True),
    ("politica_mondiala", "Politică mondială", "Actualitate & Politică", en("world politics"), True, True),
    ("international", "Internațional", "Actualitate & Politică", WORLD_TOPIC, True, True),
    ("ue", "Uniunea Europeană", "Actualitate & Politică", ro("Uniunea Europeană Bruxelles"), False, False),
    ("sua", "SUA", "Actualitate & Politică", ro("Statele Unite Casa Albă"), False, False),
    ("moldova", "Republica Moldova", "Actualitate & Politică", ro("Republica Moldova Chișinău"), False, False),
    ("diaspora", "Diaspora", "Actualitate & Politică", ro("românii din diaspora"), False, False),
    ("razboi_ucraina", "Războiul din Ucraina", "Actualitate & Politică", ro("război Ucraina Rusia"), False, False),
    ("orient", "Orientul Mijlociu", "Actualitate & Politică", ro("Orientul Mijlociu Israel Iran"), False, False),
    ("armata", "Armată & Apărare", "Actualitate & Politică", ro("armată apărare NATO"), False, False),
    ("justitie", "Justiție", "Actualitate & Politică", ro("justiție instanță procurori"), False, False),
    ("fapt_divers", "Fapt divers", "Actualitate & Politică", ro("fapt divers"), False, False),
    ("bucuresti", "București", "Actualitate & Politică", ro("București primărie"), False, False),
    ("vremea", "Vremea", "Actualitate & Politică", ro("vremea prognoza meteo"), False, False),

    # --- Economie & Bani ---
    ("economie", "Economie / Business", "Economie & Bani", ro("economie business"), False, True),
    ("finante", "Bursă & Investiții", "Economie & Bani", ro("bursă acțiuni investiții"), False, False),
    ("crypto", "Criptomonede", "Economie & Bani", ro("bitcoin criptomonede"), False, False),
    ("imobiliare", "Imobiliare", "Economie & Bani", ro("imobiliare piața apartamente"), False, False),
    ("auto", "Auto", "Economie & Bani", ro("auto mașini piața auto"), False, False),
    ("energie", "Energie", "Economie & Bani", ro("energie prețuri gaze electricitate"), False, False),
    ("agricultura", "Agricultură", "Economie & Bani", ro("agricultură fermieri"), False, False),
    ("startup", "Startup & Antreprenoriat", "Economie & Bani", ro("startup antreprenoriat"), False, False),
    ("munca", "Piața muncii", "Economie & Bani", ro("piața muncii locuri de muncă salarii"), False, False),
    ("transport", "Transport & Infrastructură", "Economie & Bani", ro("transport infrastructură autostrăzi"), False, False),

    # --- Sport ---
    ("sport", "Sport", "Sport", ro("sport"), False, True),
    ("fotbal", "Fotbal", "Sport", ro("fotbal"), False, False),
    ("tenis", "Tenis", "Sport", ro("tenis"), False, False),
    ("baschet", "Baschet", "Sport", ro("baschet NBA"), False, False),
    ("formula1", "Formula 1", "Sport", ro("Formula 1"), False, False),
    ("handbal_volei", "Handbal & Volei", "Sport", ro("handbal volei"), False, False),
    ("mma_box", "MMA & Box", "Sport", ro("MMA box UFC"), False, False),

    # --- Tehnologie ---
    ("tech", "Tehnologie", "Tehnologie", en("technology"), True, True),
    ("ai", "Inteligență artificială", "Tehnologie", ro("inteligență artificială"), False, False),
    ("gaming", "Gaming", "Tehnologie", ro("jocuri video gaming"), False, False),
    ("gadgeturi", "Gadgeturi & Telefoane", "Tehnologie", ro("smartphone gadgeturi telefoane"), False, False),
    ("securitate", "Securitate cibernetică", "Tehnologie", ro("securitate cibernetică atac hackeri"), False, False),
    ("social_media", "Social media", "Tehnologie", ro("social media TikTok Facebook Instagram"), False, False),

    # --- Divertisment & Cultură ---
    ("filme", "Filme & Cinema", "Divertisment & Cultură", ro("filme cinema premiere"), False, False),
    ("seriale", "Seriale & TV", "Divertisment & Cultură", ro("seriale TV Netflix"), False, False),
    ("muzica", "Muzică", "Divertisment & Cultură", ro("muzică concert festival"), False, False),
    ("celebritati", "Vedete", "Divertisment & Cultură", ro("vedete celebrități"), False, False),
    ("cultura", "Cultură & Cărți", "Divertisment & Cultură", ro("cultură teatru carte expoziție"), False, False),

    # --- Stil de viață ---
    ("sanatate", "Sănătate", "Stil de viață", ro("sănătate medicină"), False, False),
    ("fitness", "Fitness & Nutriție", "Stil de viață", ro("fitness nutriție alimentație"), False, False),
    ("calatorii", "Călătorii & Turism", "Stil de viață", ro("turism călătorii vacanță"), False, False),
    ("mancare", "Mâncare & Restaurante", "Stil de viață", ro("rețete gastronomie restaurante"), False, False),
    ("moda", "Modă", "Stil de viață", ro("modă fashion"), False, False),
    ("familie", "Familie & Copii", "Stil de viață", ro("parenting copii familie"), False, False),
    ("animale", "Animale", "Stil de viață", ro("animale de companie"), False, False),
    ("horoscop", "Horoscop", "Stil de viață", ro("horoscop"), False, False),

    # --- Știință & Societate ---
    ("stiinta", "Știință", "Știință & Societate", ro("știință descoperire cercetare"), False, False),
    ("spatiu", "Spațiu", "Știință & Societate", ro("spațiu NASA astronomie"), False, False),
    ("mediu", "Mediu & Climă", "Știință & Societate", ro("mediu schimbări climatice"), False, False),
    ("istorie", "Istorie & Arheologie", "Știință & Societate", ro("istorie arheologie"), False, False),
    ("educatie", "Educație", "Știință & Societate", ro("educație școală universitate"), False, False),
    ("religie", "Religie", "Știință & Societate", ro("religie biserică"), False, False),
]

MAX_PER_CATEGORY = 12
TRANSLATE_CHAR_LIMIT = 450
START_FILE = "start_date.txt"


def day_number():
    """Ziua N de cand ruleaza automatizarea (data de start e salvata la prima rulare)."""
    today = datetime.date.today()
    try:
        with open(START_FILE, "r", encoding="utf-8") as f:
            start = datetime.date.fromisoformat(f.read().strip())
    except (FileNotFoundError, ValueError):
        start = today
        with open(START_FILE, "w", encoding="utf-8") as f:
            f.write(start.isoformat())
    return (today - start).days + 1


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
        return text


def extra_summary(summary, raw_title, source):
    """Google News pune in descriere, de obicei, doar titlul + sursa.
    Pastram rezumatul doar daca aduce informatie in plus fata de titlu."""
    rest = summary.replace(raw_title, " ")
    if source:
        rest = rest.replace(source, " ")
    rest = rest.strip(" -–—|·\u00a0")
    return rest if len(rest) >= 40 else ""


def main():
    translator = GoogleTranslator(source="auto", target="ro")
    categories_meta = {}
    groups = []
    all_items = {}

    for key, label, group, url, do_translate, default in CATEGORIES:
        categories_meta[key] = {"label": label, "group": group, "default": default}
        if group not in groups:
            groups.append(group)

        items = []
        try:
            feed = feedparser.parse(url)
            entries = feed.entries
        except Exception as e:
            print(f"[{key}] eroare la feed: {e}")
            entries = []

        seen = set()
        for entry in entries:
            if len(items) >= MAX_PER_CATEGORY:
                break
            raw_title = entry.get("title", "").strip()
            link = entry.get("link", "")
            source = ""
            src = entry.get("source")
            if src is not None:
                source = getattr(src, "title", "") or (src.get("title", "") if isinstance(src, dict) else "")

            title = raw_title
            if source and title.endswith(" - " + source):
                title = title[: -(len(source) + 3)].strip()

            norm = title.lower()
            if not title or norm in seen:
                continue
            seen.add(norm)

            summary = extra_summary(clean_html(entry.get("summary", "")), raw_title, source)

            if do_translate:
                title_ro = safe_translate(title, translator)
                summary_ro = safe_translate(summary, translator) if summary else ""
            else:
                title_ro = title
                summary_ro = summary

            items.append(
                {
                    "title": title,
                    "title_ro": title_ro,
                    "summary_ro": summary_ro,
                    "link": link,
                    "source": source,
                    "published": entry.get("published", ""),
                }
            )

        all_items[key] = items
        print(f"[{key}] {len(items)} stiri")
        time.sleep(0.4)

    output = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "day_number": day_number(),
        "groups": groups,
        "categories": categories_meta,
        "items": all_items,
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=1)

    total = sum(len(v) for v in all_items.values())
    print(f"Scrise {total} stiri in {len(CATEGORIES)} categorii")


if __name__ == "__main__":
    main()
