"""中英 / 日中對照文章、影片、字幕、朗讀、可點擊單字。"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.processing.tts import ACCENT_LABELS, ACCENT_VOICES, ensure_tts
from toeic800.ui.context import is_japanese, jlpt_level, learning_track
from toeic800.ui.vocab_interactive import (
    build_highlight_vocab_map,
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

    toeic = not is_japanese()
    show_zh = False
    accent = "US"
    if toeic:
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            show_zh = st.toggle("顯示中文對照", value=False, key="toeic_show_zh")
        with c2:
            accent = st.selectbox(
                "朗讀口音",
                list(ACCENT_VOICES.keys()),
                format_func=lambda k: ACCENT_LABELS.get(k, k),
                key="toeic_tts_accent",
            )
        with c3:
            st.caption("Neural 語音 · 接近真人")

    st.markdown(f"### {article['title']}")
    if show_zh and article.get("title_zh"):
        st.markdown(f"*{article['title_zh']}*")
    lvl = f" · {article.get('jlpt_level')}" if article.get("jlpt_level") else ""
    st.caption(f"來源：{article['source']}{lvl} · [原文連結]({article['url']})")

    paragraphs = article.get("paragraphs") or []
    if toeic:
        highlight_map = build_highlight_vocab_map(article.get("vocabulary") or [])
    else:
        highlight_map = build_vocab_map(article.get("vocabulary") or [])

    tts_lang = "ja" if is_japanese() else "en"
    _render_reading_audio(paragraphs, article, lang=tts_lang, accent=accent)

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
            sub_title = "日中字幕" if is_japanese() else "字幕"
            st.markdown(f"#### {sub_title}")
            for sub in subs:
                st.markdown(
                    f'<div class="sub-line-en">{sub["text_en"]}</div>',
                    unsafe_allow_html=True,
                )
                if show_zh or is_japanese():
                    st.markdown(
                        f'<div class="sub-line-zh">{sub.get("text_zh") or ""}</div>',
                        unsafe_allow_html=True,
                    )
                st.divider()

    if toeic:
        st.markdown("#### 📖 閱讀")
        if highlight_map:
            st.caption("黃色標示為多益700+ / 托福雅思級生字 · 點下方按鈕查看釋義")
    else:
        st.markdown("#### 📖 日中對照")

    for i, para in enumerate(paragraphs):
        en = para["text_en"]
        if toeic and highlight_map:
            st.markdown(
                f'<div class="en-block">{highlight_html(en, highlight_map)}</div>',
                unsafe_allow_html=True,
            )
            render_paragraph_vocab_chips(
                en,
                highlight_map,
                key_prefix=f"art{article['id']}_p{i}",
                accent=accent,
            )
        else:
            st.markdown(f'<div class="en-block">{en}</div>', unsafe_allow_html=True)

        if (show_zh or is_japanese()) and para.get("text_zh"):
            st.markdown(
                f'<div class="zh-block">{para["text_zh"]}</div>',
                unsafe_allow_html=True,
            )
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
    paragraphs: list[dict],
    article: dict,
    *,
    lang: str,
    accent: str = "US",
) -> None:
    st.markdown("#### 🔊 朗讀")
    full_text = " ".join(p["text_en"] for p in paragraphs)
    aid = article["id"]
    accent_label = ACCENT_LABELS.get(accent, accent)

    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"產生全文朗讀（{accent_label}）", key=f"tts_full_{aid}"):
            st.session_state[f"tts_full_ready_{aid}"] = accent
    with c2:
        if st.button(f"產生逐段朗讀（{accent_label}）", key=f"tts_para_{aid}"):
            st.session_state[f"tts_para_ready_{aid}"] = accent

    ready_accent = st.session_state.get(f"tts_full_ready_{aid}")
    if ready_accent:
        with st.spinner(f"Neural 語音合成中（{ACCENT_LABELS.get(ready_accent, ready_accent)}）…"):
            path = ensure_tts(full_text, lang=lang, accent=ready_accent)
        if path and Path(path).exists():
            st.audio(path)
        else:
            st.warning("無法產生全文音檔")

    para_accent = st.session_state.get(f"tts_para_ready_{aid}")
    if para_accent:
        for i, para in enumerate(paragraphs):
            with st.spinner(f"段落 {i + 1}…"):
                path = ensure_tts(para["text_en"], lang=lang, accent=para_accent)
            if path and Path(path).exists():
                st.caption(f"段落 {i + 1} · {ACCENT_LABELS.get(para_accent, para_accent)}")
                st.audio(path)
