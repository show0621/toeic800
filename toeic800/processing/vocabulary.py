"""從文章抽取多益800等級單字並查字典。"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import requests

from toeic800 import config
from toeic800.processing.cambridge_dict import lookup_cambridge
from toeic800.processing.translator import translate_text
from toeic800.processing.vocab_examples import enrich_vocab_example, generate_example_sentence, generate_example_zh
from toeic800.processing.vocab_glossary import apply_glossary
from toeic800.processing.word_levels import ADVANCED_SEED, is_toeic800_word, score_word

logger = logging.getLogger(__name__)

# 保留舊名稱供外部引用
TOEIC800_SEED = ADVANCED_SEED

MIN_VOCAB_SCORE = 8.0

_NEWSLIKE_EXAMPLE_RE = re.compile(
    r"(M&S|Marks and Spencer|BBC|CNN|Reuters|\d{1,3},\s|\blaunches\b|\bsecured a job\b)",
    re.I,
)

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "as", "is", "was", "are", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "must", "shall", "can", "this", "that", "these", "those",
    "it", "its", "they", "them", "their", "we", "our", "you", "your", "he", "she",
    "his", "her", "who", "which", "what", "when", "where", "why", "how", "not",
    "no", "yes", "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "than", "too", "very", "just", "also", "into", "over", "after",
    "before", "between", "through", "during", "without", "within", "about", "said",
    "says", "one", "two", "new", "year", "week", "day", "time", "people", "us",
}


def extract_vocabulary(
    paragraphs: list[str], limit: int | None = None
) -> list[dict[str, Any]]:
    limit = limit or config.VOCAB_PER_ARTICLE
    full_text = " ".join(paragraphs)
    candidates = _rank_candidates(full_text)
    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    for word, score in candidates:
        if score < MIN_VOCAB_SCORE:
            continue
        low = word.lower().strip("'")
        if low in seen:
            continue
        if len(results) >= limit:
            break
        seen.add(low)
        info = lookup_word(word)
        if not info:
            continue
        if info.get("dict_source") == "cambridge":
            example = info.get("example_en") or ""
            example_zh = info.get("example_zh") or ""
        else:
            example = generate_example_sentence(word, info.get("pos"))
            example_zh = generate_example_zh(word) or translate_text(example)
        entry = enrich_vocab_example(
            {
                "word": word,
                "pos": info.get("pos"),
                "meaning_en": info.get("meaning_en"),
                "meaning_zh": info.get("meaning_zh") or translate_text(info.get("meaning_en", "")),
                "phonetic": info.get("phonetic"),
                "example_en": example,
                "example_zh": example_zh,
                "audio_path": info.get("audio_path"),
                "dict_source": info.get("dict_source"),
                "dict_url": info.get("dict_url"),
            }
        )
        results.append(entry)
    return results


def _rank_candidates(text: str) -> list[tuple[str, float]]:
    words = re.findall(r"[A-Za-z][A-Za-z\-']+", text)
    freq: dict[str, int] = {}
    for w in words:
        low = w.lower().strip("'")
        if len(low) < 8 or low in STOPWORDS or not is_toeic800_word(low):
            continue
        freq[low] = freq.get(low, 0) + 1

    scored: list[tuple[str, float]] = []
    for word, count in freq.items():
        s = score_word(word, count)
        if s > 0:
            scored.append((word, s))
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored


def _example_sentence(word: str, paragraphs: list[str]) -> str:
    """已棄用：例句改為原創生成，保留供相容。"""
    return generate_example_sentence(word)


def lookup_word(word: str) -> dict[str, Any] | None:
    """優先 Cambridge Dictionary（繁中）；失敗時備援 Free Dictionary API。"""
    cambridge = lookup_cambridge(word)
    if cambridge:
        info = apply_glossary(word, cambridge)
        if not info.get("meaning_zh") and info.get("meaning_en"):
            info["meaning_zh"] = translate_text(info["meaning_en"])
        if info.get("example_en") and not info.get("example_zh"):
            info["example_zh"] = translate_text(info["example_en"])
        return info
    return _lookup_free_dictionary(word)


def _lookup_free_dictionary(word: str) -> dict[str, Any] | None:
    try:
        resp = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}",
            timeout=12,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()[0]
    except Exception as exc:
        logger.debug("字典查詢失敗 %s: %s", word, exc)
        return None

    phonetic = ""
    audio_path = None
    for ph in data.get("phonetics") or []:
        if ph.get("text"):
            phonetic = ph["text"]
        if ph.get("audio") and not audio_path:
            audio_path = _cache_audio(word, ph["audio"])

    meanings = data.get("meanings") or []
    pos = meanings[0].get("partOfSpeech") if meanings else None
    meaning_en = _pick_meaning_en(meanings) or word

    info = apply_glossary(
        word,
        {
            "pos": _pos_zh(pos),
            "phonetic": phonetic,
            "meaning_en": meaning_en,
            "meaning_zh": "",
            "audio_path": audio_path,
            "dict_source": "free",
            "dict_url": "",
        },
    )
    if not info.get("meaning_zh") and info.get("meaning_en"):
        info["meaning_zh"] = translate_text(info["meaning_en"])
    return info


def _pick_meaning_en(meanings: list[dict[str, Any]]) -> str:
    """偏好較完整、較正式的释义，避免過於簡單的第一義。"""
    candidates: list[tuple[int, str]] = []
    for m in meanings[:3]:
        for d in (m.get("definitions") or [])[:3]:
            defn = (d.get("definition") or "").strip()
            if len(defn) < 8:
                continue
            score = len(defn)
            if any(ch in defn for ch in (";", "—", "especially", "business", "formal")):
                score += 10
            candidates.append((score, defn))
    if not candidates:
        for m in meanings[:2]:
            for d in (m.get("definitions") or [])[:2]:
                defn = (d.get("definition") or "").strip()
                if defn:
                    candidates.append((len(defn), defn))
    if not candidates:
        return ""
    candidates.sort(key=lambda x: -x[0])
    return "; ".join(dict.fromkeys(c[1] for c in candidates[:2]))


def _pos_zh(pos: str | None) -> str:
    mapping = {
        "noun": "n. 名詞",
        "verb": "v. 動詞",
        "adjective": "adj. 形容詞",
        "adverb": "adv. 副詞",
        "preposition": "prep. 介系詞",
        "conjunction": "conj. 連接詞",
        "pronoun": "pron. 代名詞",
        "interjection": "int. 感嘆詞",
    }
    return mapping.get(pos or "", pos or "")


def _cache_audio(word: str, url: str) -> str | None:
    try:
        dest = config.AUDIO_DIR / f"{word.lower()}.mp3"
        if dest.exists():
            return str(dest)
        r = requests.get(url, timeout=15)
        if r.status_code == 200 and r.content:
            dest.write_bytes(r.content)
            return str(dest)
    except Exception as exc:
        logger.debug("音檔快取失敗 %s: %s", word, exc)
    return None


def vocab_dict_fields(info: dict[str, Any]) -> dict[str, Any]:
    """將 lookup 結果轉成可寫入 DB 的欄位。"""
    return {
        k: info[k]
        for k in (
            "pos",
            "meaning_zh",
            "meaning_en",
            "phonetic",
            "example_en",
            "example_zh",
            "dict_source",
            "dict_url",
        )
        if info.get(k) not in (None, "")
    }


def is_news_like_example(text: str) -> bool:
    """例句是否像新聞摘錄（舊資料或誤存）。"""
    t = (text or "").strip()
    if not t:
        return False
    if len(t) > 120:
        return True
    if _NEWSLIKE_EXAMPLE_RE.search(t):
        return True
    if t.count(".") >= 2 and re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", t):
        return True
    return False


def refresh_vocab_from_cambridge(v: dict[str, Any]) -> dict[str, Any]:
    """確保釋義／例句來自 Cambridge；必要時改為原創例句。"""
    out = dict(v)
    word = (out.get("word") or "").strip()
    if not word:
        return out

    example = (out.get("example_en") or "").strip()
    src = (out.get("dict_source") or "").lower()
    needs_lookup = (
        src != "cambridge"
        or is_news_like_example(example)
        or not example
        or not (out.get("meaning_en") or "").strip()
    )
    if not needs_lookup:
        return out

    info = lookup_word(word)
    if info:
        out.update(vocab_dict_fields(info))

    example = (out.get("example_en") or "").strip()
    if not example or is_news_like_example(example):
        ex = generate_example_sentence(word, out.get("pos"))
        out["example_en"] = ex
        out["example_zh"] = generate_example_zh(word) or translate_text(ex)

    if out.get("example_en") and not out.get("example_zh"):
        out["example_zh"] = translate_text(out["example_en"])
    return out


def prepare_vocab_export_list(
    vocabulary: list[dict[str, Any]],
    *,
    dedupe: bool = True,
    refresh_cambridge: bool = True,
) -> list[dict[str, Any]]:
    from toeic800.processing.vocab_selection import dedupe_vocabulary_by_word

    items = dedupe_vocabulary_by_word(vocabulary) if dedupe else list(vocabulary)
    if not refresh_cambridge:
        return items
    return [refresh_vocab_from_cambridge(v) for v in items]


def build_toeic_newspaper_sections(
    db: Any,
    *,
    week_label: str | None,
    track: str = "toeic",
) -> list[dict[str, Any]]:
    """組裝報紙式 PDF：每篇含原文段落 + 該篇首次出現的單字（全書去重）。"""
    from toeic800.processing.vocab_selection import (
        filter_active_vocabulary,
        normalize_vocab_word_key,
    )

    articles = db.list_articles(week_label=week_label, track=track)
    global_seen: set[str] = set()
    sections: list[dict[str, Any]] = []

    for meta in articles:
        art = db.get_article(meta["id"])
        if not art:
            continue
        active = filter_active_vocabulary(list(art.get("vocabulary") or []), toeic=True)
        words: list[dict[str, Any]] = []
        for v in active:
            key = normalize_vocab_word_key(v.get("word") or "")
            if not key or key in global_seen:
                continue
            global_seen.add(key)
            row = dict(v)
            row.setdefault("article_title", art.get("title"))
            row.setdefault("week_label", art.get("week_label"))
            row.setdefault("source", art.get("source"))
            words.append(row)
        paragraphs = list(art.get("paragraphs") or [])
        if not paragraphs and not words:
            continue
        sections.append(
            {
                "title": art.get("title") or "",
                "title_zh": art.get("title_zh") or "",
                "source": art.get("source") or "",
                "week_label": art.get("week_label") or "",
                "summary_zh": art.get("summary_zh") or "",
                "paragraphs": paragraphs,
                "vocabulary": words,
            }
        )
    return sections


def ensure_pronunciation(word: str, accent: str = "US") -> str | None:
    """Neural TTS 發音（多口音）。"""
    from toeic800.processing.tts import ensure_word_pronunciation

    return ensure_word_pronunciation(word, accent=accent)
