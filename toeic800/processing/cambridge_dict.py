"""Cambridge Dictionary（繁中）查詢 — 引用釋義與例句，附來源連結。"""
from __future__ import annotations

import logging
import re
import time
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from toeic800 import config

logger = logging.getLogger(__name__)

CAMBRIDGE_ZHT_HOME = "https://dictionary.cambridge.org/zht/"
CAMBRIDGE_ZHT_PATH = "词典/英语-汉语-繁体"
CAMBRIDGE_COPYRIGHT = "© Cambridge University Press"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}

_BUSINESS_HINTS = (
    "business",
    "economic",
    "economy",
    "finance",
    "financial",
    "commerce",
    "trade",
    "market",
    "employment",
    "corporate",
    "commercial",
)

_last_request_at = 0.0


def cambridge_word_url(word: str) -> str:
    w = quote(word.strip().lower())
    return f"{CAMBRIDGE_ZHT_HOME}{CAMBRIDGE_ZHT_PATH}/{w}"


def cambridge_attribution_text() -> str:
    return (
        f"英文釋義與例句引用自 Cambridge Dictionary（{CAMBRIDGE_COPYRIGHT}），"
        "僅摘錄一義與一例供個人學習；完整內容請至官網查閱。"
    )


def lookup_cambridge(word: str) -> dict[str, Any] | None:
    """自 Cambridge 繁中詞典取得一則釋義與例句（非整本詞典複製）。"""
    if not config.CAMBRIDGE_DICT_ENABLED:
        return None
    w = word.strip().lower()
    if not w or not re.fullmatch(r"[a-z][a-z\-']*", w):
        return None

    _throttle()
    url = cambridge_word_url(w)
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=config.CAMBRIDGE_REQUEST_TIMEOUT)
        if resp.status_code != 200:
            logger.debug("Cambridge HTTP %s: %s", resp.status_code, w)
            return None
        parsed = _parse_page(resp.text, word=w, url=url)
        if parsed:
            return parsed
    except Exception as exc:
        logger.debug("Cambridge 查詢失敗 %s: %s", w, exc)
    return None


def _throttle() -> None:
    global _last_request_at
    gap = config.CAMBRIDGE_REQUEST_GAP_SEC
    if gap <= 0:
        return
    now = time.monotonic()
    wait = gap - (now - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _parse_page(html: str, *, word: str, url: str) -> dict[str, Any] | None:
    soup = BeautifulSoup(html, "html.parser")
    entries = soup.select(".entry-body__el")
    if not entries:
        return None

    best: dict[str, Any] | None = None
    best_score = -1
    for entry in entries:
        pos_el = entry.select_one(".posgram, .pos")
        pos_raw = pos_el.get_text(strip=True) if pos_el else ""
        ipa_el = entry.select_one(".ipa")
        phonetic = ipa_el.get_text(strip=True) if ipa_el else ""

        for block in entry.select(".def-block"):
            def_el = block.select_one(".def")
            if not def_el:
                continue
            meaning_en = def_el.get_text(" ", strip=True)
            trans_el = block.select_one(".trans.dtrans, .trans")
            meaning_zh = _clean_zh(trans_el.get_text(" ", strip=True) if trans_el else "")

            eg_el = block.select_one(".eg")
            example_en = eg_el.get_text(" ", strip=True) if eg_el else ""
            example_zh = _example_zh_from_block(block, example_en)

            score = _score_sense(meaning_en, pos_raw)
            if score > best_score:
                best_score = score
                best = {
                    "word": word,
                    "pos": _pos_zh(pos_raw),
                    "pos_raw": pos_raw,
                    "phonetic": phonetic,
                    "meaning_en": meaning_en,
                    "meaning_zh": meaning_zh,
                    "example_en": example_en,
                    "example_zh": example_zh,
                    "dict_source": "cambridge",
                    "dict_url": url,
                }

    return best


def _score_sense(meaning_en: str, pos_raw: str) -> int:
    low = meaning_en.lower()
    score = 0
    if any(h in low for h in _BUSINESS_HINTS):
        score += 20
    if "noun" in pos_raw.lower():
        score += 2
    score += min(len(meaning_en) // 20, 5)
    return score


def _example_zh_from_block(block: Any, example_en: str) -> str:
    examp = block.select_one(".examp.dexamp")
    if examp:
        full = examp.get_text(" ", strip=True)
        if example_en and full.startswith(example_en):
            zh = full[len(example_en) :].strip()
            if zh:
                return _clean_zh(zh)
        trans = examp.select(".trans.dtrans, .trans")
        if trans:
            return _clean_zh(trans[-1].get_text(" ", strip=True))
    for t in block.select(".trans.dtrans, .trans"):
        text = t.get_text(" ", strip=True)
        if text and example_en and text not in example_en:
            if not re.search(r"[A-Za-z]{4,}", text):
                return _clean_zh(text)
    return ""


def _clean_zh(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    text = text.replace("（經濟）", "（經濟）").strip()
    return text


def _pos_zh(pos_raw: str) -> str:
    low = pos_raw.lower()
    if "noun" in low:
        return "n. 名詞"
    if "verb" in low:
        return "v. 動詞"
    if "adjective" in low or "adj" in low:
        return "adj. 形容詞"
    if "adverb" in low or "adv" in low:
        return "adv. 副詞"
    return pos_raw or ""
