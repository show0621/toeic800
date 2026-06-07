"""Streamlit 主題樣式。"""

import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600&family=Source+Serif+4:wght@400;600&display=swap');
        .stApp { background: linear-gradient(165deg, #f7f4ef 0%, #eef2f6 45%, #f5f0ea 100%); }
        h1, h2, h3 { font-family: 'Noto Serif TC', serif; color: #1a2a3a; }
        .en-block { font-family: 'Source Serif 4', Georgia, serif; font-size: 1.05rem; line-height: 1.75; color: #1e293b; }
        .zh-block { font-family: 'Noto Serif TC', serif; font-size: 1rem; line-height: 1.8; color: #475569; border-left: 3px solid #c4a574; padding-left: 1rem; margin-top: 0.35rem; }
        .vocab-card { background: #fff; border: 1px solid #e2ddd4; border-radius: 12px; padding: 1rem 1.1rem; margin-bottom: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
        .vocab-word { font-size: 1.35rem; font-weight: 600; color: #0f3d5c; }
        .vocab-pos { color: #8b7355; font-size: 0.85rem; margin-left: 0.5rem; }
        .vocab-ipa { color: #64748b; font-size: 0.9rem; }
        .sub-line-en { font-weight: 500; color: #0f172a; }
        .sub-line-zh { color: #64748b; font-size: 0.92rem; margin-top: 0.15rem; }
        .hero-sub { color: #64748b; max-width: 52rem; line-height: 1.7; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(f"## {title}")
    st.markdown(f'<p class="hero-sub">{subtitle}</p>', unsafe_allow_html=True)
