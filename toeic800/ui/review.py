"""複習佇列 — 翻卡與掌握度。"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from toeic800.db.database import ToeicDatabase


def render_review_page(db: ToeicDatabase) -> None:
    st.markdown("### 單字複習")
    limit = st.slider("本輪題數", 5, 30, 15)
    queue = db.review_queue(limit=limit)
    if not queue:
        st.info("尚無單字可複習")
        return

    if "review_idx" not in st.session_state:
        st.session_state.review_idx = 0
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False

    idx = st.session_state.review_idx % len(queue)
    card = queue[idx]
    mastery = db.get_vocab_mastery(card["id"])

    st.progress((idx + 1) / len(queue), text=f"{idx + 1} / {len(queue)}")
    st.markdown(f"**{card['word']}**  ·  掌握度 {mastery}/5")
    st.caption(card.get("article_title", ""))

    if not st.session_state.show_answer:
        if st.button("顯示答案", type="primary"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.markdown(f"*{card.get('phonetic') or ''}* · {card.get('pos') or ''}")
        st.write("**中文：**", card.get("meaning_zh") or "—")
        st.write("**英文：**", card.get("meaning_en") or "—")
        if card.get("example_en"):
            st.write("**例句：**", card["example_en"])
            st.caption(card.get("example_zh") or "")
        audio = card.get("audio_path")
        if audio and Path(audio).exists():
            st.audio(audio)

        st.markdown("掌握程度")
        c = st.columns(6)
        for i, col in enumerate(c):
            if col.button(str(i), key=f"m_{card['id']}_{i}"):
                db.log_review(card["id"], i)
                st.session_state.review_idx += 1
                st.session_state.show_answer = False
                st.rerun()

    if st.button("跳過"):
        st.session_state.review_idx += 1
        st.session_state.show_answer = False
        st.rerun()
