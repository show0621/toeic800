"""Neural TTS（Edge）與 gTTS 備援，支援多口音。"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from pathlib import Path

from toeic800 import config

logger = logging.getLogger(__name__)

# 接近真人的 Neural 語音
ACCENT_VOICES: dict[str, str] = {
    "US": "en-US-JennyNeural",
    "UK": "en-GB-SoniaNeural",
    "AU": "en-AU-NatashaNeural",
    "IN": "en-IN-NeerjaNeural",
}

ACCENT_LABELS: dict[str, str] = {
    "US": "美國",
    "UK": "英國",
    "AU": "澳洲",
    "IN": "印度",
}


def ensure_tts(
    text: str,
    *,
    lang: str = "en",
    accent: str = "US",
    cache_dir: Path | None = None,
) -> str | None:
    text = (text or "").strip()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text)[:4800]

    sub = "examples" if len(text) > 80 else "tts"
    if lang == "en":
        sub = f"neural/{accent.lower()}" if len(text) <= 80 else f"neural/{accent.lower()}/examples"
    cache_dir = cache_dir or (config.AUDIO_DIR / sub)
    cache_dir.mkdir(parents=True, exist_ok=True)

    voice = ACCENT_VOICES.get(accent, ACCENT_VOICES["US"]) if lang == "en" else lang
    key = hashlib.md5(f"{voice}:{text}".encode()).hexdigest()[:20]
    dest = cache_dir / f"{key}.mp3"
    if dest.exists():
        return str(dest)

    if lang == "en":
        if _edge_tts_save(text, voice, dest):
            return str(dest)

    return _gtts_save(text, lang, dest)


def ensure_word_pronunciation(word: str, accent: str = "US") -> str | None:
    return ensure_tts(word, lang="en", accent=accent, cache_dir=config.AUDIO_DIR / "words" / accent.lower())


def _edge_tts_save(text: str, voice: str, dest: Path) -> bool:
    try:
        import edge_tts

        async def _run() -> None:
            comm = edge_tts.Communicate(text, voice)
            await comm.save(str(dest))

        asyncio.run(_run())
        return dest.exists() and dest.stat().st_size > 0
    except Exception as exc:
        logger.debug("Edge TTS 失敗: %s", exc)
        return False


def _gtts_save(text: str, lang: str, dest: Path) -> str | None:
    try:
        from gtts import gTTS

        tld_map = {"en": "com", "ja": "co.jp"}
        gTTS(text=text, lang=lang if lang != "en" else "en", tld=tld_map.get(lang, "com")).save(
            str(dest)
        )
        return str(dest) if dest.exists() else None
    except Exception as exc:
        logger.debug("gTTS 失敗: %s", exc)
        return None
