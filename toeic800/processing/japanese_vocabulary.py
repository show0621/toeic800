"""日文單字抽取、讀音、發音。"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from toeic800 import config
from toeic800.processing.japanese_translator import translate_ja_to_zh

logger = logging.getLogger(__name__)

# 依 JLPT 常見詞性標記
POS_MAP = {
    "名詞": "n. 名詞",
    "動詞": "v. 動詞",
    "形容詞": "adj. 形容詞",
    "副詞": "adv. 副詞",
    "助詞": "part. 助詞",
    "助動詞": "aux. 助動詞",
    "連体詞": "adj. 連体詞",
    "感動詞": "int. 感動詞",
    "接続詞": "conj. 連接詞",
    "記号": "sym. 符號",
}


def extract_japanese_vocabulary(
    paragraphs: list[str], jlpt_level: str, limit: int | None = None
) -> list[dict[str, Any]]:
    limit = limit or config.VOCAB_PER_JA_ARTICLE
    full = "\n".join(paragraphs)
    tokens = _tokenize(full)
    ranked = _rank_tokens(tokens, jlpt_level)
    results: list[dict[str, Any]] = []

    for surface, pos in ranked:
        if len(results) >= limit:
            break
        if len(surface) < 2 and not re.search(r"[\u4e00-\u9fff]", surface):
            continue
        reading = _to_hiragana(surface)
        romaji = _to_romaji(reading or surface)
        example = _example_sentence(surface, paragraphs)
        meaning_zh = translate_ja_to_zh(surface)
        if example and example != surface:
            meaning_zh = translate_ja_to_zh(example)[:80] or meaning_zh

        results.append(
            {
                "word": surface,
                "pos": POS_MAP.get(pos, pos),
                "meaning_zh": meaning_zh,
                "meaning_en": romaji,
                "phonetic": reading or romaji,
                "example_en": example,
                "example_zh": translate_ja_to_zh(example) if example else "",
                "audio_path": ensure_ja_pronunciation(surface),
            }
        )
    return results


def _tokenize(text: str) -> list[tuple[str, str]]:
    try:
        from janome.tokenizer import Tokenizer

        t = Tokenizer()
        out: list[tuple[str, str]] = []
        for tok in t.tokenize(text):
            pos = tok.part_of_speech.split(",")[0]
            out.append((tok.surface, pos))
        return out
    except Exception as exc:
        logger.debug("Janome 不可用: %s", exc)
        words = re.findall(r"[\u3040-\u30ff\u4e00-\u9fff]+", text)
        return [(w, "名詞") for w in words]


def _rank_tokens(
    tokens: list[tuple[str, str]], jlpt_level: str
) -> list[tuple[str, str]]:
    skip_pos = {"助詞", "助動詞", "記号"}
    freq: dict[str, tuple[int, str]] = {}
    for surface, pos in tokens:
        if pos in skip_pos or len(surface) < 2:
            continue
        if surface in freq:
            freq[surface] = (freq[surface][0] + 1, pos)
        else:
            freq[surface] = (1, pos)

    def score(item: tuple[str, tuple[int, str]]) -> float:
        w, (cnt, pos) = item
        s = cnt * 1.0
        if re.search(r"[\u4e00-\u9fff]{2,}", w):
            s += 2
        if jlpt_level in ("N1", "N2") and len(w) >= 3:
            s += 1
        if jlpt_level in ("N5", "N4") and len(w) <= 4:
            s += 1
        return s

    ranked = sorted(freq.items(), key=score, reverse=True)
    return [(w, p) for w, (_, p) in ranked]


def _example_sentence(word: str, paragraphs: list[str]) -> str:
    for para in paragraphs:
        if word in para:
            sents = re.split(r"(?<=[。！？])", para)
            for s in sents:
                if word in s:
                    return s.strip()
            return para.strip()[:120]
    return ""


def _to_hiragana(text: str) -> str:
    try:
        from pykakasi import kakasi

        kks = kakasi()
        result = kks.convert(text)
        return "".join(r["hira"] for r in result)
    except Exception:
        return ""


def _to_romaji(text: str) -> str:
    try:
        from pykakasi import kakasi

        kks = kakasi()
        result = kks.convert(text)
        return " ".join(r["hepburn"] for r in result)
    except Exception:
        return text


def ensure_ja_pronunciation(word: str) -> str | None:
    safe = re.sub(r"[^\w\u3040-\u30ff\u4e00-\u9fff]", "", word)[:40]
    if not safe:
        return None
    dest = config.JA_AUDIO_DIR / f"{safe}.mp3"
    if dest.exists():
        return str(dest)
    try:
        from gtts import gTTS

        gTTS(text=word, lang="ja").save(str(dest))
        return str(dest)
    except Exception as exc:
        logger.debug("gTTS ja 失敗 %s: %s", word, exc)
        return None
