"""TOEIC 800–900 RAG 擬真出題引擎（原創題目，不依新聞）。

版權聲明：
- 本模組題目為原創擬真練習，非 ETS／IIBC 官方試題，亦未複製商業機構題庫原文。
- 僅參考 IIBC 公開之測驗「格式」說明（Part 5–7 題型、時間、主題類別）。
- TOEIC 為 ETS 註冊商標；本專案與 ETS／IIBC 無關，不提供官方認證或成績。
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from datetime import date
from typing import Any

from toeic800 import config
from toeic800.data.toeic800_bank import (
    GRAMMAR_BANK,
    LISTENING_BANK,
    READING_BANK,
    VOCAB_BANK,
)
from toeic800.data.toeic800_bank_ext import (
    GRAMMAR_EXT,
    LISTENING_EXT,
    READING_EXT,
    VOCAB_EXT,
)
from toeic800.data.toeic_format_spec import PART5_GRAMMAR_TYPES, TOEIC_TOPICS_800
from toeic800.data.toeic_rag_patterns import expand_pattern_pool
from toeic800.processing.listening_validator import filter_listening_pool
from toeic800.processing.practice_open_mixer import (
    build_open_listening_questions,
    build_open_phrase_questions,
    build_open_reading_questions,
    build_open_vocab_questions,
    mix_open_into,
    open_pool_stats,
)
from toeic800.processing.toeic_explanations import enrich_question

DAILY_COUNT = 20
READING_SPLIT = {"single": 8, "double": 7, "triple": 5}

_CORPUS_VERSION = config.TOEIC_RAG_CORPUS_VERSION


def _daily_rng(skill: str, day: date | None = None) -> random.Random:
    day = day or date.today()
    seed = int(
        hashlib.md5(f"{day.isoformat()}:{skill}:{_CORPUS_VERSION}".encode()).hexdigest()[:8],
        16,
    )
    return random.Random(seed)


def _normalize(q: dict[str, Any], skill: str) -> dict[str, Any]:
    item = dict(q)
    item.setdefault("source", "toeic_rag_original")
    item.setdefault("score_band", "800-900")
    if "options_json" not in item and "options" in item:
        item["options_json"] = json.dumps(item["options"], ensure_ascii=False)
    return enrich_question(item, skill)


def _dedupe_pool(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    pool: list[dict[str, Any]] = []
    for q in items:
        key = (q.get("audio_text") or q.get("question", "")) + "|" + q.get("answer", "")
        if key in seen:
            continue
        seen.add(key)
        pool.append(q)
    return pool


def _full_corpus(skill: str) -> list[dict[str, Any]]:
    """RAG 檢索池：核心題庫 + 擴充題庫 + 模式展開題。"""
    if skill == "vocab":
        base = [dict(q) for q in VOCAB_BANK + VOCAB_EXT]
        expanded = expand_pattern_pool("vocab")
    elif skill == "grammar":
        base = [dict(q) for q in GRAMMAR_BANK + GRAMMAR_EXT]
        expanded = expand_pattern_pool("grammar")
    elif skill == "listening":
        base = [dict(q) for q in LISTENING_BANK + LISTENING_EXT]
        expanded = expand_pattern_pool("listening")
        raw = base + expanded
        return filter_listening_pool(_dedupe_pool(raw))
    elif skill == "reading":
        base = [dict(q) for q in READING_BANK + READING_EXT]
        expanded = expand_pattern_pool("reading")
    else:
        return []

    seen: set[str] = set()
    pool: list[dict[str, Any]] = []
    for q in _dedupe_pool(base + expanded):
        key = q.get("question", "") + "|" + q.get("answer", "")
        if key in seen:
            continue
        seen.add(key)
        pool.append(q)
    return pool


def _stratified_pick(
    pool: list[dict[str, Any]],
    count: int,
    rng: random.Random,
    *,
    topic_key: str = "topic",
) -> list[dict[str, Any]]:
    """按 TOEIC 主題分層抽題，避免單日主題過於集中。"""
    by_topic: dict[str, list[dict[str, Any]]] = {t: [] for t in TOEIC_TOPICS_800}
    by_topic["_other"] = []
    for q in pool:
        t = q.get(topic_key) or q.get("grammar_type") or "_other"
        if t in by_topic:
            by_topic[t].append(q)
        else:
            by_topic["_other"].append(q)

    picked: list[dict[str, Any]] = []
    topics = [t for t in TOEIC_TOPICS_800 if by_topic[t]]
    rng.shuffle(topics)
    ti = 0
    while len(picked) < count and topics:
        t = topics[ti % len(topics)]
        candidates = by_topic[t]
        if candidates:
            q = rng.choice(candidates)
            if q not in picked:
                picked.append(q)
                candidates.remove(q)
        if not candidates:
            topics = [x for x in topics if by_topic[x]]
        ti += 1
        if ti > count * 20:
            break

    remaining = [q for q in pool if q not in picked]
    rng.shuffle(remaining)
    while len(picked) < count and remaining:
        picked.append(remaining.pop())
    return picked[:count]


def _apply_open_mix(
    db: Any,
    skill: str,
    base: list[dict[str, Any]],
    rng: random.Random,
    count: int,
) -> list[dict[str, Any]]:
    if not config.OPEN_RESOURCES_ENABLED or db is None:
        return base
    open_builders = {
        "vocab": lambda: build_open_vocab_questions(db, count, rng),
        "grammar": lambda: build_open_phrase_questions(count, rng),
        "phrase": lambda: build_open_phrase_questions(count, rng),
        "listening": lambda: build_open_listening_questions(count, rng),
        "reading": lambda: build_open_reading_questions(db, count, rng),
    }
    fn = open_builders.get(skill)
    if not fn:
        return base
    try:
        open_qs = fn()
    except Exception:
        return base
    return mix_open_into(base, open_qs, rng)


def build_daily_vocab(db: Any, count: int = DAILY_COUNT, day: date | None = None) -> list[dict[str, Any]]:
    rng = _daily_rng("vocab", day)
    pool = _full_corpus("vocab")
    picked = _stratified_pick(pool, count, rng)
    rng.shuffle(picked)
    picked = _apply_open_mix(db, "vocab", picked, rng, count)
    return [_normalize(q, "vocab") for q in picked[:count]]


def build_daily_grammar(db: Any, count: int = DAILY_COUNT, day: date | None = None) -> list[dict[str, Any]]:
    rng = _daily_rng("grammar", day)
    pool = _full_corpus("grammar")
    # 文法題確保時態/介系詞等類型分散
    by_type: dict[str, list] = {g: [] for g in PART5_GRAMMAR_TYPES}
    by_type["_x"] = []
    for q in pool:
        gt = q.get("grammar_type", "_x")
        (by_type.get(gt) or by_type["_x"]).append(q)
    picked: list[dict] = []
    types = [t for t in PART5_GRAMMAR_TYPES if by_type[t]]
    rng.shuffle(types)
    for i in range(count):
        t = types[i % len(types)] if types else "_x"
        cands = by_type.get(t) or pool
        if not cands:
            break
        q = rng.choice(cands)
        if q not in picked:
            picked.append(q)
    rng.shuffle(picked)
    while len(picked) < count:
        q = rng.choice(pool)
        if q not in picked:
            picked.append(q)
    picked = _apply_open_mix(db, "grammar", picked, rng, count)
    return [_normalize(q, "grammar") for q in picked[:count]]


def build_daily_phrase(db: Any, count: int = DAILY_COUNT, day: date | None = None) -> list[dict[str, Any]]:
    """片語／搭配詞（Tatoeba + Wiktionary + 原創模板）。"""
    rng = _daily_rng("phrase", day)
    pool = [q for q in _full_corpus("grammar") if q.get("grammar_type") == "collocation"]
    pool += expand_pattern_pool("grammar")
    pool = _dedupe_pool(pool)
    picked = _stratified_pick(pool, count, rng) if pool else []
    while len(picked) < count and pool:
        q = rng.choice(pool)
        if q not in picked:
            picked.append(q)
    if len(picked) < count:
        picked.extend(build_open_phrase_questions(count, rng))
    picked = _apply_open_mix(db, "phrase", picked[:count], rng, count)
    rng.shuffle(picked)
    return [_normalize(q, "phrase") for q in picked[:count]]


def build_daily_listening(db: Any, count: int = DAILY_COUNT, day: date | None = None) -> list[dict[str, Any]]:
    rng = _daily_rng("listening", day)
    pool = _full_corpus("listening")
    picked = _stratified_pick(pool, count, rng)
    rng.shuffle(picked)
    picked = _apply_open_mix(db, "listening", picked, rng, count)
    return [_normalize(q, "listening") for q in picked[:count]]


def build_daily_reading(db: Any, count: int = DAILY_COUNT, day: date | None = None) -> list[dict[str, Any]]:
    rng = _daily_rng("reading", day)
    pool = _full_corpus("reading")
    by_fmt: dict[str, list] = {"single": [], "double": [], "triple": []}
    for q in pool:
        by_fmt[q.get("format", "single")].append(q)
    picked: list[dict] = []
    for fmt, n in READING_SPLIT.items():
        c = list(by_fmt.get(fmt, []))
        rng.shuffle(c)
        picked.extend(c[:n])
    rng.shuffle(picked)
    picked = _apply_open_mix(db, "reading", picked, rng, count)
    return [_normalize(q, "reading") for q in picked[:count]]


def build_daily_set(
    db: Any, skill: str, count: int = DAILY_COUNT, day: date | None = None
) -> list[dict[str, Any]]:
    builders = {
        "vocab": build_daily_vocab,
        "grammar": build_daily_grammar,
        "phrase": build_daily_phrase,
        "listening": build_daily_listening,
        "reading": build_daily_reading,
    }
    fn = builders.get(skill)
    if not fn:
        return []
    items = fn(db, count, day)
    for i, q in enumerate(items):
        q["skill"] = skill
        q["qid"] = f"{skill}_{i}"
    return items


def corpus_stats(db: Any = None) -> dict[str, int]:
    stats = {
        "vocab": len(_full_corpus("vocab")),
        "grammar": len(_full_corpus("grammar")),
        "phrase": len(_full_corpus("grammar")),
        "listening": len(_full_corpus("listening")),
        "reading": len(_full_corpus("reading")),
    }
    if config.OPEN_RESOURCES_ENABLED:
        open_s = open_pool_stats(db if db is not None else None)
        stats["open_vocab"] = open_s["open_vocab"]
        stats["open_phrase"] = open_s["open_phrase"]
        stats["open_reading"] = open_s["open_reading"]
        stats["open_listening"] = open_s["open_listening"]
    return stats
