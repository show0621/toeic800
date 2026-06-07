"""中英翻譯（Google 或 OpenAI）。"""
from __future__ import annotations

import logging
import time

from toeic800 import config

logger = logging.getLogger(__name__)


def translate_text(text: str, target: str = "zh-TW") -> str:
    text = (text or "").strip()
    if not text:
        return ""

    if config.OPENAI_API_KEY and config.TRANSLATOR == "openai":
        return _translate_openai(text, target)

    return _translate_google(text, target)


def translate_batch(texts: list[str], target: str = "zh-TW") -> list[str]:
    return [translate_text(t, target) for t in texts]


def _translate_google(text: str, target: str) -> str:
    try:
        from deep_translator import GoogleTranslator

        dest = "zh-TW" if target.startswith("zh") else target
        # 長文分段避免 API 限制
        if len(text) <= 4500:
            return GoogleTranslator(source="auto", target=dest).translate(text)
        parts = []
        chunk = ""
        for sentence in text.replace("\n", " ").split(". "):
            piece = sentence if sentence.endswith(".") else sentence + ". "
            if len(chunk) + len(piece) > 4000:
                parts.append(chunk)
                chunk = piece
            else:
                chunk += piece
        if chunk:
            parts.append(chunk)
        tr = GoogleTranslator(source="auto", target=dest)
        return " ".join(tr.translate(p) for p in parts)
    except Exception as exc:
        logger.warning("Google 翻譯失敗: %s", exc)
        return ""


def _translate_openai(text: str, target: str) -> str:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        lang = "繁體中文" if target.startswith("zh") else target
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"你是專業譯者，將英文新聞譯成{lang}，保留財經術語準確性。只輸出譯文。",
                },
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as exc:
        logger.warning("OpenAI 翻譯失敗，改用 Google: %s", exc)
        time.sleep(0.3)
        return _translate_google(text, target)
