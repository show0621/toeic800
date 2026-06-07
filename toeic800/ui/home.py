"""首頁與週次列表。"""
from __future__ import annotations

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.ui.context import is_japanese, jlpt_level, learning_track


def render_home(db: ToeicDatabase) -> None:
    track = learning_track()
    level = jlpt_level() if is_japanese() else None
    stats = db.stats(track=track, jlpt_level=level)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("學習週數", stats["weeks"])
    c2.metric("文章", stats["articles"])
    c3.metric("單字", stats["vocabulary"])
    c4.metric("筆記", stats["notes"])

    weeks = db.list_weeks(track=track, jlpt_level=level)
    if not weeks:
        hint = "請至「管理」執行每週抓取。" if is_japanese() else "請執行「每週抓取」或匯入示範文章。"
        st.info(f"尚無資料。{hint}")
        if is_japanese():
            st.markdown(
                "**本週來源（各級 1 篇）**  \n"
                "N5 NHKやさしいことば · N4 毎日小学生新聞 · N3 Yahoo!ニュース · "
                "N2 NHKニュース · N1 朝日新聞社説  \n"
                "參考：[免費日文新聞資源推薦](https://vocus.cc/article/6837b674fd8978000142bdb4)"
            )
        return

    week = st.selectbox("選擇週次", weeks, index=0)
    articles = db.list_articles(week_label=week, track=track, jlpt_level=level)
    label = f"{level} " if level else ""
    st.markdown(f"### {week} {label}本週文章 ({len(articles)} 篇)")

    for art in articles:
        badge = "🔊" if art.get("audio_url") else ("🎬" if art.get("has_video") else "📰")
        with st.container():
            cols = st.columns([5, 1])
            with cols[0]:
                st.markdown(f"**{badge} [{art['source']}] {art['title']}**")
                if art.get("title_zh"):
                    st.caption(art["title_zh"])
            with cols[1]:
                if st.button("閱讀", key=f"read_{art['id']}"):
                    st.session_state["article_id"] = art["id"]
                    st.session_state["nav_page_pending"] = "文章閱讀"
                    st.rerun()
