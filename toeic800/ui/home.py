"""首頁與週次列表。"""
from __future__ import annotations

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.ui.theme import hero


def render_home(db: ToeicDatabase) -> None:
    stats = db.stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("學習週數", stats["weeks"])
    c2.metric("文章", stats["articles"])
    c3.metric("單字", stats["vocabulary"])
    c4.metric("筆記", stats["notes"])

    weeks = db.list_weeks()
    if not weeks:
        st.info("尚無資料。請執行「每週抓取」或匯入示範文章。")
        return

    week = st.selectbox("選擇週次", weeks, index=0)
    articles = db.list_articles(week_label=week)
    st.markdown(f"### {week} 本週文章 ({len(articles)} 篇)")

    for art in articles:
        badge = "🎬" if art.get("has_video") else "📰"
        with st.container():
            cols = st.columns([5, 1])
            with cols[0]:
                st.markdown(f"**{badge} [{art['source']}] {art['title']}**")
                if art.get("title_zh"):
                    st.caption(art["title_zh"])
            with cols[1]:
                if st.button("閱讀", key=f"read_{art['id']}"):
                    st.session_state["article_id"] = art["id"]
                    st.session_state["nav_page"] = "文章閱讀"
                    st.rerun()
