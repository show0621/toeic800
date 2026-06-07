"""多益800分 — Streamlit 學習站。"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from toeic800.db.database import ToeicDatabase
from toeic800.processing.pipeline import process_url, run_weekly_fetch
from toeic800.ui.article_view import render_article_page
from toeic800.ui.home import render_home
from toeic800.ui.notes import render_notes_page
from toeic800.ui.review import render_review_page
from toeic800.ui.theme import hero, inject_theme
from toeic800.ui.vocabulary_view import render_vocabulary_page

st.set_page_config(
    page_title="多益800分 · 經濟英文週報",
    page_icon="📚",
    layout="wide",
)

inject_theme()


@st.cache_resource
def get_db() -> ToeicDatabase:
    return ToeicDatabase()


def main() -> None:
    db = get_db()

    with st.sidebar:
        st.markdown(
            """<div style="font-family:'Noto Serif TC',serif;font-size:1.1rem;
            color:#0f3d5c;letter-spacing:0.08em;">多益800分</div>
            <div style="font-size:0.75rem;color:#64748b;">BBC · CNN · 經濟英文</div>""",
            unsafe_allow_html=True,
        )
        page = st.radio(
            "導覽",
            ["首頁", "文章閱讀", "單字表", "複習", "我的筆記", "管理"],
            key="nav_page",
        )
        st.divider()
        st.caption("每週自動抓取 BBC / CNN 經濟、股市、國際新聞")

    hero(
        "多益800分 · 經濟英文週報",
        "每週精選 BBC 與 CNN 財經／國際報導，中英對照閱讀、多益級單字整理、"
        "發音與例句，並支援影片中英字幕、複習與筆記。",
    )

    if page == "首頁":
        render_home(db)
    elif page == "文章閱讀":
        render_article_page(db)
    elif page == "單字表":
        render_vocabulary_page(db)
    elif page == "複習":
        render_review_page(db)
    elif page == "我的筆記":
        render_notes_page(db)
    elif page == "管理":
        _render_admin(db)


def _render_admin(db: ToeicDatabase) -> None:
    st.markdown("### 資料管理")
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


if __name__ == "__main__":
    main()
