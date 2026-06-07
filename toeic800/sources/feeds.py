"""RSS 探索 BBC / CNN 經濟與國際新聞。"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import feedparser

from toeic800 import config

logger = logging.getLogger(__name__)


def _matches_topic(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in config.TOPIC_KEYWORDS)


def _source_name(feed_key: str, url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "bbc" in host:
        return "BBC"
    if "cnn" in host:
        return "CNN"
    return feed_key.upper()


def discover_articles(limit: int | None = None) -> list[dict[str, Any]]:
    """從 RSS 找出符合主題的文章連結。"""
    limit = limit or config.WEEKLY_ARTICLE_LIMIT
    found: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for feed_key, feed_url in config.RSS_FEEDS.items():
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as exc:
            logger.warning("RSS 失敗 %s: %s", feed_key, exc)
            continue

        for entry in parsed.entries:
            url = getattr(entry, "link", "") or ""
            if not url or url in seen_urls:
                continue
            title = getattr(entry, "title", "") or ""
            summary = getattr(entry, "summary", "") or ""
            blob = f"{title} {summary}"
            if not _matches_topic(blob):
                continue

            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6]).isoformat()

            seen_urls.add(url)
            found.append(
                {
                    "source": _source_name(feed_key, url),
                    "url": url,
                    "title": re.sub(r"\s+", " ", title).strip(),
                    "summary_en": _strip_html(summary)[:500],
                    "published_at": published,
                }
            )
            if len(found) >= limit:
                return found

    return found


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").strip()
