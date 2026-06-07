"""日文專屬：文法、聽力、小考、PDF。"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.processing.japanese_vocabulary import ensure_ja_pronunciation
from toeic800.processing.pdf_export import build_vocab_pdf
from toeic800.ui.context import jlpt_level, learning_track


def _pick_article(db: ToeicDatabase) -> dict | None:
    level = jlpt_level()
    weeks = db.list_weeks(track="japanese", jlpt_level=level)
    if not weeks:
        return None
    week = st.selectbox("週次", weeks, key="ja_sub_week")
    articles = db.list_articles(week_label=week, track="japanese", jlpt_level=level)
    if not articles:
        return None
    idx = st.selectbox(
        "文章",
        range(len(articles)),
        format_func=lambda i: articles[i]["title"][:50],
        key="ja_sub_art",
    )
    return db.get_article(articles[idx]["id"])


def render_grammar_page(db: ToeicDatabase) -> None:
    article = _pick_article(db)
    if not article:
        st.info("尚無文法資料，請先抓取本週日文文章。")
        return
    grammar = article.get("grammar") or []
    if not grammar:
        st.warning("此篇尚未分析文法點")
        return
    for g in grammar:
        st.markdown(
            f"""
            <div class="vocab-card">
              <span class="vocab-word">{g['pattern']}</span>
              <div><strong>說明：</strong>{g.get('meaning_zh') or '—'}</div>
              <div><strong>例句：</strong>{g.get('example_ja') or '—'}</div>
              <div style="color:#64748b">{g.get('example_zh') or ''}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_listening_page(db: ToeicDatabase) -> None:
    article = _pick_article(db)
    if not article:
        st.info("尚無聽力資料。")
        return

    if article.get("audio_url"):
        st.markdown("#### 🔊 NHK 朗讀（原文音檔）")
        st.audio(article["audio_url"])

    st.markdown("#### 分段聽力 · 日中字幕")
    for i, para in enumerate(article.get("paragraphs") or []):
        ja = para["text_en"]
        st.markdown(f"**{i + 1}.** {ja}")
        st.caption(para.get("text_zh") or "")
        audio = ensure_ja_pronunciation(ja[:80])
        if audio and Path(audio).exists():
            st.audio(audio)
        st.divider()


def render_quiz_page(db: ToeicDatabase) -> None:
    article = _pick_article(db)
    if not article:
        st.info("尚無小考題目。")
        return
    quiz = article.get("quiz") or []
    if not quiz:
        st.warning("此篇尚無小考")
        return

    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_idx" not in st.session_state:
        st.session_state.quiz_idx = 0

    idx = st.session_state.quiz_idx
    if idx >= len(quiz):
        st.success(f"完成！得分 {st.session_state.quiz_score}/{len(quiz)}")
        if st.button("再測一次"):
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            st.rerun()
        return

    q = quiz[idx]
    options = json.loads(q["options_json"])
    st.progress((idx + 1) / len(quiz), text=f"第 {idx + 1} / {len(quiz)} 題")
    st.markdown(f"**{q['question']}**")
    choice = st.radio("選擇答案", options, key=f"q_{q['id']}")
    if st.button("送出", type="primary"):
        if choice == q["answer"]:
            st.session_state.quiz_score += 1
            st.toast("✓ 正確")
        else:
            st.toast(f"✗ 正解：{q['answer']}")
        st.session_state.quiz_idx += 1
        st.rerun()


def render_pdf_page(db: ToeicDatabase) -> None:
    level = jlpt_level()
    vocab = db.list_all_vocabulary(track="japanese", jlpt_level=level)
    if not vocab:
        st.info("尚無單字可匯出。")
        return
    st.caption(f"共 {len(vocab)} 個 {level} 單字")
    if st.button("產生 PDF", type="primary"):
        try:
            pdf_bytes = build_vocab_pdf(
                vocab, title="日文新聞單字表", jlpt_level=level
            )
            st.download_button(
                "下載 PDF",
                data=pdf_bytes,
                file_name=f"japanese_vocab_{level}.pdf",
                mime="application/pdf",
            )
        except Exception as exc:
            st.error(f"PDF 產生失敗：{exc}")
            st.caption("若字型缺失，請確認 Windows 已安裝微軟正黑體。")
