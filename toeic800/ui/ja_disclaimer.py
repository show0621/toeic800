"""日文學習模組 — 免責聲明與版權說明（非法律意見）。"""
from __future__ import annotations

import streamlit as st

JA_DISCLAIMER_SHORT = (
    "本 App 為個人日文學習工具，與 JLPT、Mazii、MOJi 官方無關；"
    "讀音請以辭書官網為準，App 語音為 TTS 合成。"
)

JA_DISCLAIMER_SECTIONS: list[tuple[str, str]] = [
    (
        "日文單字與讀音",
        "日文單字之**讀音（假名／羅馬字）**請以 "
        "[Mazii 辭書](https://mazii.net/zh-TW/search) 與 "
        "[MOJi 辞書](https://www.mojidict.com/search) 官網條目為準；"
        "本 App 僅提供搜尋連結與學習輔助，**未**獲 Mazii、MOJi 或其營運方授權，"
        "**不得**將辭書內容大量複製、公開散播或用於商業用途。"
        "App 內顯示之讀音若與辭書不同，以辭書為準。",
    ),
    (
        "例句與新聞",
        "日文例句多摘錄自本 App 已存**新聞原文**（NHK、Yahoo 等），"
        "著作權屬原媒體；僅供個人學習，請至原文閱讀完整報導。"
        "中文譯文為機器或輔助翻譯，僅供參考。",
    ),
    (
        "語音",
        "日文朗讀採第三方 Neural TTS 合成，**非** Mazii／MOJi 原聲或真人錄音，"
        "僅供聽力練習，發音標準請以辭書官網音檔為準。",
    ),
    (
        "JLPT",
        "「JLPT」「N5–N1」為日本語能力試驗之一般稱呼；"
        "本 App **不提供**官方認證、成績預測或考古題。",
    ),
    (
        "一般聲明",
        "本說明**不構成法律意見**。若您計畫商業化、公開大量散播內容，"
        "請自行諮詢專業法律／智財顧問。",
    ),
]

JA_DICT_PDF_NOTICE = (
    "讀音請以 Mazii（mazii.net）與 MOJi 辞書（mojidict.com）為準；"
    "本表例句多來自新聞摘錄，僅供個人學習；"
    "語音為 TTS 合成，非辭書原聲。本 App 未獲上述服務商授權。"
)


def render_ja_disclaimer(*, expanded: bool = False, key: str = "ja_disclaimer") -> None:
    with st.expander("⚖️ 日文學習免責聲明與版權說明", expanded=expanded):
        st.caption(JA_DISCLAIMER_SHORT)
        for title, body in JA_DISCLAIMER_SECTIONS:
            st.markdown(f"**{title}**")
            st.markdown(body)


def render_ja_disclaimer_footer() -> None:
    st.caption(f"⚖️ {JA_DISCLAIMER_SHORT} 詳見側欄「免責聲明」。")
