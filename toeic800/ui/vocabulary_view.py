"""單字表 — 詞性、中文、例句、發音。"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.processing.tts import ACCENT_LABELS, ACCENT_VOICES, ensure_tts
from toeic800.processing.vocabulary import ensure_pronunciation
from toeic800.processing.word_levels import filter_advanced_vocabulary
from toeic800.ui.context import is_japanese, jlpt_level, learning_track


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
        vocab_list = filter_advanced_vocabulary(vocab_list)

    if not vocab_list:
        st.info("尚無單字資料（多益模式僅顯示700+進階生字）")
        return

    fmt = "單字｜詞性｜讀音｜中文｜例句" if is_japanese() else "進階單字｜詞性｜中文｜英文解釋｜例句"
    st.caption(f"共 {len(vocab_list)} 個單字 · {fmt}")

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
              <div><strong>例句：</strong>{v.get('example_en') or '—'}</div>
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
