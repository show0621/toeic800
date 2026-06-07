"""日文翻譯（日→繁中）。"""
from __future__ import annotations

import logging

from toeic800.utils.zh_tw import ensure_zh_tw

logger = logging.getLogger(__name__)


def translate_ja_to_zh(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    try:
        from deep_translator import GoogleTranslator

        if len(text) <= 4500:
            result = GoogleTranslator(source="ja", target="zh-TW").translate(text)
            return ensure_zh_tw(result)
        parts = []
        buf = ""
        for sent in re_split_ja(text):
            if len(buf) + len(sent) > 4000:
                parts.append(buf)
                buf = sent
            else:
                buf += sent
        if buf:
            parts.append(buf)
        tr = GoogleTranslator(source="ja", target="zh-TW")
        return ensure_zh_tw("".join(tr.translate(p) for p in parts))
    except Exception as exc:
        logger.warning("日翻中失敗: %s", exc)
        return ""


def translate_ja_batch(texts: list[str]) -> list[str]:
    return [translate_ja_to_zh(t) for t in texts]


def re_split_ja(text: str) -> list[str]:
    import re

    return [s for s in re.split(r"(?<=[。！？\n])", text) if s.strip()]
