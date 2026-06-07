"""中英 / 日中對照文章、影片、字幕、朗讀、可點擊單字。"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.processing.tts import ensure_tts
from toeic800.ui.context import is_japanese, jlpt_level, learning_track
from toeic800.ui.vocab_interactive import (
    build_vocab_map,
    highlight_html,
    render_paragraph_vocab_chips,
)


def render_article_page(db: ToeicDatabase) -> None:
    track = learning_track()
    level = jlpt_level() if is_japanese() else None
    weeks = db.list_weeks(track=track, jlpt_level=level)
    if not weeks:
        st.warning("尚無文章")
        return

    week = st.selectbox("週次", weeks, key="art_week")
    articles = db.list_articles(week_label=week, track=track, jlpt_level=level)
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

    picked = st.selectbox(
        "選擇文章", range(len(labels)), format_func=lambda i: labels[i], index=default_idx
    )
    article = db.get_article(articles[picked]["id"])
    if not article:
        return

    st.markdown(f"### {article['title']}")
    if article.get("title_zh"):
        st.markdown(f"*{article['title_zh']}*")
    lvl = f" · {article.get('jlpt_level')}" if article.get("jlpt_level") else ""
    st.caption(f"來源：{article['source']}{lvl} · [原文連結]({article['url']})")

    vocab_map = build_vocab_map(article.get("vocabulary") or [])
    paragraphs = article.get("paragraphs") or []
    tts_lang = "ja" if is_japanese() else "en"

    _render_reading_audio(paragraphs, article, lang=tts_lang)

    if article.get("audio_url"):
        st.markdown("#### 🔊 原文音檔")
        st.audio(article["audio_url"])

    if article.get("has_video"):
        st.markdown("#### 🎬 影片")
        if article.get("video_embed_html"):
            st.markdown(article["video_embed_html"], unsafe_allow_html=True)
        elif article.get("video_url"):
            st.video(article["video_url"])

        subs = article.get("subtitles") or []
        if subs:
            sub_title = "日中字幕" if is_japanese() else "中英字幕"
            st.markdown(f"#### {sub_title}")
            for sub in subs:
                st.markdown(
                    f'<div class="sub-line-en">{sub["text_en"]}</div>'
                    f'<div class="sub-line-zh">{sub.get("text_zh") or ""}</div>',
                    unsafe_allow_html=True,
                )
                st.divider()

    read_title = "📖 日中對照" if is_japanese() else "📖 中英對照"
    st.markdown(f"#### {read_title}")
    if not is_japanese() and vocab_map:
        st.caption("黄色高亮为本文单字 · 点击下方单字按钮查看释义与例句")

    for i, para in enumerate(paragraphs):
        en = para["text_en"]
        if not is_japanese() and vocab_map:
            st.markdown(
                f'<div class="en-block">{highlight_html(en, vocab_map)}</div>',
                unsafe_allow_html=True,
            )
            render_paragraph_vocab_chips(
                en, vocab_map, key_prefix=f"art{article['id']}_p{i}"
            )
        else:
            st.markdown(f'<div class="en-block">{en}</div>', unsafe_allow_html=True)

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


def _render_reading_audio(
    paragraphs: list[dict], article: dict, *, lang: str
) -> None:
    st.markdown("#### 🔊 朗讀")
    full_text = " ".join(p["text_en"] for p in paragraphs)
    aid = article["id"]

    c1, c2 = st.columns(2)
    with c1:
        if st.button("產生全文朗讀", key=f"tts_full_{aid}"):
            st.session_state[f"tts_full_ready_{aid}"] = True
    with c2:
        if st.button("產生逐段朗讀", key=f"tts_para_{aid}"):
            st.session_state[f"tts_para_ready_{aid}"] = True

    if st.session_state.get(f"tts_full_ready_{aid}"):
        with st.spinner("產生音檔…"):
            path = ensure_tts(full_text, lang=lang)
        if path and Path(path).exists():
            st.audio(path)
        else:
            st.warning("無法產生全文音檔")

    if st.session_state.get(f"tts_para_ready_{aid}"):
        for i, para in enumerate(paragraphs):
            with st.spinner(f"段落 {i + 1}…"):
                path = ensure_tts(para["text_en"], lang=lang)
            if path and Path(path).exists():
                st.caption(f"段落 {i + 1}")
                st.audio(path)
