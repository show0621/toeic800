"""網站免責聲明（非法律意見）。"""

from __future__ import annotations



import streamlit as st

from toeic800.processing.cambridge_dict import CAMBRIDGE_COPYRIGHT



DISCLAIMER_SHORT = (

    "本 App 為非官方多益風格學習工具，與 ETS／IIBC 無關。"

    "TOEIC® 為 ETS 註冊商標。"

)



DISCLAIMER_SECTIONS: list[tuple[str, str]] = [

    (

        "TOEIC 擬真練習",

        "每日練習為**原創擬真** + **公開資源改編**（非 ETS／IIBC 官方試題）："
        "題型參考 [IIBC 公開格式](https://www.iibc-global.org/english/toeic/test/lr/about/format.html)；"
        "單字例句可引用 [Cambridge Dictionary](https://dictionary.cambridge.org/zht/)（摘錄一義一例）；"
        "片語例句可改編 [Tatoeba](https://tatoeba.org/)（CC BY 2.0 FR）；"
        "閱讀可摘錄本 App 已存新聞短段（著作權屬原媒體，請至原文閱讀）；"
        "聽力語音為 Neural TTS 合成。"
        "**禁止**使用官方考古題或商業題庫原文。"
        "本 App **不提供**官方認證或成績換算。",

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

        "英文單字之**釋義與例句**優先引用 "
        "[Cambridge Dictionary（英汉繁体）](https://dictionary.cambridge.org/zht/)，"
        "僅摘錄一則英文釋義與一則例句，並附官網連結供查閱完整條目；"
        f"內容 {CAMBRIDGE_COPYRIGHT}，本 App **未**獲 Cambridge 授權，"
        "**不得**將詞典內容大量複製、公開散播或用於商業用途。"
        "備援來源為 Free Dictionary API；若無引用標示，例句可能為原創撰寫。"
        "語音朗讀為 Neural TTS 合成，非 Cambridge 原聲。",

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


