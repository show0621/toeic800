"""文章內可點擊單字（popover）與高亮。"""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

import streamlit as st

from toeic800.processing.tts import ACCENT_LABELS, ensure_tts
from toeic800.processing.vocabulary import ensure_pronunciation
from toeic800.processing.word_levels import filter_advanced_vocab_map


def build_vocab_map(vocabulary: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for v in vocabulary:
        key = v["word"].lower()
        if key not in out:
            out[key] = v
    return out


def build_highlight_vocab_map(
    vocabulary: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """僅保留多益700+ / 托福雅思級生字供黃標。"""
    return filter_advanced_vocab_map(build_vocab_map(vocabulary))


def words_in_text(text: str, vocab_map: dict[str, dict[str, Any]]) -> list[str]:
    found: list[str] = []
    for word in vocab_map:
        if re.search(rf"\b{re.escape(word)}\b", text, re.I):
            found.append(word)
    return sorted(found, key=len, reverse=True)


def highlight_html(text: str, vocab_map: dict[str, dict[str, Any]]) -> str:
    escaped = html.escape(text)
    for word in words_in_text(text, vocab_map):
        pattern = re.compile(rf"\b({re.escape(word)})\b", re.I)
        escaped = pattern.sub(r'<mark class="vocab-hl">\1</mark>', escaped)
    return escaped


def render_vocab_popover(
    v: dict[str, Any], *, key_prefix: str, accent: str = "US"
) -> None:
    """在 popover 內顯示單字詳情。"""
    st.markdown(f"**{v['word']}** · {v.get('pos') or ''}")
    st.caption(v.get("phonetic") or "")
    st.write("**中文：**", v.get("meaning_zh") or "—")
    st.write("**英文：**", v.get("meaning_en") or "—")
    if v.get("example_en"):
        st.write("**例句：**", v["example_en"])
        st.caption(v.get("example_zh") or "")
        ex_audio = ensure_tts(v["example_en"], lang="en", accent=accent)
        if ex_audio and Path(ex_audio).exists():
            st.audio(ex_audio)
    audio = v.get("audio_path")
    if not audio or not Path(str(audio)).exists():
        audio = ensure_pronunciation(v["word"], accent=accent)
    if audio and Path(str(audio)).exists():
        st.caption(f"發音 · {ACCENT_LABELS.get(accent, accent)}")
        st.audio(audio)


def render_paragraph_vocab_chips(
    text: str,
    vocab_map: dict[str, dict[str, Any]],
    *,
    key_prefix: str,
    accent: str = "US",
) -> None:
    """段落下方：可點擊單字 chip（popover）。"""
    hits = words_in_text(text, vocab_map)
    if not hits:
        return
            st.caption("點選生字查看釋義與例句：")
    cols = st.columns(min(len(hits), 6) or 1)
    for i, wkey in enumerate(hits):
        v = vocab_map[wkey]
        label = v["word"]
        with cols[i % len(cols)]:
            with st.popover(label, use_container_width=True):
                render_vocab_popover(v, key_prefix=f"{key_prefix}_{wkey}", accent=accent)
