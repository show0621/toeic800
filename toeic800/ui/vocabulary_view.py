"""單字表 — 詞性、中文、例句、發音、PDF 匯出。"""

from __future__ import annotations



from datetime import datetime

from pathlib import Path



import streamlit as st



from toeic800.db.database import ToeicDatabase

from toeic800.processing.pdf_export import build_vocab_pdf

from toeic800.processing.tts import ACCENT_LABELS, ACCENT_VOICES, ensure_tts

from toeic800.processing.vocabulary import ensure_pronunciation, lookup_word, vocab_dict_fields
from toeic800.ui.vocab_attribution import render_cambridge_notice, render_dict_attribution

from toeic800.processing.vocab_selection import filter_active_vocabulary

from toeic800.ui.context import is_japanese, jlpt_level, learning_track

from toeic800.ui.disclaimer import render_disclaimer
from toeic800.ui.theme import render_vocab_card





def render_vocabulary_page(db: ToeicDatabase) -> None:

    track = learning_track()

    level = jlpt_level() if is_japanese() else None

    toeic = not is_japanese()



    if toeic:

        accent = st.selectbox(

            "朗讀口音",

            list(ACCENT_VOICES.keys()),

            format_func=lambda k: ACCENT_LABELS.get(k, k),

            key="vocab_tts_accent",

        )

    else:

        accent = "US"



    weeks = ["全部"] + db.list_weeks(track=track, jlpt_level=level)

    week = st.selectbox("週次篩選", weeks, key="vocab_week")

    week_filter = None if week == "全部" else week



    vocab_list = db.list_all_vocabulary(
        week_label=week_filter, track=track, jlpt_level=level
    )
    vocab_list = filter_active_vocabulary(vocab_list, toeic=toeic)

    if not vocab_list:

        st.info("尚無單字資料（請至文章閱讀 → 單字管理納入學習）")

        return



    fmt = "單字｜詞性｜讀音｜中文｜例句" if is_japanese() else "已納入單字｜詞性｜中文｜英文｜例句"

    st.caption(f"共 {len(vocab_list)} 個單字 · {fmt}")
    if toeic:
        render_cambridge_notice()



    _render_pdf_export(vocab_list, week=week, toeic=toeic, level=level)



    tts_lang = "ja" if is_japanese() else "en"



    for v in vocab_list:

        meaning2_label = "讀音" if is_japanese() else "英文"

        render_vocab_card(
            word=v["word"],
            pos=v.get("pos") or "",
            phonetic=v.get("phonetic") or "",
            meaning_zh=v.get("meaning_zh") or "",
            secondary_label=meaning2_label,
            secondary=v.get("meaning_en") or "",
            example_en=v.get("example_en") or "",
            example_zh=v.get("example_zh") or "",
            source=v.get("article_title") or "",
        )
        render_dict_attribution(v)

        cols = st.columns([1, 1, 1, 1, 1])
        vid = v["id"]

        if cols[0].button("🔊 語音", key=f"vgtts_{vid}"):
            with st.spinner("…"):
                if is_japanese():
                    from toeic800.processing.japanese_vocabulary import ensure_ja_pronunciation
                    audio = ensure_ja_pronunciation(v["word"])
                else:
                    audio = ensure_pronunciation(v["word"], accent=accent)
            if audio and Path(str(audio)).exists():
                db.update_vocab_entry(vid, audio_path=audio)
                st.rerun()

        if cols[1].button("📖 Cambridge", key=f"vgex_{vid}", disabled=not toeic):
            with st.spinner("…"):
                info = lookup_word(v["word"])
            if info:
                db.update_vocab_entry(vid, **vocab_dict_fields(info))
                st.rerun()
            else:
                st.warning("查無結果")

        audio = v.get("audio_path")
        if audio and Path(str(audio)).exists():
            cols[2].caption("單字")
            cols[2].audio(audio)

        if v.get("example_en") and cols[3].button("▶ 例句音", key=f"vgexa_{vid}"):
            ex_path = ensure_tts(v["example_en"], lang=tts_lang, accent=accent)
            if ex_path and Path(ex_path).exists():
                st.audio(ex_path)

        if cols[4].button("⭐ 複習", key=f"rev_{vid}"):

            db.log_review(v["id"], 1)

            st.toast(f"已加入複習：{v['word']}")

        note_key = f"vnote_{vid}"
        if st.button("📝 筆記", key=f"btn_{note_key}"):

            st.session_state["vocab_note_id"] = v["id"]



        if st.session_state.get("vocab_note_id") == v["id"]:

            txt = st.text_input("單字筆記", key=note_key)

            if st.button("儲存", key=f"save_{note_key}") and txt.strip():

                db.add_note(txt.strip(), article_id=v["article_id"], vocab_id=v["id"])

                st.session_state.pop("vocab_note_id", None)

                st.success("已儲存")

                st.rerun()



    if toeic:

        render_disclaimer(key="vocab_disclaimer")





def _render_pdf_export(

    vocab_list: list[dict],

    *,

    week: str,

    toeic: bool,

    level: str | None,

) -> None:

    with st.expander("📄 匯出 PDF 單字表", expanded=False):

        st.caption("雙欄精美排版 · 含中文、英文釋義與原創例句")

        if st.button("產生 PDF", type="primary", key="vocab_pdf_gen"):

            try:

                if toeic:

                    pdf_bytes = build_vocab_pdf(

                        vocab_list,

                        title="多益 800–900 進階單字表",

                        week_label="" if week == "全部" else week,

                        style="toeic",

                    )

                    fname = f"toeic800_vocab_{week}_{datetime.now():%Y%m%d}.pdf".replace(

                        "全部_", "all_"

                    )

                else:

                    pdf_bytes = build_vocab_pdf(

                        vocab_list,

                        title="日文新聞單字表",

                        jlpt_level=level or "",

                        style="default",

                    )

                    fname = f"japanese_vocab_{level}_{datetime.now():%Y%m%d}.pdf"

                st.session_state["vocab_pdf_bytes"] = pdf_bytes

                st.session_state["vocab_pdf_fname"] = fname

                st.success(f"已產生 {len(vocab_list)} 詞 PDF")

            except Exception as exc:

                st.error(f"PDF 產生失敗：{exc}")

                st.caption(
                    "若為雲端部署，請確認可連線 jsdelivr CDN 或 repo 已含 "
                    "toeic800/assets/fonts/NotoSansTC-Regular.ttf。"
                )



        if st.session_state.get("vocab_pdf_bytes"):

            st.download_button(

                "⬇️ 下載 PDF",

                data=st.session_state["vocab_pdf_bytes"],

                file_name=st.session_state.get("vocab_pdf_fname", "vocab.pdf"),

                mime="application/pdf",

                type="primary",

                key="vocab_pdf_dl",

            )


