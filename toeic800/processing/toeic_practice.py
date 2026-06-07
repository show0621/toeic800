"""多益 800+ 每日擬真練習出題。"""
from __future__ import annotations

import hashlib
import json
import random
from datetime import date
from typing import Any

from toeic800.data.toeic800_bank import (
    GRAMMAR_BANK,
    LISTENING_BANK,
    READING_BANK,
    VOCAB_BANK,
)
from toeic800.db.database import ToeicDatabase
from toeic800.processing.toeic_explanations import enrich_question

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
        item = enrich_question(dict(q), skill)
        item["skill"] = skill
        item["qid"] = f"{skill}_{i}"
        if "options_json" not in item and "options" in item:
            item["options_json"] = json.dumps(item["options"], ensure_ascii=False)
        out.append(item)
    return out


def build_daily_vocab(db: ToeicDatabase, count: int = DAILY_COUNT, day: date | None = None) -> list[dict[str, Any]]:
    rng = daily_rng("vocab", day)
    pool = [dict(q) for q in VOCAB_BANK]
    rng.shuffle(pool)
    return _tag(pool[:count], "vocab")


def build_daily_grammar(db: ToeicDatabase, count: int = DAILY_COUNT, day: date | None = None) -> list[dict[str, Any]]:
    rng = daily_rng("grammar", day)
    pool = [dict(q) for q in GRAMMAR_BANK]
    rng.shuffle(pool)
    return _tag(pool[:count], "grammar")


def build_daily_listening(
    db: ToeicDatabase, count: int = DAILY_COUNT, day: date | None = None
) -> list[dict[str, Any]]:
    rng = daily_rng("listening", day)
    pool = [dict(q) for q in LISTENING_BANK]
    # 僅使用擬真 Part 3/4 對話題庫，不將新聞段落硬拆成男女對話
    rng.shuffle(pool)
    return _tag(pool[:count], "listening")


def build_daily_reading(
    db: ToeicDatabase, count: int = DAILY_COUNT, day: date | None = None
) -> list[dict[str, Any]]:
    rng = daily_rng("reading", day)
    by_fmt: dict[str, list[dict[str, Any]]] = {"single": [], "double": [], "triple": []}
    for q in READING_BANK:
        by_fmt[q["format"]].append(dict(q))

    picked: list[dict[str, Any]] = []
    for fmt, n in READING_SPLIT.items():
        pool = by_fmt.get(fmt, [])
        rng.shuffle(pool)
        picked.extend(pool[:n])

    rng.shuffle(picked)
    return _tag(picked[:count], "reading")


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
