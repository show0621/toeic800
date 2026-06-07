"""日文讀音／辭典 — 參考 Mazii、MOJi 辭書（附官網連結）。"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from toeic800 import config

logger = logging.getLogger(__name__)

MAZII_SEARCH = "https://mazii.net/zh-TW/search"
MOJI_SEARCH = "https://www.mojidict.com/searchText"
JISHO_API = "https://jisho.org/api/v1/search/words"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en;q=0.7",
}

_last_jisho_at = 0.0


def mazii_search_url(word: str) -> str:
    q = quote(word.strip())
    return f"{MAZII_SEARCH}?dict=javi&type=w&query={q}"


def moji_search_url(word: str) -> str:
    return f"{MOJI_SEARCH}/{quote(word.strip())}"


def ja_dict_attribution_text() -> str:
    return (
        "日文讀音與釋義請以 "
        "[Mazii 辭書](https://mazii.net/zh-TW/search) 與 "
        "[MOJi 辞書](https://www.mojidict.com/search) 為準；"
        "本 App **未**獲上述服務商授權，僅附連結供查閱；"
        "讀音為 TTS 合成，非辭書原聲。詳見側欄免責聲明。"
    )


def lookup_japanese_reading(word: str) -> dict[str, Any] | None:
    """查日文讀音（假名＋羅馬字），並附 Mazii / MOJi 連結。"""
    w = word.strip()
    if not w:
        return None

    cached = _read_cache(w)
    if cached:
        return cached

    mazii_url = mazii_search_url(w)
    moji_url = moji_search_url(w)
    reading = ""
    romaji = ""
    meanings: list[str] = []

    if config.JA_DICT_JISHO_FALLBACK:
        jisho = _lookup_jisho(w)
        if jisho:
            reading = jisho.get("reading") or ""
            romaji = jisho.get("romaji") or ""
            meanings = jisho.get("meanings") or []

    if not reading:
        reading, romaji = _pykakasi_reading(w)

    out: dict[str, Any] = {
        "word": w,
        "phonetic": reading,
        "meaning_en": romaji,
        "meaning_zh": "",
        "dict_source": "mazii",
        "dict_url": mazii_url,
        "mazii_url": mazii_url,
        "moji_url": moji_url,
    }
    if meanings:
        out["meaning_hint_en"] = "; ".join(meanings[:3])

    _write_cache(w, out)
    return out


def ja_vocab_dict_fields(info: dict[str, Any]) -> dict[str, Any]:
    return {
        k: info[k]
        for k in (
            "phonetic",
            "meaning_en",
            "meaning_zh",
            "dict_source",
            "dict_url",
        )
        if info.get(k) not in (None, "")
    }


def _lookup_jisho(word: str) -> dict[str, Any] | None:
    _throttle_jisho()
    try:
        resp = requests.get(
            JISHO_API,
            params={"keyword": word},
            timeout=config.JA_DICT_REQUEST_TIMEOUT,
            headers=_HEADERS,
        )
        if resp.status_code != 200:
            return None
        data = resp.json().get("data") or []
    except Exception as exc:
        logger.debug("Jisho 查詢失敗 %s: %s", word, exc)
        return None

    best = _pick_jisho_entry(word, data)
    if not best:
        return None

    jp = (best.get("japanese") or [{}])[0]
    reading = (jp.get("reading") or jp.get("word") or "").strip()
    if not reading:
        return None

    romaji = _pykakasi_romaji(reading)
    senses = best.get("senses") or []
    meanings: list[str] = []
    for s in senses[:2]:
        meanings.extend(s.get("english_definitions") or [])

    return {"reading": reading, "romaji": romaji, "meanings": meanings}


def _pick_jisho_entry(word: str, data: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in data:
        for jp in item.get("japanese") or []:
            if (jp.get("word") or "") == word or (jp.get("reading") or "") == word:
                return item
    return data[0] if data else None


def _pykakasi_reading(word: str) -> tuple[str, str]:
    try:
        from pykakasi import kakasi

        result = kakasi().convert(word)
        hira = "".join(r["hira"] for r in result)
        romaji = " ".join(r["hepburn"] for r in result)
        return hira, romaji
    except Exception:
        return word, word


def _pykakasi_romaji(text: str) -> str:
    try:
        from pykakasi import kakasi

        result = kakasi().convert(text)
        return " ".join(r["hepburn"] for r in result)
    except Exception:
        return text


def _cache_path(word: str) -> Path:
    key = hashlib.md5(word.encode("utf-8")).hexdigest()
    return config.DATA_DIR / "cache" / "ja_dict" / f"{key}.json"


def _read_cache(word: str) -> dict[str, Any] | None:
    path = _cache_path(word)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if (data.get("word") or "") != word:
            return None
        age_h = (time.time() - path.stat().st_mtime) / 3600
        if age_h > config.JA_DICT_CACHE_HOURS:
            return None
        return data
    except Exception:
        return None


def _write_cache(word: str, data: dict[str, Any]) -> None:
    path = _cache_path(word)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")
    except Exception as exc:
        logger.debug("日文讀音快取寫入失敗: %s", exc)


def _throttle_jisho() -> None:
    global _last_jisho_at
    gap = config.JA_DICT_REQUEST_GAP_SEC
    if gap <= 0:
        return
    now = time.monotonic()
    wait = gap - (now - _last_jisho_at)
    if wait > 0:
        time.sleep(wait)
    _last_jisho_at = time.monotonic()
