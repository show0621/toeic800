"""網站免責聲明（非法律意見）。"""
from __future__ import annotations

import streamlit as st

DISCLAIMER_SHORT = (
    "本 App 為非官方多益風格學習工具，與 ETS／IIBC 無關。"
    "TOEIC® 為 ETS 註冊商標。"
)

DISCLAIMER_SECTIONS: list[tuple[str, str]] = [
    (
        "TOEIC 擬真練習",
        "每日練習題目為本專案**原創擬真練習**，僅參考 IIBC 公開之測驗格式說明（Part 5–7 題型、主題類別），"
        "**非** ETS／IIBC 官方試題，亦**未**複製任何商業機構題庫或官方考古題原文。"
        "本 App **不提供**官方認證、成績換算或任何形式的官方背書。",
    ),
    (
        "商標",
        "「TOEIC®」為 Educational Testing Service（ETS）之註冊商標。"
        "本專案使用「多益風格」「TOEIC-style」等描述性用語，僅供個人學習參考，"
        "不代表與 ETS、IIBC 或其授權單位有任何關係。",
    ),
    (
        "新聞閱讀",
        "BBC、CNN 等新聞內容之著作權屬原出版者。"
        "本 App 提供之連結、摘要與學習輔助功能，**不得**視為可任意重製、公開散播全文之授權。"
        "請優先至原文網站閱讀；若為個人學習以外之公開使用，請自行確認來源授權條款。",
    ),
    (
        "單字與例句",
        "文章單字釋義、例句與發音為學習輔助，例句為原創撰寫（非新聞原文摘錄）。"
        "字典資料可能與多益考場語意略有差異，僅供參考。",
    ),
    (
        "語音",
        "英文／日文朗讀採第三方 Neural TTS 合成，僅供學習聽力，非真人錄音或官方試題音檔。",
    ),
    (
        "一般聲明",
        "本說明**不構成法律意見**。若您計畫商業化、公開大量散播內容，"
        "請自行諮詢專業法律／智財顧問。",
    ),
]


def render_disclaimer(*, expanded: bool = False, key: str = "disclaimer") -> None:
    """側欄或頁尾免責區塊。"""
    with st.expander("⚖️ 免責聲明與版權說明", expanded=expanded):
        st.caption(DISCLAIMER_SHORT)
        for title, body in DISCLAIMER_SECTIONS:
            st.markdown(f"**{title}**")
            st.markdown(body)
        st.markdown("---")
        st.caption(
            "格式參考："
            "[IIBC TOEIC Official Format](https://www.iibc-global.org/english/toeic/test/lr/about/format.html)"
        )


def render_disclaimer_footer() -> None:
    """頁尾一行摘要。"""
    st.caption(f"⚖️ {DISCLAIMER_SHORT} 詳見側欄「免責聲明」。")
