"""每週抓取與單篇處理管線。"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from toeic800 import config
from toeic800.db.database import ToeicDatabase
from toeic800.processing.translator import translate_batch, translate_text
from toeic800.processing.vocabulary import ensure_pronunciation, extract_vocabulary
from toeic800.sources.feeds import discover_articles
from toeic800.sources.scraper import fetch_article_content

logger = logging.getLogger(__name__)


def process_url(
    url: str,
    *,
    source: str = "Manual",
    title: str | None = None,
    db: ToeicDatabase | None = None,
) -> int:
    db = db or ToeicDatabase()
    logger.info("處理文章: %s", url)

    raw = fetch_article_content(url)
    paras_en = raw.get("paragraphs_raw") or []
    if not paras_en:
        raise ValueError(f"無法擷取正文: {url}")

    paras_zh = translate_batch(paras_en)
    paragraphs = [{"en": en, "zh": zh} for en, zh in zip(paras_en, paras_zh)]

    title_en = title or raw.get("title") or paras_en[0][:120]
    title_zh = translate_text(title_en)
    summary_en = raw.get("summary_en") or paras_en[0][:300]
    summary_zh = translate_text(summary_en)

    vocabulary = extract_vocabulary(paras_en)
    for v in vocabulary:
        if not v.get("audio_path"):
            v["audio_path"] = ensure_pronunciation(v["word"])

    subs_raw = raw.get("subtitles_raw") or []
    subtitles: list[dict[str, Any]] = []
    if subs_raw:
        en_lines = [s["en"] for s in subs_raw]
        zh_lines = translate_batch(en_lines)
        for s, zh in zip(subs_raw, zh_lines):
            subtitles.append(
                {
                    "en": s["en"],
                    "zh": zh,
                    "start_sec": s.get("start_sec"),
                    "end_sec": s.get("end_sec"),
                }
            )
    elif raw.get("has_video") and len(paras_en) >= 2:
        # 無原生字幕時，用前幾段正文當「分段字幕」輔助聽讀
        for i, (en, zh) in enumerate(zip(paras_en[:8], paras_zh[:8])):
            subtitles.append(
                {"en": en, "zh": zh, "start_sec": float(i * 8), "end_sec": float((i + 1) * 8)}
            )

    bundle = {
        "track": "toeic",
        "source": source,
        "url": url,
        "title": title_en,
        "title_zh": title_zh,
        "summary_en": summary_en,
        "summary_zh": summary_zh,
        "week_label": db.week_label(),
        "published_at": raw.get("published_at"),
        "has_video": raw.get("has_video"),
        "video_url": raw.get("video_url"),
        "video_embed_html": raw.get("video_embed_html"),
        "thumbnail_url": raw.get("thumbnail_url"),
        "paragraphs": paragraphs,
        "vocabulary": vocabulary,
        "subtitles": subtitles,
    }
    article_id = db.save_article_bundle(bundle)
    logger.info("已儲存 article_id=%s 單字=%d", article_id, len(vocabulary))
    return article_id


def run_weekly_fetch(db: ToeicDatabase | None = None) -> list[int]:
    db = db or ToeicDatabase()
    candidates = discover_articles(limit=config.WEEKLY_ARTICLE_LIMIT)
    saved: list[int] = []

    for item in candidates:
        if db.article_exists(item["url"]):
            logger.info("已存在，跳過: %s", item["url"])
            continue
        try:
            aid = process_url(
                item["url"],
                source=item["source"],
                title=item.get("title"),
                db=db,
            )
            saved.append(aid)
        except Exception as exc:
            logger.error("處理失敗 %s: %s", item["url"], exc)

    logger.info("本週新增 %d 篇", len(saved))
    return saved
