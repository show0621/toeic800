"""多益 800+ 每日擬真練習出題。"""
from __future__ import annotations

import hashlib
import json
import random
import re
from datetime import date
from typing import Any

from toeic800.data.toeic800_bank import (
    GRAMMAR_BANK,
    LISTENING_BANK,
    READING_BANK,
    VOCAB_BANK,
)
from toeic800.db.database import ToeicDatabase
from toeic800.processing.word_levels import filter_advanced_vocabulary, is_advanced_word

DAILY_COUNT = 20
READING_SPLIT = {"single": 8, "double": 7, "triple": 5}


def daily_rng(skill: str, day: date | None = None) -> random.Random:
    day = day or date.today()
    seed = int(
        hashlib.md5(f"{day.isoformat()}:{skill}:toeic800v1".encode()).hexdigest()[:8],
        16,
    )
    return random.Random(seed)


def _tag(items: list[dict[str, Any]], skill: str) -> list[dict[str, Any]]:
    out = []
    for i, q in enumerate(items):
        item = dict(q)
        item["skill"] = skill
        item["qid"] = f"{skill}_{i}"
        if "options_json" not in item and "options" in item:
            item["options_json"] = json.dumps(item["options"], ensure_ascii=False)
        out.append(item)
    return out


def _vocab_from_db(db: ToeicDatabase, rng: random.Random) -> list[dict[str, Any]]:
    vocab = filter_advanced_vocabulary(db.list_all_vocabulary(track="toeic"))
    if len(vocab) < 4:
        return []
    generated: list[dict[str, Any]] = []
    templates = [
        "Analysts noted that _____ market conditions have affected portfolio allocations.",
        "The report highlights _____ risks in emerging economies.",
        "Investors remain _____ amid uncertainty surrounding monetary policy.",
        "Management cited _____ demand as a key driver of revenue growth.",
    ]
    for v in vocab:
        word = v.get("word", "")
        if not word or not is_advanced_word(word):
            continue
        question = rng.choice(templates)
        answer = word
        others = [x["word"] for x in vocab if x["word"] != word and is_advanced_word(x["word"])]
        if len(others) < 3:
            continue
        distractors = rng.sample(others, 3)
        options = [answer] + distractors
        rng.shuffle(options)
        generated.append(
            {
                "question": question,
                "options": options,
                "answer": answer,
                "explanation_zh": v.get("meaning_zh") or "來自本週經濟新聞單字。",
            }
        )
        if len(generated) >= 12:
            break
    return generated


def _grammar_from_articles(db: ToeicDatabase, rng: random.Random) -> list[dict[str, Any]]:
    articles = db.list_articles(track="toeic")
    generated: list[dict[str, Any]] = []
    preps = ["in", "on", "at", "by", "for", "to", "with", "from", "of", "about"]
    for art in articles[:6]:
        full = db.get_article(art["id"])
        if not full:
            continue
        for para in full.get("paragraphs") or []:
            text = para.get("text_en") or ""
            sents = re.split(r"(?<=[.!?])\s+", text)
            for sent in sents:
                if len(sent) < 60 or len(sent) > 220:
                    continue
                for prep in preps:
                    pat = rf"\b{prep}\b"
                    if not re.search(pat, sent, re.I):
                        continue
                    blanked = re.sub(pat, "_____", sent, count=1, flags=re.I)
                    if blanked == sent:
                        continue
                    distractors = rng.sample([p for p in preps if p != prep.lower()], 3)
                    options = [prep.lower()] + distractors
                    rng.shuffle(options)
                    generated.append(
                        {
                            "question": blanked,
                            "options": options,
                            "answer": prep.lower(),
                            "explanation_zh": "依文章上下文選擇正確介系詞。",
                        }
                    )
                    break
                if len(generated) >= 15:
                    return generated
    return generated


def build_daily_vocab(db: ToeicDatabase, count: int = DAILY_COUNT, day: date | None = None) -> list[dict[str, Any]]:
    rng = daily_rng("vocab", day)
    pool = [dict(q) for q in VOCAB_BANK]
    pool.extend(_vocab_from_db(db, rng))
    rng.shuffle(pool)
    seen: set[str] = set()
    picked: list[dict[str, Any]] = []
    for q in pool:
        key = q.get("question", "")
        if key in seen:
            continue
        seen.add(key)
        picked.append(q)
        if len(picked) >= count:
            break
    return _tag(picked, "vocab")


def build_daily_grammar(db: ToeicDatabase, count: int = DAILY_COUNT, day: date | None = None) -> list[dict[str, Any]]:
    rng = daily_rng("grammar", day)
    pool = [dict(q) for q in GRAMMAR_BANK]
    pool.extend(_grammar_from_articles(db, rng))
    rng.shuffle(pool)
    return _tag(pool[:count], "grammar")


def _plain_text_to_dialogue(text: str) -> str:
    """將新聞段落拆成 W/M 對話，供雙語音聽力合成。"""
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    if len(sents) >= 2:
        mid = max(1, len(sents) // 2)
        w_part = " ".join(sents[:mid])
        m_part = " ".join(sents[mid : mid + 2])
        return f"W: {w_part} M: {m_part}"
    return text


def build_daily_listening(
    db: ToeicDatabase, count: int = DAILY_COUNT, day: date | None = None
) -> list[dict[str, Any]]:
    rng = daily_rng("listening", day)
    pool = [dict(q) for q in LISTENING_BANK]
    # 補充：從文章句子的 TTS 聽力理解
    articles = db.list_articles(track="toeic")
    for art in rng.sample(articles, min(5, len(articles))):
        full = db.get_article(art["id"])
        if not full:
            continue
        for para in (full.get("paragraphs") or [])[:2]:
            text = (para.get("text_en") or "")[:280]
            if len(text) < 80:
                continue
            zh = para.get("text_zh") or "經濟相關報導內容"
            pool.append(
                {
                    "audio_text": _plain_text_to_dialogue(text),
                    "question": "What topic is primarily discussed in the passage?",
                    "options": [
                        "Economic or financial developments",
                        "Sports and entertainment news",
                        "Local weather forecasts",
                        "Restaurant dining recommendations",
                    ],
                    "answer": "Economic or financial developments",
                    "explanation_zh": f"摘要：{zh[:60]}…",
                }
            )
    rng.shuffle(pool)
    return _tag(pool[:count], "listening")


def build_daily_reading(
    db: ToeicDatabase, count: int = DAILY_COUNT, day: date | None = None
) -> list[dict[str, Any]]:
    rng = daily_rng("reading", day)
    by_fmt: dict[str, list[dict[str, Any]]] = {"single": [], "double": [], "triple": []}
    for q in READING_BANK:
        by_fmt[q["format"]].append(dict(q))

    # 從 DB 組合單篇閱讀
    articles = db.list_articles(track="toeic")
    for art in articles[:8]:
        full = db.get_article(art["id"])
        if not full or not full.get("paragraphs"):
            continue
        text = " ".join(p["text_en"] for p in full["paragraphs"][:3])[:600]
        if len(text) < 120:
            continue
        by_fmt["single"].append(
            {
                "format": "single",
                "passages": [{"label": full["title"][:40], "text": text}],
                "question": "What is the passage mainly about?",
                "options": [
                    "Economic or business news developments",
                    "A personal travel memoir",
                    "Scientific research on biology",
                    "A fictional short story",
                ],
                "answer": "Economic or business news developments",
                "explanation_zh": "本週 BBC/CNN 經濟英文報導。",
            }
        )

    picked: list[dict[str, Any]] = []
    for fmt, n in READING_SPLIT.items():
        pool = by_fmt.get(fmt, [])
        rng.shuffle(pool)
        picked.extend(pool[:n])

    rng.shuffle(picked)
    items = picked[:count]
    for i, q in enumerate(items):
        q["skill"] = "reading"
        q["qid"] = f"reading_{q.get('format', 'x')}_{i}"
        if "options_json" not in q:
            q["options_json"] = json.dumps(q["options"], ensure_ascii=False)
    return items


def build_daily_set(
    db: ToeicDatabase, skill: str, count: int = DAILY_COUNT, day: date | None = None
) -> list[dict[str, Any]]:
    builders = {
        "vocab": build_daily_vocab,
        "grammar": build_daily_grammar,
        "listening": build_daily_listening,
        "reading": build_daily_reading,
    }
    fn = builders.get(skill)
    if not fn:
        return []
    return fn(db, count, day)
