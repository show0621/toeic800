"""平假名・片假名 50 音：學習、練習、測驗。"""
from __future__ import annotations

import random
from pathlib import Path

import streamlit as st

from toeic800.data.kana import KanaType, all_kana, kana_char
from toeic800.processing.japanese_vocabulary import ensure_ja_pronunciation
from toeic800.processing.tts import ensure_tts


def render_kana_page() -> None:
    tab_learn, tab_practice, tab_quiz = st.tabs(["📋 五十音表", "✏️ 練習", "📝 測驗"])

    with tab_learn:
        _render_kana_chart()
    with tab_practice:
        _render_kana_practice()
    with tab_quiz:
        _render_kana_quiz()


def _render_kana_chart() -> None:
    view_mode = st.radio(
        "顯示方式",
        ["hiragana", "katakana", "both"],
        format_func=lambda x: {"hiragana": "平假名", "katakana": "片假名", "both": "平片對照"}[x],
        horizontal=True,
        key="kana_chart_view",
    )
    include_adv = st.checkbox("包含濁音・半濁音", value=False, key="kana_include_dakuon")

    st.caption("五十音表 · 每格可播放發音")

    rows = all_kana(include_dakuon=include_adv)
    current_row = ""
    cols = None
    col_i = 0
    for item in rows:
        if item["row"] != current_row:
            current_row = item["row"]
            st.markdown(f"**{current_row}**")
            cols = st.columns(5)
            col_i = 0
        h, k, r = item["hiragana"], item["katakana"], item["romaji"]
        with cols[col_i % 5]:  # type: ignore[union-attr]
            if view_mode == "both":
                st.markdown(
                    f'<div class="vocab-card" style="text-align:center;padding:0.4rem;">'
                    f'<div style="font-size:1.4rem;">{h} · {k}</div>'
                    f'<div class="vocab-ipa">{r}</div></div>',
                    unsafe_allow_html=True,
                )
                _kana_audio_widget(h)
            else:
                ch = h if view_mode == "hiragana" else k
                st.markdown(
                    f'<div class="vocab-card" style="text-align:center;padding:0.6rem;">'
                    f'<div class="vocab-word" style="font-size:2rem;">{ch}</div>'
                    f'<div class="vocab-ipa">{r}</div></div>',
                    unsafe_allow_html=True,
                )
                _kana_audio_widget(ch)
        col_i += 1


def _kana_audio_widget(char: str) -> None:
    path = _kana_audio(char)
    if path and Path(path).exists():
        st.audio(path)


def _render_kana_practice() -> None:
    mode = st.selectbox(
        "練習模式",
        ["看假名選羅馬字", "看羅馬字選假名", "聽音選假名"],
        key="kana_practice_mode",
    )
    kana_type: KanaType = st.radio(
        "假名",
        ["hiragana", "katakana"],
        format_func=lambda x: "平假名" if x == "hiragana" else "片假名",
        horizontal=True,
        key="kana_practice_type",
    )
    include_adv = st.checkbox("含濁音・半濁音", value=False, key="kana_practice_dakuon")

    pool = all_kana(include_dakuon=include_adv)
    if "kana_practice_item" not in st.session_state:
        st.session_state.kana_practice_item = random.choice(pool)

    item = st.session_state.kana_practice_item
    ch = kana_char(item, kana_type)

    if mode == "看假名選羅馬字":
        st.markdown(f"## {ch}")
        _kana_audio_button(ch)
        options = _distractors(pool, item["romaji"], "romaji")
        choice = st.radio("選擇讀音", options, key="kana_prac_pick")
        if st.button("確認", type="primary", key="kana_prac_check"):
            if choice == item["romaji"]:
                st.success("✓ 正確！")
            else:
                st.error(f"✗ 正解：{item['romaji']}")
            st.session_state.kana_practice_item = random.choice(pool)
            st.rerun()
    elif mode == "看羅馬字選假名":
        st.markdown(f"## {item['romaji']}")
        options = _distractors(pool, ch, kana_type)
        choice = st.radio("選擇假名", options, key="kana_prac_pick2")
        if st.button("確認", type="primary", key="kana_prac_check2"):
            if choice == ch:
                st.success("✓ 正確！")
            else:
                st.error(f"✗ 正解：{ch}")
            st.session_state.kana_practice_item = random.choice(pool)
            st.rerun()
    else:
        st.markdown("## 🔊 聽音選假名")
        _kana_audio_button(ch, label="播放")
        options = _distractors(pool, ch, kana_type)
        choice = st.radio("選擇假名", options, key="kana_prac_pick3")
        if st.button("確認", type="primary", key="kana_prac_check3"):
            if choice == ch:
                st.success("✓ 正確！")
            else:
                st.error(f"✗ 正解：{ch}（{item['romaji']}）")
            st.session_state.kana_practice_item = random.choice(pool)
            st.rerun()

    if st.button("下一題"):
        st.session_state.kana_practice_item = random.choice(pool)
        st.rerun()


def _render_kana_quiz() -> None:
    kana_type: KanaType = st.radio(
        "假名",
        ["hiragana", "katakana"],
        format_func=lambda x: "平假名" if x == "hiragana" else "片假名",
        horizontal=True,
        key="kana_quiz_type",
    )
    include_adv = st.checkbox("含濁音・半濁音", value=False, key="kana_quiz_dakuon")
    n_q = st.slider("題數", 5, 30, 10, key="kana_quiz_n")

    if "kana_quiz_queue" not in st.session_state:
        st.session_state.kana_quiz_queue = []
        st.session_state.kana_quiz_score = 0
        st.session_state.kana_quiz_idx = 0

    if st.button("開始測驗", type="primary", key="kana_quiz_start"):
        pool = all_kana(include_dakuon=include_adv)
        random.shuffle(pool)
        st.session_state.kana_quiz_queue = pool[:n_q]
        st.session_state.kana_quiz_score = 0
        st.session_state.kana_quiz_idx = 0
        st.session_state.kana_quiz_type_locked = kana_type
        st.rerun()

    if not st.session_state.kana_quiz_queue:
        st.info("設定題數後，按「開始測驗」。")
        return

    queue = st.session_state.kana_quiz_queue
    idx = st.session_state.kana_quiz_idx
    if idx >= len(queue):
        st.success(
            f"測驗完成！得分 {st.session_state.kana_quiz_score}/{len(queue)}"
        )
        if st.button("再測一次"):
            st.session_state.kana_quiz_queue = []
            st.rerun()
        return

    item = queue[idx]
    qtype = st.session_state.get("kana_quiz_type_locked", kana_type)
    ch = kana_char(item, qtype)
    pool = all_kana(include_dakuon=include_adv)

    st.progress((idx + 1) / len(queue), text=f"第 {idx + 1} / {len(queue)} 題")
    st.markdown(f"**{ch}** 的讀音是？")
    _kana_audio_button(ch)

    options = _distractors(pool, item["romaji"], "romaji")
    choice = st.radio("選擇答案", options, key=f"kana_q_{idx}")
    if st.button("送出", type="primary", key=f"kana_q_submit_{idx}"):
        if choice == item["romaji"]:
            st.session_state.kana_quiz_score += 1
            st.toast("✓ 正確")
        else:
            st.toast(f"✗ 正解：{item['romaji']}")
        st.session_state.kana_quiz_idx += 1
        st.rerun()


def _distractors(pool: list[dict], correct: str, field: str) -> list[str]:
    others = [
        kana_char(x, field) if field in ("hiragana", "katakana") else x["romaji"]
        for x in pool
        if (kana_char(x, field) if field in ("hiragana", "katakana") else x["romaji"])
        != correct
    ]
    random.shuffle(others)
    opts = [correct] + others[:3]
    random.shuffle(opts)
    return opts


def _kana_audio(char: str) -> str | None:
    return ensure_ja_pronunciation(char) or ensure_tts(char, lang="ja")


def _kana_audio_button(char: str, label: str = "🔊") -> None:
    path = _kana_audio(char)
    if path and Path(path).exists():
        st.audio(path)
    else:
        st.caption("（發音載入中，請稍後再試）")
