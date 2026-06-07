"""日文學習處理管線。"""
from __future__ import annotations

import logging
from typing import Any

from toeic800 import config
from toeic800.db.database import ToeicDatabase
from toeic800.processing.japanese_grammar import extract_grammar
from toeic800.processing.japanese_quiz import build_quiz
from toeic800.processing.japanese_translator import translate_ja_batch, translate_ja_to_zh
from toeic800.processing.japanese_vocabulary import (
    ensure_ja_pronunciation,
    extract_japanese_vocabulary,
)
from toeic800.sources.japanese_feeds import discover_japanese_article
from toeic800.sources.japanese_scraper import fetch_japanese_article

logger = logging.getLogger(__name__)


def process_japanese_url(
    url: str,
    *,
    jlpt_level: str = "N5",
    source: str = "Manual",
    title: str | None = None,
    parser: str = "generic",
    db: ToeicDatabase | None = None,
) -> int:
    db = db or ToeicDatabase()
    logger.info("處理日文 [%s]: %s", jlpt_level, url)

    raw = fetch_japanese_article(url, parser=parser)
    paras_ja = raw.get("paragraphs_raw") or []
    if not paras_ja:
        raise ValueError(f"無法擷取日文正文: {url}")

    paras_zh = translate_ja_batch(paras_ja)
    paragraphs = [{"en": ja, "zh": zh} for ja, zh in zip(paras_ja, paras_zh)]

    title_ja = title or raw.get("title") or paras_ja[0][:80]
    title_zh = translate_ja_to_zh(title_ja)
    summary_ja = raw.get("summary_en") or paras_ja[0][:200]
    summary_zh = translate_ja_to_zh(summary_ja)

    vocabulary = extract_japanese_vocabulary(paras_ja, jlpt_level)
    for v in vocabulary:
        if not v.get("audio_path"):
            v["audio_path"] = ensure_ja_pronunciation(v["word"])

    grammar = extract_grammar(paras_ja, jlpt_level)
    quiz_raw = build_quiz(vocabulary, grammar)
    quiz = [
        {
            **q,
            "options_json": q["options_json"],
        }
        for q in quiz_raw
    ]

    subtitles = []
    for i, (ja, zh) in enumerate(zip(paras_ja[:10], paras_zh[:10])):
        subtitles.append(
            {"en": ja, "zh": zh, "start_sec": float(i * 6), "end_sec": float((i + 1) * 6)}
        )

    audio_url = raw.get("audio_url")
    bundle = {
        "track": "japanese",
        "jlpt_level": jlpt_level,
        "source": source,
        "url": url,
        "title": title_ja,
        "title_zh": title_zh,
        "summary_en": summary_ja,
        "summary_zh": summary_zh,
        "week_label": db.week_label(),
        "published_at": raw.get("published_at"),
        "has_video": bool(raw.get("has_video")),
        "video_url": raw.get("video_url"),
        "video_embed_html": raw.get("video_embed_html"),
        "thumbnail_url": raw.get("thumbnail_url"),
        "audio_url": audio_url,
        "paragraphs": paragraphs,
        "vocabulary": vocabulary,
        "subtitles": subtitles,
        "grammar": grammar,
        "quiz": quiz,
    }
    article_id = db.save_article_bundle(bundle)
    logger.info(
        "已儲存日文 article_id=%s level=%s vocab=%d grammar=%d",
        article_id,
        jlpt_level,
        len(vocabulary),
        len(grammar),
    )
    return article_id


def run_japanese_weekly_fetch(db: ToeicDatabase | None = None) -> dict[str, int]:
    """每週 N5–N1 各抓取一篇。"""
    db = db or ToeicDatabase()
    week = db.week_label()
    saved: dict[str, int] = {}

    for level in config.JLPT_LEVELS:
        if db.has_weekly_article("japanese", week, level):
            logger.info("本週已有 %s 文章，跳過", level)
            continue
        candidate = discover_japanese_article(level)
        if not candidate:
            logger.warning("找不到 %s 候選文章", level)
            continue
        if db.article_exists(candidate["url"]):
            logger.info("URL 已存在: %s", candidate["url"])
            continue
        try:
            aid = process_japanese_url(
                candidate["url"],
                jlpt_level=level,
                source=candidate["source"],
                title=candidate.get("title"),
                parser=candidate.get("parser", "generic"),
                db=db,
            )
            saved[level] = aid
        except Exception as exc:
            logger.error("日文 %s 處理失敗: %s", level, exc)

    logger.info("本週日文新增: %s", saved)
    return saved
