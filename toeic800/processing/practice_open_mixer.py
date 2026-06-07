"""以公開資源補充多益擬真題（不複製官方／商業題庫）。"""
from __future__ import annotations

import random
import re
from typing import Any

from toeic800 import config
from toeic800.data.open_sources_registry import source_attribution_line
from toeic800.db.database import ToeicDatabase
from toeic800.processing.tatoeba_client import fetch_business_sentences, search_sentences
from toeic800.processing.vocab_selection import filter_active_vocabulary
from toeic800.processing.wiktionary_client import lookup_phrase
from toeic800.processing.word_levels import is_toeic800_word

_DISTRACTOR_SUFFIXES = ("ing", "ed", "ly", "tion", "ment", "ness", "able")


def mix_open_into(
    base: list[dict[str, Any]],
    open_items: list[dict[str, Any]],
    rng: random.Random,
    *,
    ratio: float | None = None,
) -> list[dict[str, Any]]:
    """將公開資源題混入每日題組（替換部分原創題）。"""
    if not open_items or not base:
        return base
    ratio = ratio if ratio is not None else config.OPEN_RESOURCE_MIX_RATIO
    n = min(len(open_items), max(1, int(len(base) * ratio)))
    merged = list(base)
    picks = open_items[:]
    rng.shuffle(picks)
    replace_idx = rng.sample(range(len(merged)), min(n, len(merged)))
    for i, idx in enumerate(replace_idx):
        if i < len(picks):
            merged[idx] = picks[i]
    return merged


def build_open_vocab_questions(
    db: ToeicDatabase, count: int, rng: random.Random
) -> list[dict[str, Any]]:
    """從 DB 已納入單字 + Cambridge 例句改編 Part 5。"""
    rows = filter_active_vocabulary(
        db.list_all_vocabulary(track="toeic"), toeic=True
    )
    rng.shuffle(rows)
    out: list[dict[str, Any]] = []
    for v in rows:
        if len(out) >= count:
            break
        word = v.get("word") or ""
        if not word or not is_toeic800_word(word):
            continue
        ex = (v.get("example_en") or "").strip()
        if len(ex) < 20:
            continue
        q = _cloze_from_sentence(ex, word, rng)
        if not q:
            continue
        q["topic"] = "finance_banking"
        q["explanation_zh"] = (
            f"例句改編自本 App 單字庫（Cambridge 等來源）。"
            f" 釋義：{v.get('meaning_zh') or v.get('meaning_en') or ''}"
        )[:200]
        _tag(q, "cambridge", url=v.get("dict_url") or "")
        out.append(q)
    return out


def build_open_phrase_questions(count: int, rng: random.Random) -> list[dict[str, Any]]:
    """Tatoeba / Wiktionary 片語克漏字。"""
    sentences = fetch_business_sentences(per_query=1)
    rng.shuffle(sentences)
    out: list[dict[str, Any]] = []
    for s in sentences:
        if len(out) >= count:
            break
        q = _phrase_cloze_from_tatoeba(s, rng)
        if q:
            out.append(q)
    # 不足時用 Wiktionary 片語模板
    for phrase in ("subject to", "in accordance with", "due diligence", "cash flow"):
        if len(out) >= count:
            break
        wiki = lookup_phrase(phrase)
        if not wiki:
            continue
        q = {
            "question": f"The acquisition is ___ regulatory approval before closing.",
            "options": ["subject to", "subjective to", "subjecting", "subjected"],
            "answer": "subject to",
            "grammar_type": "collocation",
            "topic": "contracts_legal",
            "explanation_zh": f"固定片語 subject to（須經…）。{wiki.get('meaning_en', '')[:80]}",
        }
        _tag(q, "wiktionary", url=wiki.get("dict_url", ""))
        out.append(q)
    return out[:count]


def build_open_reading_questions(
    db: ToeicDatabase, count: int, rng: random.Random
) -> list[dict[str, Any]]:
    """從 DB 新聞短摘錄出 Part 7 理解題（非全文）。"""
    articles = db.list_articles(track="toeic")
    if not articles:
        return []
    rng.shuffle(articles)
    out: list[dict[str, Any]] = []
    for art in articles:
        if len(out) >= count:
            break
        full = db.get_article(art["id"])
        if not full:
            continue
        paras = full.get("paragraphs") or []
        if len(paras) < 2:
            continue
        excerpt = "\n\n".join(p["text_en"] for p in paras[:2])
        if len(excerpt) > 650:
            excerpt = excerpt[:650].rsplit(" ", 1)[0] + "…"
        title = full.get("title") or "News report"
        summary = full.get("summary_en") or paras[0]["text_en"][:120]
        distractors = _reading_distractors(title, rng)
        options = [summary[:80]] + distractors[:3]
        rng.shuffle(options)
        answer = summary[:80]
        if answer not in options:
            options[0] = answer
        out.append(
            _tag(
                {
                    "format": "single",
                    "topic": "finance_banking",
                    "passages": [{"label": "Passage", "text": excerpt}],
                    "question": "What is the main idea of the passage?",
                    "options": options,
                    "answer": answer,
                    "explanation_zh": "依摘錄段落主旨判斷；完整報導請見原文連結。",
                    "article_url": full.get("url"),
                },
                "article_db",
                url=full.get("url") or "",
            )
        )
    return out


def build_open_listening_questions(count: int, rng: random.Random) -> list[dict[str, Any]]:
    """Tatoeba 例句改編為短對話（Neural TTS，非原聲）。"""
    pool = fetch_business_sentences(per_query=2)
    rng.shuffle(pool)
    out: list[dict[str, Any]] = []
    for i in range(0, len(pool) - 1, 2):
        if len(out) >= count:
            break
        a, b = pool[i], pool[i + 1]
        dialogue = f"W: {a['text']}\nM: {b['text']}"
        q_text = _listening_question_from_lines(a["text"], b["text"], rng)
        if not q_text:
            continue
        out.append(
            _tag(
                {
                    "topic": "office_admin",
                    "audio_text": dialogue,
                    "question": q_text["question"],
                    "options": q_text["options"],
                    "answer": q_text["answer"],
                    "explanation_zh": "對話改編自 Tatoeba 例句（CC BY），語音為合成。",
                },
                "tatoeba",
                url="https://tatoeba.org/",
            )
        )
    return out


def open_pool_stats(db: ToeicDatabase | None = None) -> dict[str, int]:
    """估算公開資源池規模（不觸發大量網路請求）。"""
    db = db or ToeicDatabase()
    vocab_n = len(
        filter_active_vocabulary(db.list_all_vocabulary(track="toeic"), toeic=True)
    )
    article_n = len(db.list_articles(track="toeic"))
    return {
        "open_vocab": min(vocab_n, 80),
        "open_phrase": 30,
        "open_reading": min(article_n * 2, 40),
        "open_listening": 20,
    }


def _tag(q: dict[str, Any], source_id: str, *, url: str = "") -> dict[str, Any]:
    q = dict(q)
    q["content_source"] = source_id
    q["source_url"] = url
    q["source_note"] = source_attribution_line(source_id, url=url)
    q.setdefault("source", f"open_{source_id}")
    return q


def _cloze_from_sentence(sentence: str, word: str, rng: random.Random) -> dict[str, Any] | None:
    pattern = re.compile(rf"\b({re.escape(word)})\b", re.I)
    match = pattern.search(sentence)
    if not match:
        return None
    token = match.group(1)
    blanked = pattern.sub("___", sentence, count=1)
    distractors = _fake_distractors(token, rng)
    options = [token] + [d for d in distractors if d.lower() != token.lower()][:3]
    rng.shuffle(options)
    return {
        "question": blanked,
        "options": options,
        "answer": token,
    }


def _phrase_cloze_from_tatoeba(item: dict[str, Any], rng: random.Random) -> dict[str, Any] | None:
    text = item["text"]
    words = re.findall(r"[A-Za-z]{5,}", text)
    if not words:
        return None
    target = rng.choice(words[1:] if len(words) > 1 else words)
    q = _cloze_from_sentence(text, target, rng)
    if not q:
        return None
    q["grammar_type"] = "collocation"
    q["topic"] = "office_admin"
    q["explanation_zh"] = f"Tatoeba 例句改編（CC BY 2.0 FR）。"
    return _tag(q, "tatoeba", url="https://tatoeba.org/")


def _fake_distractors(word: str, rng: random.Random) -> list[str]:
    w = word.lower()
    out: list[str] = []
    for suf in _DISTRACTOR_SUFFIXES:
        if w.endswith(suf) and len(w) > len(suf) + 3:
            out.append(w[: -len(suf)])
        else:
            out.append(w + suf)
    rng.shuffle(out)
    return out[:3]


def _reading_distractors(title: str, rng: random.Random) -> list[str]:
    templates = [
        "A local sports team won the championship.",
        "Weather forecasts predict heavy rain next week.",
        "A new restaurant opened in the downtown area.",
        "Travel restrictions were lifted at several airports.",
    ]
    rng.shuffle(templates)
    return templates


def _listening_question_from_lines(
    line_a: str, line_b: str, rng: random.Random
) -> dict[str, Any] | None:
    keywords = re.findall(r"[A-Za-z]{5,}", line_a + " " + line_b)
    if not keywords:
        return None
    focus = rng.choice(keywords).lower()
    return {
        "question": f"What topic is discussed in the conversation?",
        "options": [
            focus,
            "weather forecast",
            "sports results",
            "movie reviews",
        ],
        "answer": focus,
    }
