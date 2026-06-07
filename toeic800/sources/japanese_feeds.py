"""JLPT N5–N1 日文新聞 RSS 探索。

來源分級參考：https://vocus.cc/article/6837b674fd8978000142bdb4
（NHK やさしいは news.web.nhk 需從 NHK RSS 導向；毎日小学生 RSS 已失效，N4 改 Yahoo 社會版）
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

import feedparser
import requests

from toeic800 import config

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}


def discover_japanese_article(level: str) -> dict[str, Any] | None:
    if level == "N5":
        item = _discover_nhk_easy_via_rss()
        if item:
            return item

    meta = config.JLPT_SOURCES.get(level)
    if not meta:
        return None
    return _from_rss(
        meta["rss"],
        source=meta["source"],
        jlpt_level=level,
        parser=meta.get("parser", "generic"),
        pick=meta.get("pick", 0),
    )


def _from_rss(
    rss_url: str,
    *,
    source: str,
    jlpt_level: str,
    parser: str,
    pick: int = 0,
) -> dict[str, Any] | None:
    try:
        parsed = feedparser.parse(rss_url, request_headers=HEADERS)
    except Exception as exc:
        logger.warning("RSS 失敗 %s: %s", jlpt_level, exc)
        return None

    entries = parsed.entries or []
    if not entries:
        return None

    idx = min(pick, len(entries) - 1)
    entry = entries[idx]
    url = getattr(entry, "link", "") or ""
    if not url:
        return None

    title = re.sub(r"\s+", " ", getattr(entry, "title", "") or "").strip()
    published = None
    if getattr(entry, "published_parsed", None):
        published = datetime(*entry.published_parsed[:6]).isoformat()

    return {
        "url": url,
        "title": title,
        "source": source,
        "jlpt_level": jlpt_level,
        "parser": parser,
        "published_at": published,
    }


def _discover_nhk_easy_via_rss() -> dict[str, Any] | None:
    """N5：從 NHK RSS 取最新，優先 news.web.nhk 連結（やさしいニュース同体系）。"""
    item = _from_rss(
        "https://www.nhk.or.jp/rss/news/cat0.xml",
        source=config.JLPT_SOURCES["N5"]["source"],
        jlpt_level="N5",
        parser="nhk_easy",
        pick=0,
    )
    if not item:
        return None

    url = item["url"]
    if "news.web.nhk" in url:
        easy = _find_easy_link(url)
        if easy:
            item["url"] = easy
            item["parser"] = "nhk_easy"
    return item


def _find_easy_link(article_url: str) -> str | None:
    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        m = re.search(r'(https?://news\.web\.nhk/news/easy/[^"\']+)', resp.text)
        if m:
            return m.group(1).rstrip("\\")
        m2 = re.search(r'href="(/news/easy/[^"]+)"', resp.text)
        if m2:
            return "https://news.web.nhk" + m2.group(1)
    except Exception as exc:
        logger.debug("easy link 失敗: %s", exc)
    return None
