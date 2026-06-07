"""單字表 — 詞性、中文、例句、發音、PDF 匯出。"""

from __future__ import annotations



from datetime import datetime

from pathlib import Path



import streamlit as st



from toeic800.db.database import ToeicDatabase

from toeic800.processing.pdf_export import build_vocab_pdf

from toeic800.processing.tts import ACCENT_LABELS, ACCENT_VOICES, ensure_tts

from toeic800.processing.vocabulary import (
    build_toeic_newspaper_sections,
    ensure_pronunciation,
    lookup_word,
    prepare_vocab_export_list,
    vocab_dict_fields,
)
from toeic800.ui.vocab_attribution import render_cambridge_notice, render_dict_attribution

from toeic800.processing.vocab_selection import (
    dedupe_vocabulary_by_word,
    filter_active_vocabulary,
    group_vocabulary_by_article,
)

from toeic800.ui.context import is_japanese, jlpt_level, learning_track

from toeic800.ui.disclaimer import render_disclaimer
from toeic800.ui.ja_disclaimer import render_ja_disclaimer
from toeic800.ui.ja_dict_attribution import render_ja_dict_attribution
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
    raw_count = len(vocab_list)
    vocab_list = filter_active_vocabulary(vocab_list, toeic=toeic)
    vocab_list = dedupe_vocabulary_by_word(vocab_list)

    if not vocab_list:

        st.info("尚無單字資料（請至文章閱讀 → 單字管理納入學習）")

        return



    fmt = "單字｜詞性｜讀音｜中文｜例句" if is_japanese() else "已納入單字｜詞性｜中文｜英文｜例句"

    deduped_note = ""
    if toeic and raw_count > len(vocab_list):
        deduped_note = f" · 已合併 {raw_count - len(vocab_list)} 筆跨篇重複"
    st.caption(f"共 {len(vocab_list)} 個單字 · {fmt}{deduped_note}")
    if toeic:
        render_cambridge_notice()
    else:
        from toeic800.processing.ja_dict_lookup import ja_dict_attribution_text

        st.caption(ja_dict_attribution_text())



    _render_pdf_export(
        db, vocab_list, week=week, toeic=toeic, level=level, track=track
    )



    tts_lang = "ja" if is_japanese() else "en"

    display_groups = (
        group_vocabulary_by_article(vocab_list) if toeic else [{"items": vocab_list}]
    )

    for group in display_groups:
        if toeic and group.get("article_title"):
            st.markdown(
                f"#### 📰 {group.get('week_label') or ''} · "
                f"{group.get('source') or ''} · {group.get('article_title')}"
            )
        for v in group["items"]:
            _render_vocab_entry(
                db, v, toeic=toeic, accent=accent, tts_lang=tts_lang
            )

    if toeic:
        render_disclaimer(key="vocab_disclaimer")
    else:
        render_ja_disclaimer(key="vocab_ja_disclaimer")


def _render_vocab_entry(
    db: ToeicDatabase,
    v: dict,
    *,
    toeic: bool,
    accent: str,
    tts_lang: str,
) -> None:
    meaning2_label = "羅馬字" if is_japanese() else "英文"
    if is_japanese():
        example_label = "例句（新聞）"
    else:
        example_label = (
            "例句"
            if (v.get("dict_source") or "").lower() == "cambridge"
            else "例句（原創）"
        )

    render_vocab_card(
        word=v["word"],
        pos=v.get("pos") or "",
        phonetic=v.get("phonetic") or "",
        meaning_zh=v.get("meaning_zh") or "",
        secondary_label=meaning2_label,
        secondary=v.get("meaning_en") or "",
        example_label=example_label,
        example_en=v.get("example_en") or "",
        example_zh=v.get("example_zh") or "",
        source=v.get("article_title") or "",
    )
    render_dict_attribution(v) if toeic else render_ja_dict_attribution(v)

    if toeic:
        cols = st.columns([1, 1, 1, 1, 1])
    else:
        cols = st.columns([1, 1, 1, 1, 1, 1, 1])
    vid = v["id"]

    if cols[0].button("🔊 語音", key=f"vgtts_{vid}"):
        with st.spinner("…"):
            if is_japanese():
                from toeic800.processing.japanese_vocabulary import ensure_ja_pronunciation

                audio = ensure_ja_pronunciation(
                    v["word"], reading=v.get("phonetic") or None
                )
            else:
                audio = ensure_pronunciation(v["word"], accent=accent)
        if audio and Path(str(audio)).exists():
            db.update_vocab_entry(vid, audio_path=audio)
            st.rerun()

    if toeic:
        if cols[1].button("📖 Cambridge", key=f"vgex_{vid}"):
            with st.spinner("…"):
                info = lookup_word(v["word"])
            if info:
                db.update_vocab_entry(vid, **vocab_dict_fields(info))
                st.rerun()
            else:
                st.warning("查無結果")
        audio_col, ex_col, rev_col = cols[2], cols[3], cols[4]
    else:
        from toeic800.processing.ja_dict_lookup import (
            ja_vocab_dict_fields,
            lookup_japanese_reading,
            mazii_search_url,
            moji_search_url,
        )

        cols[1].link_button(
            "Mazii",
            v.get("mazii_url") or v.get("dict_url") or mazii_search_url(v["word"]),
            use_container_width=True,
        )
        cols[2].link_button(
            "MOJi",
            v.get("moji_url") or moji_search_url(v["word"]),
            use_container_width=True,
        )
        if cols[3].button("更新讀音", key=f"vgja_{vid}"):
            with st.spinner("…"):
                info = lookup_japanese_reading(v["word"])
            if info:
                db.update_vocab_entry(vid, **ja_vocab_dict_fields(info))
                st.rerun()
            else:
                st.warning("查無讀音")
        audio_col, ex_col, rev_col = cols[4], cols[5], cols[6]

    audio = v.get("audio_path")
    if audio and Path(str(audio)).exists():
        audio_col.caption("單字")
        audio_col.audio(audio)

    if v.get("example_en") and ex_col.button("▶ 例句音", key=f"vgexa_{vid}"):
        ex_path = ensure_tts(v["example_en"], lang=tts_lang, accent=accent)
        if ex_path and Path(ex_path).exists():
            st.audio(ex_path)

    if rev_col.button("⭐ 複習", key=f"rev_{vid}"):
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


def _render_pdf_export(

    db: ToeicDatabase,

    vocab_list: list[dict],

    *,

    week: str,

    toeic: bool,

    level: str | None,

    track: str,

) -> None:

    with st.expander("📄 匯出 PDF 單字表", expanded=False):

        if toeic:
            st.caption(
                "報紙式排版：每篇先原文、後精選單字（雙欄）· "
                "跨篇重複單字只出現一次 · 產生時查詢 Cambridge 並寫回"
            )
        else:
            st.caption(
                "單欄正式排版 · 讀音請以 Mazii／MOJi 為準 · "
                "例句多摘錄自新聞原文"
            )

        if st.button("產生 PDF", type="primary", key="vocab_pdf_gen"):

            try:
                if toeic:
                    week_filter = None if week == "全部" else week
                    with st.spinner("查詢 Cambridge 例句並排版…"):
                        sections = build_toeic_newspaper_sections(
                            db, week_label=week_filter, track=track
                        )
                        for sec in sections:
                            refreshed = prepare_vocab_export_list(sec["vocabulary"])
                            for src, item in zip(sec["vocabulary"], refreshed, strict=False):
                                vid = src.get("id")
                                if not vid:
                                    continue
                                fields = vocab_dict_fields(item)
                                if fields and any(
                                    (src.get(k) or "") != (fields.get(k) or "")
                                    for k in fields
                                ):
                                    db.update_vocab_entry(vid, **fields)
                            sec["vocabulary"] = refreshed
                    export_list = [v for s in sections for v in s["vocabulary"]]
                else:
                    sections = None
                    export_list = vocab_list

                if toeic:

                    pdf_bytes = build_vocab_pdf(

                        export_list,

                        title="多益 800–900 經濟英文週報",

                        week_label="" if week == "全部" else week,

                        style="toeic",

                        sections=sections,

                    )

                    fname = f"toeic800_vocab_{week}_{datetime.now():%Y%m%d}.pdf".replace(

                        "全部_", "all_"

                    )

                else:

                    pdf_bytes = build_vocab_pdf(

                        export_list,

                        title="日文新聞單字表",

                        jlpt_level=level or "",

                        style="japanese",

                    )

                    fname = f"japanese_vocab_{level}_{datetime.now():%Y%m%d}.pdf"

                st.session_state["vocab_pdf_bytes"] = pdf_bytes

                st.session_state["vocab_pdf_fname"] = fname

                st.success(
                    f"已產生 {len(export_list)} 詞 PDF"
                    + (f"（{len(sections)} 篇文章）" if toeic and sections else "")
                )

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


