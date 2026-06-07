"""從文章抽取多益800等級單字並查字典。"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import requests

from toeic800 import config
from toeic800.processing.translator import translate_text
from toeic800.processing.vocab_examples import enrich_vocab_example, generate_example_sentence, generate_example_zh
from toeic800.processing.vocab_glossary import apply_glossary
from toeic800.processing.word_levels import ADVANCED_SEED, is_toeic800_word, score_word

logger = logging.getLogger(__name__)

# 保留舊名稱供外部引用
TOEIC800_SEED = ADVANCED_SEED

MIN_VOCAB_SCORE = 8.0

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

    for word, score in candidates:
        if score < MIN_VOCAB_SCORE:
            continue
        if len(results) >= limit:
            break
        info = lookup_word(word)
        if not info:
            continue
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


def ensure_pronunciation(word: str, accent: str = "US") -> str | None:
    """Neural TTS 發音（多口音）。"""
    from toeic800.processing.tts import ensure_word_pronunciation

    return ensure_word_pronunciation(word, accent=accent)
