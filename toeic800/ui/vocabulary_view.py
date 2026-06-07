"""單字表 — 詞性、中文、例句、發音、PDF 匯出。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.processing.pdf_export import build_vocab_pdf
from toeic800.processing.tts import ACCENT_LABELS, ACCENT_VOICES, ensure_tts
from toeic800.processing.vocab_examples import enrich_vocab_example
from toeic800.processing.vocabulary import ensure_pronunciation
from toeic800.processing.word_levels import filter_toeic800_vocabulary
from toeic800.ui.context import is_japanese, jlpt_level, learning_track
from toeic800.ui.disclaimer import render_disclaimer


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
    if toeic:
        vocab_list = filter_toeic800_vocabulary(vocab_list)
        for i, v in enumerate(vocab_list):
            vocab_list[i] = enrich_vocab_example(v)

    if not vocab_list:
        st.info("尚無單字資料（多益模式僅顯示 800–900 進階生字）")
        return

    fmt = "單字｜詞性｜讀音｜中文｜例句" if is_japanese() else "800–900 進階單字｜詞性｜中文｜英文｜原創例句"
    st.caption(f"共 {len(vocab_list)} 個單字 · {fmt}")

    _render_pdf_export(vocab_list, week=week, toeic=toeic, level=level)

    tts_lang = "ja" if is_japanese() else "en"

    for v in vocab_list:
        meaning2_label = "讀音" if is_japanese() else "英文"
        st.markdown(
            f"""
            <div class="vocab-card">
              <span class="vocab-word">{v['word']}</span>
              <span class="vocab-pos">{v.get('pos') or ''}</span>
              <div class="vocab-ipa">{v.get('phonetic') or ''}</div>
              <div><strong>中文：</strong>{v.get('meaning_zh') or '—'}</div>
              <div><strong>{meaning2_label}：</strong>{v.get('meaning_en') or '—'}</div>
              <div><strong>例句（原創）：</strong>{v.get('example_en') or '—'}</div>
              <div style="color:#64748b">{v.get('example_zh') or ''}</div>
              <div style="font-size:0.8rem;color:#94a3b8;margin-top:0.35rem">出處：{v.get('article_title','')[:40]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols = st.columns([2, 2, 2, 2])
        if is_japanese():
            from toeic800.processing.japanese_vocabulary import ensure_ja_pronunciation

            audio = v.get("audio_path")
            if not audio or not Path(str(audio)).exists():
                audio = ensure_ja_pronunciation(v["word"])
        else:
            audio = ensure_pronunciation(v["word"], accent=accent)

        if audio and Path(str(audio)).exists():
            cols[0].caption("單字")
            cols[0].audio(audio)

        if v.get("example_en"):
            ex_path = ensure_tts(v["example_en"], lang=tts_lang, accent=accent)
            if ex_path and Path(ex_path).exists():
                cols[1].caption("例句朗讀")
                cols[1].audio(ex_path)

        if cols[2].button("⭐ 加入複習", key=f"rev_{v['id']}"):
            db.log_review(v["id"], 1)
            st.toast(f"已加入複習：{v['word']}")
        note_key = f"vnote_{v['id']}"
        if cols[3].button("📝 筆記", key=f"btn_{note_key}"):
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
                st.caption("請確認 Windows 已安裝微軟正黑體（msjh.ttc）。")

        if st.session_state.get("vocab_pdf_bytes"):
            st.download_button(
                "⬇️ 下載 PDF",
                data=st.session_state["vocab_pdf_bytes"],
                file_name=st.session_state.get("vocab_pdf_fname", "vocab.pdf"),
                mime="application/pdf",
                type="primary",
                key="vocab_pdf_dl",
            )
