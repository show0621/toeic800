"""單字表 — 多益800格式（詞性、中文、造句、發音）。"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from toeic800.db.database import ToeicDatabase


def render_vocabulary_page(db: ToeicDatabase) -> None:
    weeks = ["全部"] + db.list_weeks()
    week = st.selectbox("週次篩選", weeks, key="vocab_week")
    week_filter = None if week == "全部" else week

    vocab_list = db.list_all_vocabulary(week_label=week_filter)
    if not vocab_list:
        st.info("尚無單字資料")
        return

    st.caption(f"共 {len(vocab_list)} 個單字 · 格式：單字｜詞性｜中文｜英文解釋｜例句")

    for v in vocab_list:
        st.markdown(
            f"""
            <div class="vocab-card">
              <span class="vocab-word">{v['word']}</span>
              <span class="vocab-pos">{v.get('pos') or ''}</span>
              <div class="vocab-ipa">{v.get('phonetic') or ''}</div>
              <div><strong>中文：</strong>{v.get('meaning_zh') or '—'}</div>
              <div><strong>英文：</strong>{v.get('meaning_en') or '—'}</div>
              <div><strong>例句：</strong>{v.get('example_en') or '—'}</div>
              <div style="color:#64748b">{v.get('example_zh') or ''}</div>
              <div style="font-size:0.8rem;color:#94a3b8;margin-top:0.35rem">出處：{v.get('article_title','')[:40]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols = st.columns([2, 2, 2])
        audio = v.get("audio_path")
        if audio and Path(audio).exists():
            cols[0].audio(audio)
        if cols[1].button("⭐ 加入複習", key=f"rev_{v['id']}"):
            db.log_review(v["id"], 1)
            st.toast(f"已加入複習：{v['word']}")
        note_key = f"vnote_{v['id']}"
        if cols[2].button("📝 筆記", key=f"btn_{note_key}"):
            st.session_state["vocab_note_id"] = v["id"]

        if st.session_state.get("vocab_note_id") == v["id"]:
            txt = st.text_input("單字筆記", key=note_key)
            if st.button("儲存", key=f"save_{note_key}") and txt.strip():
                db.add_note(txt.strip(), article_id=v["article_id"], vocab_id=v["id"])
                st.session_state.pop("vocab_note_id", None)
                st.success("已儲存")
                st.rerun()
