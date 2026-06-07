"""從 article_view / vocab_curation 共用的字典引用 UI。"""
from __future__ import annotations

from typing import Any

import streamlit as st

from toeic800.processing.cambridge_dict import CAMBRIDGE_COPYRIGHT, cambridge_attribution_text


def render_dict_attribution(v: dict[str, Any]) -> None:
    """顯示 Cambridge 等字典來源與版權說明。"""
    source = (v.get("dict_source") or "").lower()
    url = v.get("dict_url") or ""
    if source == "cambridge" and url:
        st.caption(
            f"📖 釋義／例句引用自 "
            f"[Cambridge Dictionary（繁中）]({url}) · {CAMBRIDGE_COPYRIGHT} · "
            "僅摘錄一義一例供個人學習，完整內容請至官網查閱。"
        )
    elif source == "free":
        st.caption("釋義來源：Free Dictionary API（備援）· 例句為原創或 Cambridge 查詢結果。")


def render_cambridge_notice() -> None:
    st.caption(cambridge_attribution_text())
