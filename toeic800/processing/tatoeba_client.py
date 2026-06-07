"""Tatoeba 例句（CC BY 2.0 FR）— 片語／聽力素材。"""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any

import requests

from toeic800 import config

logger = logging.getLogger(__name__)

_TATOEBA_API = "https://tatoeba.org/en/api_v0/search"
_CACHE_DIR = config.DATA_DIR / "cache" / "tatoeba"
_HEADERS = {"User-Agent": "Toeic800Study/1.0 (personal education)"}

_BUSINESS_QUERIES = (
    "meeting",
    "deadline",
    "contract",
    "budget",
    "revenue",
    "customer",
    "shipment",
    "invoice",
    "postpone",
    "approve",
    "negotiate",
    "quarterly",
    "supervisor",
    "conference",
    "application",
)

_last_fetch = 0.0


def search_sentences(
    query: str,
    *,
    limit: int = 5,
    min_len: int = 25,
) -> list[dict[str, Any]]:
    if not config.TATOEBA_ENABLED:
        return []
    cached = _read_cache(query, limit)
    if cached is not None:
        return [s for s in cached if len(s.get("text", "")) >= min_len][:limit]

    _throttle()
    try:
        resp = requests.get(
            _TATOEBA_API,
            params={
                "from": "eng",
                "query": query,
                "sort": "relevance",
                "limit": max(limit * 3, 10),
            },
            headers=_HEADERS,
            timeout=config.TATOEBA_REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return []
        rows = resp.json().get("results") or []
    except Exception as exc:
        logger.debug("Tatoeba 查詢失敗 %s: %s", query, exc)
        return []

    out: list[dict[str, Any]] = []
    for row in rows:
        text = (row.get("text") or "").strip()
        if len(text) < min_len or not _looks_english(text):
            continue
        out.append(
            {
                "text": text,
                "license": row.get("license") or "CC BY 2.0 FR",
                "author": row.get("username") or "",
                "tatoeba_id": row.get("id"),
                "query": query,
            }
        )
        if len(out) >= limit:
            break
    _write_cache(query, out)
    return out


def fetch_business_sentences(*, per_query: int = 2) -> list[dict[str, Any]]:
    """輪詢商業相關關鍵字，彙整例句池。"""
    pool: list[dict[str, Any]] = []
    seen: set[str] = set()
    for q in _BUSINESS_QUERIES:
        for item in search_sentences(q, limit=per_query, min_len=20):
            key = item["text"].lower()
            if key in seen:
                continue
            seen.add(key)
            pool.append(item)
    return pool


def _looks_english(text: str) -> bool:
    letters = sum(1 for c in text if c.isalpha())
    return letters >= 10 and letters / max(len(text), 1) > 0.6


def _throttle() -> None:
    global _last_fetch
    gap = config.TATOEBA_REQUEST_GAP_SEC
    now = time.monotonic()
    wait = gap - (now - _last_fetch)
    if wait > 0:
        time.sleep(wait)
    _last_fetch = time.monotonic()


def _cache_path(query: str) -> Path:
    safe = re.sub(r"[^\w\-]+", "_", query.lower())[:40]
    return _CACHE_DIR / f"{safe}.json"


def _read_cache(query: str, limit: int) -> list[dict[str, Any]] | None:
    path = _cache_path(query)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - data.get("fetched_at", 0) > config.TATOEBA_CACHE_HOURS * 3600:
            return None
        return list(data.get("items") or [])[:limit]
    except Exception:
        return None


def _write_cache(query: str, items: list[dict[str, Any]]) -> None:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(query)
    path.write_text(
        json.dumps({"fetched_at": time.time(), "items": items}, ensure_ascii=False),
        encoding="utf-8",
    )
