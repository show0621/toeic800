"""Neural TTS（Edge）與 gTTS 備援，支援多口音。"""
from __future__ import annotations

import asyncio
import hashlib
import html
import logging
import random
import re
from pathlib import Path

from toeic800 import config

logger = logging.getLogger(__name__)

ACCENTS = ("US", "UK", "AU", "IN")

# 接近真人的 Neural 語音（預設單一朗讀）
ACCENT_VOICES: dict[str, str] = {
    "US": "en-US-JennyNeural",
    "UK": "en-GB-SoniaNeural",
    "AU": "en-AU-NatashaNeural",
    "IN": "en-IN-NeerjaNeural",
}

# 聽力對話：男女分別使用不同 Neural 語音
FEMALE_VOICES: dict[str, str] = {
    "US": "en-US-JennyNeural",
    "UK": "en-GB-SoniaNeural",
    "AU": "en-AU-NatashaNeural",
    "IN": "en-IN-NeerjaNeural",
}

MALE_VOICES: dict[str, str] = {
    "US": "en-US-GuyNeural",
    "UK": "en-GB-RyanNeural",
    "AU": "en-AU-WilliamNeural",
    "IN": "en-IN-PrabhatNeural",
}

ACCENT_LABELS: dict[str, str] = {
    "US": "美國",
    "UK": "英國",
    "AU": "澳洲",
    "IN": "印度",
    "MIX": "混合各國（每題不同口音）",
}

_DIALOGUE_TURN_RE = re.compile(r"^([WM]):\s*(.+)$", re.IGNORECASE | re.DOTALL)


def parse_dialogue(text: str) -> list[tuple[str, str]]:
    """解析 W:/M: 對話，回傳 [(speaker, line), ...]。"""
    text = (text or "").strip()
    if not text:
        return []
    parts = re.split(r"\s+(?=[WM]:)", text)
    turns: list[tuple[str, str]] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = _DIALOGUE_TURN_RE.match(part)
        if m:
            turns.append((m.group(1).upper(), m.group(2).strip()))
        elif not turns:
            turns.append(("N", part))
        else:
            spk, prev = turns[-1]
            turns[-1] = (spk, f"{prev} {part}")
    return turns


def _pick_dialogue_voices(
    turns: list[tuple[str, str]],
    *,
    accent: str = "MIX",
    seed: int | None = None,
) -> list[tuple[str, str, str]]:
    """為每段對話分配語音；同一題對話固定同一口音，僅男女聲不同。"""
    rng = random.Random(seed)
    if accent in ACCENTS:
        dialogue_accent = accent
    else:
        # 混合模式：每「題」隨機一種口音，對話中兩人使用相同國別（較自然）
        dialogue_accent = rng.choice(ACCENTS)

    female = (FEMALE_VOICES[dialogue_accent], dialogue_accent)
    male = (MALE_VOICES[dialogue_accent], dialogue_accent)
    out: list[tuple[str, str, str]] = []

    for speaker, _line in turns:
        if speaker == "N":
            out.append((ACCENT_VOICES[dialogue_accent], dialogue_accent, "N"))
            continue
        if speaker == "W":
            out.append((female[0], female[1], "W"))
        else:
            out.append((male[0], male[1], "M"))
    return out


def _build_dialogue_ssml(assignments: list[tuple[str, str, str, str]]) -> str:
    """assignments: [(voice, accent, label, line), ...]"""
    chunks: list[str] = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">']
    prev_label = ""
    for voice, _ac, label, line in assignments:
        if prev_label and label != prev_label:
            chunks.append('<break time="800ms"/>')
        safe = html.escape(line.strip(), quote=False)
        chunks.append(f'<voice name="{voice}">{safe}</voice>')
        prev_label = label
    chunks.append("</speak>")
    return "".join(chunks)


def dialogue_voice_summary(
    text: str,
    *,
    accent: str = "MIX",
    seed: int | None = None,
) -> str:
    """描述本次對話使用的語音組合。"""
    turns = parse_dialogue(text)
    if not turns:
        return ""
    if len(turns) == 1 and turns[0][0] == "N":
        ac = accent if accent in ACCENTS else "US"
        return f"Neural · {ACCENT_LABELS.get(ac, ac)}"
    assigned = _pick_dialogue_voices(turns, accent=accent, seed=seed)
    parts: list[str] = []
    seen: set[str] = set()
    for voice, ac, label in assigned:
        if label == "N":
            parts.append(ACCENT_LABELS.get(ac, ac))
            break
        key = f"{label}:{ac}"
        if key in seen:
            continue
        seen.add(key)
        role = "女" if label == "W" else "男"
        parts.append(f"{role}聲·{ACCENT_LABELS.get(ac, ac)}")
    return " · ".join(parts)


def ensure_dialogue_tts(
    text: str,
    *,
    accent: str = "MIX",
    seed: int | None = None,
    cache_dir: Path | None = None,
) -> str | list[str] | None:
    """聽力對話：男女不同 Neural 語音。回傳單一 mp3 或分段 mp3 列表。"""
    text = (text or "").strip()
    if not text:
        return None

    turns = parse_dialogue(text)
    if not turns:
        return None

    if len(turns) == 1 and turns[0][0] == "N":
        ac = accent if accent in ACCENTS else random.Random(seed).choice(ACCENTS)
        return ensure_tts(turns[0][1], lang="en", accent=ac, cache_dir=cache_dir)

    voice_plan = _pick_dialogue_voices(turns, accent=accent, seed=seed)
    assignments = [
        (voice, ac, label, line)
        for (voice, ac, label), (_spk, line) in zip(voice_plan, turns)
    ]
    ssml = _build_dialogue_ssml(assignments)

    cache_dir = cache_dir or (config.AUDIO_DIR / "neural" / "dialogue")
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.md5(f"{accent}:{seed}:{ssml}".encode()).hexdigest()[:20]
    dest = cache_dir / f"{key}.mp3"
    if dest.exists() and dest.stat().st_size > 0:
        return str(dest)

    if _edge_tts_save(ssml, "en-US-JennyNeural", dest):
        return str(dest)

    # SSML 失敗：分段合成，由 UI 依序播放（避免 MP3 硬拼接失真）
    segments: list[str] = []
    seg_dir = cache_dir / "segments" / key
    seg_dir.mkdir(parents=True, exist_ok=True)
    for i, (voice, _ac, _label, line) in enumerate(assignments):
        seg = seg_dir / f"{i}.mp3"
        if seg.exists() and seg.stat().st_size > 0:
            segments.append(str(seg))
            continue
        if _edge_tts_save(line.strip(), voice, seg):
            segments.append(str(seg))
    return segments if segments else None


def format_dialogue_script(text: str) -> list[tuple[str, str]]:
    """將 W:/M: 轉為 (角色, 台詞) 供 UI 顯示。"""
    turns = parse_dialogue(text)
    out: list[tuple[str, str]] = []
    for spk, line in turns:
        if spk == "W":
            out.append(("女", line))
        elif spk == "M":
            out.append(("男", line))
        else:
            out.append(("旁白", line))
    return out


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


def _edge_tts_save(text: str, voice: str, dest: Path, *, ssml: bool = False) -> bool:
    try:
        import edge_tts

        async def _run() -> None:
            v = voice or "en-US-JennyNeural"
            comm = edge_tts.Communicate(text, v)
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
