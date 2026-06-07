"""日文辭典引用 UI（Mazii / MOJi）。"""
from __future__ import annotations

from typing import Any

import streamlit as st

from toeic800.processing.ja_dict_lookup import (
    ja_dict_attribution_text,
    lookup_japanese_reading,
    mazii_search_url,
    moji_search_url,
)


def render_ja_dict_attribution(v: dict[str, Any] | None = None) -> None:
    mazii = (v or {}).get("mazii_url") or (v or {}).get("dict_url") or mazii_search_url(
        (v or {}).get("word") or ""
    )
    moji = (v or {}).get("moji_url") or moji_search_url((v or {}).get("word") or "")
    word = (v or {}).get("word") or ""
    if word:
        st.caption(
            f"📖 讀音請以 "
            f"[Mazii]({mazii}) · "
            f"[MOJi 辞書]({moji}) 為準 · "
            "App 語音為 TTS 合成 · 本 App 未獲辭書商授權"
        )
    else:
        st.caption(ja_dict_attribution_text())


def render_ja_dict_links(word: str, *, key_prefix: str) -> None:
    if not word:
        return
    c1, c2 = st.columns(2)
    c1.link_button("Mazii", mazii_search_url(word), use_container_width=True)
    c2.link_button("MOJi", moji_search_url(word), use_container_width=True)


def refresh_japanese_reading(word: str) -> dict[str, Any] | None:
    return lookup_japanese_reading(word)
