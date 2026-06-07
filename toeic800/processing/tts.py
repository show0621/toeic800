"""文字轉語音（gTTS）並快取。"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path

from toeic800 import config

logger = logging.getLogger(__name__)


def ensure_tts(
    text: str,
    *,
    lang: str = "en",
    cache_dir: Path | None = None,
) -> str | None:
    text = (text or "").strip()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text)[:4800]
    cache_dir = cache_dir or (config.AUDIO_DIR / ("examples" if len(text) > 80 else "tts"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.md5(f"{lang}:{text}".encode()).hexdigest()[:20]
    dest = cache_dir / f"{key}.mp3"
    if dest.exists():
        return str(dest)
    try:
        from gtts import gTTS

        gTTS(text=text, lang=lang).save(str(dest))
        return str(dest)
    except Exception as exc:
        logger.debug("TTS 失敗: %s", exc)
        return None
