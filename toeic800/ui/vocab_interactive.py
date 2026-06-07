"""文章內可點擊單字（popover）與高亮。"""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

import streamlit as st

from toeic800.processing.japanese_vocabulary import ensure_ja_pronunciation
from toeic800.processing.tts import ACCENT_LABELS, ensure_tts
from toeic800.processing.vocabulary import ensure_pronunciation
from toeic800.processing.word_levels import filter_advanced_vocab_map


def build_vocab_map(vocabulary: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for v in vocabulary:
        key = v["word"]
        if key not in out:
            out[key] = v
    return out


def build_ja_vocab_map(vocabulary: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """日文單字 map（保留原文，不 lower）。"""
    return build_vocab_map(vocabulary)


def build_highlight_vocab_map(
    vocabulary: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """僅保留多益700+ / 托福雅思級生字供黃標。"""
    mapped = build_vocab_map(vocabulary)
    # 英文 key 用小寫
    en_map: dict[str, dict[str, Any]] = {}
    for v in vocabulary:
        key = v["word"].lower()
        if key not in en_map:
            en_map[key] = v
    return filter_advanced_vocab_map(en_map)


def words_in_text(text: str, vocab_map: dict[str, dict[str, Any]]) -> list[str]:
    found: list[str] = []
    for word in vocab_map:
        if re.search(rf"\b{re.escape(word)}\b", text, re.I):
            found.append(word)
    return sorted(found, key=len, reverse=True)


def words_in_ja_text(text: str, vocab_map: dict[str, dict[str, Any]]) -> list[str]:
    found: list[str] = []
    for word in sorted(vocab_map.keys(), key=len, reverse=True):
        if word in text:
            found.append(word)
    return found


def highlight_html(text: str, vocab_map: dict[str, dict[str, Any]]) -> str:
    escaped = html.escape(text)
    for word in words_in_text(text, vocab_map):
        pattern = re.compile(rf"\b({re.escape(word)})\b", re.I)
        escaped = pattern.sub(r'<mark class="vocab-hl">\1</mark>', escaped)
    return escaped


def highlight_ja_html(text: str, vocab_map: dict[str, dict[str, Any]]) -> str:
    words = sorted(vocab_map.keys(), key=len, reverse=True)
    if not words:
        return html.escape(text)
    pattern = re.compile("|".join(re.escape(w) for w in words))
    parts: list[str] = []
    last = 0
    for m in pattern.finditer(text):
        parts.append(html.escape(text[last : m.start()]))
        parts.append(f'<mark class="vocab-hl">{html.escape(m.group())}</mark>')
        last = m.end()
    parts.append(html.escape(text[last:]))
    return "".join(parts)


def render_vocab_popover(
    v: dict[str, Any], *, key_prefix: str, accent: str = "US", japanese: bool = False
) -> None:
    """在 popover 內顯示單字詳情。"""
    st.markdown(f"**{v['word']}** · {v.get('pos') or ''}")
    st.caption(v.get("phonetic") or v.get("meaning_en") or "")
    st.write("**中文：**", v.get("meaning_zh") or "—")
    if not japanese:
        st.write("**英文：**", v.get("meaning_en") or "—")
    if v.get("example_en"):
        st.write("**例句：**", v["example_en"])
        st.caption(v.get("example_zh") or "")
        lang = "ja" if japanese else "en"
        ex_audio = ensure_tts(v["example_en"], lang=lang, accent=accent if not japanese else "US")
        if ex_audio and Path(ex_audio).exists():
            st.audio(ex_audio)
    audio = v.get("audio_path")
    if japanese:
        if not audio or not Path(str(audio)).exists():
            audio = ensure_ja_pronunciation(v["word"])
    else:
        if not audio or not Path(str(audio)).exists():
            audio = ensure_pronunciation(v["word"], accent=accent)
    if audio and Path(str(audio)).exists():
        label = "日語發音" if japanese else f"發音 · {ACCENT_LABELS.get(accent, accent)}"
        st.caption(label)
        st.audio(audio)


def render_paragraph_vocab_chips(
    text: str,
    vocab_map: dict[str, dict[str, Any]],
    *,
    key_prefix: str,
    accent: str = "US",
    japanese: bool = False,
) -> None:
    """段落下方：可點擊單字 chip（popover）。"""
    hits = words_in_ja_text(text, vocab_map) if japanese else words_in_text(text, vocab_map)
    if not hits:
        return
    st.caption("點選單字查看釋義與例句：")
    cols = st.columns(min(len(hits), 6) or 1)
    for i, wkey in enumerate(hits):
        v = vocab_map[wkey]
        label = v["word"]
        with cols[i % len(cols)]:
            with st.popover(label, use_container_width=True):
                render_vocab_popover(
                    v,
                    key_prefix=f"{key_prefix}_{wkey}",
                    accent=accent,
                    japanese=japanese,
                )
