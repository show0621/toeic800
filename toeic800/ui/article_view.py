"""中英對照文章與影片字幕。"""
from __future__ import annotations

import streamlit as st

from toeic800.db.database import ToeicDatabase


def render_article_page(db: ToeicDatabase) -> None:
    weeks = db.list_weeks()
    if not weeks:
        st.warning("尚無文章")
        return

    week = st.selectbox("週次", weeks, key="art_week")
    articles = db.list_articles(week_label=week)
    if not articles:
        st.warning("此週無文章")
        return

    labels = [f"[{a['source']}] {a['title'][:60]}" for a in articles]
    default_idx = 0
    if st.session_state.get("article_id"):
        for i, a in enumerate(articles):
            if a["id"] == st.session_state["article_id"]:
                default_idx = i
                break

    picked = st.selectbox("選擇文章", range(len(labels)), format_func=lambda i: labels[i], index=default_idx)
    article = db.get_article(articles[picked]["id"])
    if not article:
        return

    st.markdown(f"### {article['title']}")
    if article.get("title_zh"):
        st.markdown(f"*{article['title_zh']}*")
    st.caption(f"來源：{article['source']} · [原文連結]({article['url']})")

    if article.get("has_video"):
        st.markdown("#### 🎬 影片")
        if article.get("video_embed_html"):
            st.markdown(article["video_embed_html"], unsafe_allow_html=True)
        elif article.get("video_url"):
            st.video(article["video_url"])

        subs = article.get("subtitles") or []
        if subs:
            st.markdown("#### 中英字幕")
            for sub in subs:
                st.markdown(
                    f'<div class="sub-line-en">{sub["text_en"]}</div>'
                    f'<div class="sub-line-zh">{sub.get("text_zh") or ""}</div>',
                    unsafe_allow_html=True,
                )
                st.divider()

    st.markdown("#### 📖 中英對照")
    for para in article.get("paragraphs") or []:
        st.markdown(f'<div class="en-block">{para["text_en"]}</div>', unsafe_allow_html=True)
        if para.get("text_zh"):
            st.markdown(f'<div class="zh-block">{para["text_zh"]}</div>', unsafe_allow_html=True)
        st.markdown("")

    with st.expander("📝 文章筆記"):
        note = st.text_area("新增筆記", key=f"note_art_{article['id']}")
        if st.button("儲存筆記", key=f"save_note_art_{article['id']}"):
            if note.strip():
                db.add_note(note.strip(), article_id=article["id"])
                st.success("已儲存")
                st.rerun()

    notes = db.list_notes(article_id=article["id"])
    for n in notes:
        st.text_area(
            "筆記",
            value=n["note_text"],
            key=f"edit_note_{n['id']}",
            disabled=True,
        )
