"""文章內可點擊單字（popover）與高亮。"""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

import streamlit as st

from toeic800.processing.japanese_vocabulary import ensure_ja_pronunciation
from toeic800.processing.tts import ACCENT_LABELS, ensure_tts
from toeic800.ui.vocab_attribution import render_dict_attribution
from toeic800.processing.vocab_selection import filter_active_vocabulary


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
    *,
    toeic: bool = True,
) -> dict[str, dict[str, Any]]:
    """依學習範圍設定（納入／不納入／自動）決定黃標單字。"""
    active = filter_active_vocabulary(vocabulary, toeic=toeic)
    en_map: dict[str, dict[str, Any]] = {}
    for v in active:
        key = v["word"].lower()
        if key not in en_map:
            en_map[key] = v
    return en_map


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


def highlight_html(
    text: str,
    vocab_map: dict[str, dict[str, Any]],
    seen: set[str] | None = None,
) -> tuple[str, set[str]]:
    """黃標進階單字；同一篇文章每詞僅首次標示。"""
    seen = set(seen) if seen is not None else set()
    output = text
    for word in words_in_text(text, vocab_map):
        key = word.lower()
        if key in seen:
            continue
        pattern = re.compile(rf"\b({re.escape(word)})\b", re.I)
        match = pattern.search(output)
        if not match:
            continue
        token = match.group(1)
        output = (
            output[: match.start()]
            + f"\0HL\0{token}\0/EHL\0"
            + output[match.end() :]
        )
        seen.add(key)
    escaped = html.escape(output)
    escaped = escaped.replace("\0HL\0", '<mark class="vocab-hl">').replace("\0/EHL\0", "</mark>")
    return escaped, seen


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
    v: dict[str, Any],
    *,
    key_prefix: str,
    accent: str = "US",
    japanese: bool = False,
    on_demand: bool = True,
) -> None:
    """在 popover 內顯示單字詳情（預設按需產生語音／例句）。"""
    st.markdown(f"**{v['word']}** · {v.get('pos') or ''}")
    st.caption(v.get("phonetic") or v.get("meaning_en") or "")
    st.write("**中文：**", v.get("meaning_zh") or "—")
    if not japanese:
        st.write("**英文：**", v.get("meaning_en") or "—")
    render_dict_attribution(v)

    vid = v.get("id")
    lang = "ja" if japanese else "en"

    if v.get("example_en"):
        st.write("**例句（原創）：**", v["example_en"])
        st.caption(v.get("example_zh") or "")
        if on_demand:
            if st.button("🔊 例句朗讀", key=f"{key_prefix}_ex_tts"):
                with st.spinner("…"):
                    ex_audio = ensure_tts(
                        v["example_en"], lang=lang, accent=accent if not japanese else "US"
                    )
                if ex_audio and Path(ex_audio).exists():
                    st.audio(ex_audio)
        else:
            ex_audio = ensure_tts(v["example_en"], lang=lang, accent=accent if not japanese else "US")
            if ex_audio and Path(ex_audio).exists():
                st.caption("例句朗讀")
                st.audio(ex_audio)
    elif on_demand and vid and st.button("📖 查 Cambridge", key=f"{key_prefix}_cam"):
        from toeic800.processing.vocabulary import lookup_word

        info = lookup_word(v["word"])
        if info:
            st.write("**英文：**", info.get("meaning_en") or "—")
            st.write("**中文：**", info.get("meaning_zh") or "—")
            if info.get("example_en"):
                st.write("**例句：**", info["example_en"])
                st.caption(info.get("example_zh") or "")
            render_dict_attribution(info)
        else:
            st.warning("Cambridge 查無此詞")

    audio = v.get("audio_path")
    if audio and Path(str(audio)).exists():
        label = "日語發音" if japanese else f"單字發音 · {ACCENT_LABELS.get(accent, accent)}"
        st.caption(label)
        st.audio(audio)
    elif on_demand:
        if st.button(
            "🔊 產生語音" if not japanese else "🔊 產生日語發音",
            key=f"{key_prefix}_gen_tts",
        ):
            with st.spinner("…"):
                if japanese:
                    audio = ensure_ja_pronunciation(v["word"])
                else:
                    audio = ensure_pronunciation(v["word"], accent=accent)
            if audio and Path(str(audio)).exists():
                st.audio(audio)
    elif not japanese:
        audio = ensure_pronunciation(v["word"], accent=accent)
        if audio and Path(str(audio)).exists():
            st.caption(f"單字發音 · {ACCENT_LABELS.get(accent, accent)}")
            st.audio(audio)


def render_article_vocab_chips(
    vocab_map: dict[str, dict[str, Any]],
    *,
    key_prefix: str,
    accent: str = "US",
    japanese: bool = False,
) -> None:
    """文章底部：每個進階單字只顯示一次 chip。"""
    if not vocab_map:
        return
    hits = sorted(vocab_map.keys(), key=lambda k: vocab_map[k]["word"].lower())
    st.caption("點選單字查看釋義與原創例句（含朗讀）：")
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
