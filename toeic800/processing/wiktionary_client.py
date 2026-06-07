"""Wiktionary 片語／搭配（CC BY-SA）— 簡短摘錄。"""
from __future__ import annotations

import logging
import re
import time
from typing import Any
from urllib.parse import quote

import requests

from toeic800 import config

logger = logging.getLogger(__name__)

_WIKI_API = "https://en.wiktionary.org/w/api.php"
_HEADERS = {"User-Agent": "Toeic800Study/1.0 (personal education; CC-BY-SA)"}
_last_fetch = 0.0


def lookup_phrase(phrase: str) -> dict[str, Any] | None:
    """取一則英文定義摘錄（非整頁複製）。"""
    if not config.WIKTIONARY_ENABLED:
        return None
    term = phrase.strip().lower()
    if not term or len(term) > 40:
        return None
    _throttle()
    try:
        resp = requests.get(
            _WIKI_API,
            params={
                "action": "query",
                "format": "json",
                "titles": term.replace(" ", "_"),
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "exchars": 280,
            },
            headers=_HEADERS,
            timeout=12,
        )
        if resp.status_code != 200:
            return None
        pages = resp.json().get("query", {}).get("pages", {})
        for page in pages.values():
            if page.get("missing"):
                continue
            extract = (page.get("extract") or "").strip()
            if not extract or len(extract) < 20:
                continue
            first = extract.split("\n")[0][:240]
            return {
                "phrase": phrase,
                "meaning_en": first,
                "dict_source": "wiktionary",
                "dict_url": f"https://en.wiktionary.org/wiki/{quote(term.replace(' ', '_'))}",
            }
    except Exception as exc:
        logger.debug("Wiktionary 查詢失敗 %s: %s", phrase, exc)
    return None


def _throttle() -> None:
    global _last_fetch
    gap = config.WIKTIONARY_REQUEST_GAP_SEC
    now = time.monotonic()
    wait = gap - (now - _last_fetch)
    if wait > 0:
        time.sleep(wait)
    _last_fetch = time.monotonic()
