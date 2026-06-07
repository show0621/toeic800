"""Streamlit 主題樣式。"""

from html import escape

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
        mark.vocab-hl, .vocab-hl {
            background: #fef3c7; color: #0f3d5c; padding: 0 0.2em;
            border-radius: 3px; font-weight: 600; cursor: help;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(f"## {title}")
    st.markdown(f'<p class="hero-sub">{subtitle}</p>', unsafe_allow_html=True)


def render_vocab_card(
    *,
    word: str,
    pos: str = "",
    phonetic: str = "",
    meaning_label: str = "中文",
    meaning_zh: str = "",
    secondary_label: str = "英文",
    secondary: str = "",
    example_label: str = "例句（原創）",
    example_en: str = "",
    example_zh: str = "",
    source: str = "",
) -> None:
    """以 st.html 渲染單字卡（避免 markdown 將縮排 HTML 當成 code block）。"""
    e = escape
    parts = [
        '<div class="vocab-card">',
        f'<span class="vocab-word">{e(word)}</span>',
    ]
    if pos:
        parts.append(f' <span class="vocab-pos">{e(pos)}</span>')
    if phonetic:
        parts.append(f'<div class="vocab-ipa">{e(phonetic)}</div>')
    parts.append(
        f'<div><strong>{e(meaning_label)}：</strong>{e(meaning_zh) or "—"}</div>'
    )
    if secondary_label:
        parts.append(
            f'<div><strong>{e(secondary_label)}：</strong>{e(secondary) or "—"}</div>'
        )
    if example_label:
        parts.append(
            f'<div><strong>{e(example_label)}：</strong>{e(example_en) or "—"}</div>'
        )
    if example_zh:
        parts.append(f'<div style="color:#64748b">{e(example_zh)}</div>')
    if source:
        parts.append(
            f'<div style="font-size:0.8rem;color:#94a3b8;margin-top:0.35rem">'
            f"出處：{e(source[:40])}</div>"
        )
    parts.append("</div>")
    st.html("".join(parts))
