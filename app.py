"""多益800分 · 經濟英文 + 日文 JLPT 學習站。"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from toeic800 import config
from toeic800.db.database import ToeicDatabase
from toeic800.processing.japanese_pipeline import (
    process_japanese_url,
    run_japanese_weekly_fetch,
)
from toeic800.processing.pipeline import process_url, run_weekly_fetch
from toeic800.ui.article_view import render_article_page
from toeic800.ui.context import is_japanese
from toeic800.ui.home import render_home
from toeic800.ui.japanese_pages import (
    render_grammar_page,
    render_listening_page,
    render_pdf_page,
    render_quiz_page,
)
from toeic800.ui.kana_pages import render_kana_page
from toeic800.ui.notes import render_notes_page
from toeic800.ui.review import render_review_page
from toeic800.ui.theme import hero, inject_theme
from toeic800.ui.toeic_practice_pages import render_daily_practice_page
from toeic800.ui.vocabulary_view import render_vocabulary_page

st.set_page_config(
    page_title="多益800 · 日文新聞學習",
    page_icon="📚",
    layout="wide",
)

inject_theme()


@st.cache_resource
def get_db() -> ToeicDatabase:
    return ToeicDatabase()


def main() -> None:
    db = get_db()

    # 首頁「閱讀」等需在 radio 渲染前寫入 nav_page
    if st.session_state.get("nav_page_pending"):
        st.session_state["nav_page"] = st.session_state.pop("nav_page_pending")

    with st.sidebar:
        track_label = st.radio(
            "學習模組",
            ["多益800", "日文 N5–N1"],
            key="learning_track",
            horizontal=True,
        )
        if track_label == "日文 N5–N1":
            st.selectbox("JLPT 等級", list(config.JLPT_LEVELS), key="jlpt_level")
            st.caption(
                "來源：NHKやさしい / 毎日小学生 / Yahoo / NHK / 朝日社説  \n"
                "[資源說明](https://vocus.cc/article/6837b674fd8978000142bdb4)"
            )
        else:
            st.caption("BBC · CNN 經濟英文")

        st.divider()
        if is_japanese():
            pages = [
                "首頁",
                "文章閱讀",
                "單字表",
                "50音學習",
                "文法",
                "聽力",
                "小考",
                "複習",
                "單字PDF",
                "我的筆記",
                "管理",
            ]
        else:
            pages = ["首頁", "每日練習", "文章閱讀", "單字表", "複習", "我的筆記", "管理"]

        if st.session_state.get("nav_page") not in pages:
            st.session_state["nav_page"] = pages[0]

        page = st.radio("導覽", pages, key="nav_page")

    if is_japanese():
        hero(
            f"日文新聞學習 · {st.session_state.get('jlpt_level', 'N5')}",
            "每週 N5–N1 各一篇日文新聞，日中對照、單字、文法、聽力、小考與 PDF，"
            "支援發音、例句、複習與筆記。",
        )
    else:
        hero(
            "多益800分 · 經濟英文週報",
            "每週精選 BBC 與 CNN 財經／國際報導，中英對照閱讀、多益級單字整理、"
            "發音與例句，並提供 800–900 分擬真每日練習（聽力、文法、單字、閱讀）。",
        )

    if page == "首頁":
        render_home(db)
    elif page == "每日練習":
        render_daily_practice_page(db)
    elif page == "文章閱讀":
        render_article_page(db)
    elif page == "單字表":
        render_vocabulary_page(db)
    elif page == "50音學習":
        render_kana_page()
    elif page == "文法":
        render_grammar_page(db)
    elif page == "聽力":
        render_listening_page(db)
    elif page == "小考":
        render_quiz_page(db)
    elif page == "複習":
        render_review_page(db)
    elif page == "單字PDF":
        render_pdf_page(db)
    elif page == "我的筆記":
        render_notes_page(db)
    elif page == "管理":
        _render_admin(db)


def _render_admin(db: ToeicDatabase) -> None:
    st.markdown("### 資料管理")
    if is_japanese():
        level = st.session_state.get("jlpt_level", "N5")
        if st.button("🔄 本週日文抓取（N5–N1 各 1 篇）", type="primary"):
            with st.spinner("抓取各級日文新聞…"):
                saved = run_japanese_weekly_fetch(db)
            st.success(f"新增：{saved}")
            st.cache_resource.clear()
            st.rerun()
        url = st.text_input("手動匯入 URL", key="ja_url")
        if st.button("匯入日文文章") and url.strip():
            meta = config.JLPT_SOURCES.get(level, {})
            with st.spinner("處理中…"):
                try:
                    aid = process_japanese_url(
                        url.strip(),
                        jlpt_level=level,
                        source=meta.get("source", "Manual"),
                        parser=meta.get("parser", "generic"),
                        db=db,
                    )
                    st.success(f"article_id={aid}")
                    st.cache_resource.clear()
                except Exception as exc:
                    st.error(str(exc))
    else:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 執行本週抓取", type="primary"):
                with st.spinner("抓取 BBC / CNN 中…"):
                    ids = run_weekly_fetch(db)
                st.success(f"新增 {len(ids)} 篇")
                st.cache_resource.clear()
                st.rerun()
        with c2:
            demo_url = "https://www.bbc.com/news/articles/cwy2yq0dj58o"
            if st.button("📥 匯入示範文章 (BBC)"):
                with st.spinner("處理示範文章…"):
                    try:
                        aid = process_url(demo_url, source="BBC", db=db)
                        st.success(f"已匯入 article_id={aid}")
                        st.cache_resource.clear()
                    except Exception as exc:
                        st.error(str(exc))
        st.markdown("#### 手動匯入 URL")
        url = st.text_input("文章網址", placeholder="https://www.bbc.com/news/...")
        src = st.selectbox("來源", ["BBC", "CNN", "Manual"])
        if st.button("匯入") and url.strip():
            with st.spinner("處理中…"):
                try:
                    aid = process_url(url.strip(), source=src, db=db)
                    st.success(f"完成 article_id={aid}")
                    st.cache_resource.clear()
                except Exception as exc:
                    st.error(str(exc))

    st.markdown("---")
    if st.button("🔄 全部每週抓取（多益 + 日文 N5–N1）"):
        with st.spinner("執行中…"):
            toeic_ids = run_weekly_fetch(db)
            ja_saved = run_japanese_weekly_fetch(db)
        st.success(f"多益 {len(toeic_ids)} 篇 · 日文 {ja_saved}")
        st.cache_resource.clear()
        st.rerun()


if __name__ == "__main__":
    main()
