"""多益 800+ 每日擬真練習 UI。"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.processing.toeic_practice import DAILY_COUNT, build_daily_set
from toeic800.processing.tts import (
    ACCENT_LABELS,
    ACCENTS,
    dialogue_voice_summary,
    ensure_dialogue_tts,
)


def render_daily_practice_page(db: ToeicDatabase) -> None:
    today = date.today()
    st.markdown("### 每日擬真練習 · 800–900 分")
    st.caption(
        f"📅 {today.isoformat()} · 聽力 / 文法 / 單字 / 閱讀 各 {DAILY_COUNT} 題 · "
        "題目每日更新（同日期題組固定，隔日換新）"
    )

    accent_options = ["MIX"] + list(ACCENTS)
    accent = st.selectbox(
        "聽力語音",
        accent_options,
        format_func=lambda k: ACCENT_LABELS.get(k, k),
        key="toeic_practice_accent",
        help="「混合各國口音」：女聲與男聲使用不同 Neural 語音，並隨機搭配美/英/澳/印口音，更接近多益真實聽力。",
    )

    tab_vocab, tab_grammar, tab_listen, tab_read = st.tabs(
        ["📝 單字", "📐 文法", "🔊 聽力", "📖 閱讀"]
    )

    with tab_vocab:
        _render_skill_tab(db, "vocab", "單字", accent=None)
    with tab_grammar:
        _render_skill_tab(db, "grammar", "文法", accent=None)
    with tab_listen:
        _render_skill_tab(db, "listening", "聽力", accent=accent)
    with tab_read:
        _render_reading_tab(db)


def _session_keys(skill: str) -> tuple[str, str, str, str]:
    prefix = f"toeic_{skill}_{date.today().isoformat()}"
    return (
        f"{prefix}_idx",
        f"{prefix}_score",
        f"{prefix}_done",
        f"{prefix}_questions",
    )


def _load_questions(db: ToeicDatabase, skill: str) -> list[dict]:
    _, _, _, qkey = _session_keys(skill)
    if qkey not in st.session_state:
        st.session_state[qkey] = build_daily_set(db, skill)
    return st.session_state[qkey]


def _render_skill_tab(
    db: ToeicDatabase,
    skill: str,
    label: str,
    *,
    accent: str | None,
) -> None:
    idx_key, score_key, done_key, qkey = _session_keys(skill)
    questions = _load_questions(db, skill)

    if not questions:
        st.warning(f"尚無{label}題目。")
        return

    if idx_key not in st.session_state:
        st.session_state[idx_key] = 0
    if score_key not in st.session_state:
        st.session_state[score_key] = 0

    idx = st.session_state[idx_key]
    if idx >= len(questions):
        st.success(
            f"今日{label}完成！得分 {st.session_state[score_key]}/{len(questions)}"
        )
        pct = st.session_state[score_key] / len(questions) * 100
        if pct >= 85:
            st.balloons()
            st.caption("🎯 優秀！已達 800+ 水準，繼續保持。")
        elif pct >= 70:
            st.caption("💪 良好！再複習錯題可望突破 800 分。")
        else:
            st.caption("📚 建議搭配文章閱讀與單字複習後再挑戰。")
        if st.button(f"重新作答今日{label}", key=f"retry_{skill}"):
            for k in (idx_key, score_key, qkey):
                st.session_state.pop(k, None)
            st.rerun()
        return

    q = questions[idx]
    options = json.loads(q["options_json"]) if isinstance(q.get("options_json"), str) else q["options"]

    st.progress((idx + 1) / len(questions), text=f"第 {idx + 1} / {len(questions)} 題 · {label}")

    if skill == "listening" and q.get("audio_text"):
        seed = hash(f"{date.today().isoformat()}:{q.get('qid', idx)}:{q['audio_text']}") & 0xFFFFFFFF
        voice_info = dialogue_voice_summary(
            q["audio_text"], accent=accent or "MIX", seed=seed
        )
        st.caption(f"🔊 請先聽音檔再作答 · Neural 真人語音 · {voice_info}")
        with st.spinner("Neural 語音合成中…"):
            audio_path = ensure_dialogue_tts(
                q["audio_text"],
                accent=accent or "MIX",
                seed=seed,
            )
        if audio_path and Path(audio_path).exists():
            st.audio(audio_path)
        else:
            st.warning("音檔載入失敗，請稍後再試或展開原文對照。")
        with st.expander("顯示聽力原文（先試著不要看）"):
            st.write(q["audio_text"])

    st.markdown(f"**{q['question']}**")
    choice = st.radio("選擇答案", options, key=f"toeic_{skill}_q_{idx}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("送出", type="primary", key=f"toeic_{skill}_submit_{idx}"):
            if choice == q["answer"]:
                st.session_state[score_key] += 1
                st.toast("✓ 正確")
            else:
                st.toast(f"✗ 正解：{q['answer']}")
            st.session_state[idx_key] += 1
            st.rerun()
    with c2:
        if q.get("explanation_zh"):
            st.caption(f"💡 {q['explanation_zh']}")


def _render_reading_tab(db: ToeicDatabase) -> None:
    skill = "reading"
    idx_key, score_key, _, qkey = _session_keys(skill)
    questions = _load_questions(db, skill)

    if not questions:
        st.warning("尚無閱讀題目。")
        return

    if idx_key not in st.session_state:
        st.session_state[idx_key] = 0
    if score_key not in st.session_state:
        st.session_state[score_key] = 0

    idx = st.session_state[idx_key]
    fmt_labels = {"single": "單篇", "double": "雙篇", "triple": "三篇"}

    if idx >= len(questions):
        st.success(f"今日閱讀完成！得分 {st.session_state[score_key]}/{len(questions)}")
        singles = sum(1 for q in questions if q.get("format") == "single")
        doubles = sum(1 for q in questions if q.get("format") == "double")
        triples = sum(1 for q in questions if q.get("format") == "triple")
        st.caption(f"題型分布：單篇 {singles} · 雙篇 {doubles} · 三篇 {triples}")
        if st.button("重新作答今日閱讀", key="retry_reading"):
            for k in (idx_key, score_key, qkey):
                st.session_state.pop(k, None)
            st.rerun()
        return

    q = questions[idx]
    fmt = q.get("format", "single")
    st.progress(
        (idx + 1) / len(questions),
        text=f"第 {idx + 1} / {len(questions)} 題 · {fmt_labels.get(fmt, fmt)}閱讀",
    )

    for p in q.get("passages") or []:
        st.markdown(
            f"""
            <div class="vocab-card" style="margin-bottom:0.75rem;">
              <div style="font-weight:600;color:#0f3d5c;margin-bottom:0.35rem;">{p.get('label','Passage')}</div>
              <div class="en-block" style="margin:0;">{p.get('text','')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    options = json.loads(q["options_json"]) if isinstance(q.get("options_json"), str) else q["options"]
    st.markdown(f"**{q['question']}**")
    choice = st.radio("選擇答案", options, key=f"toeic_reading_q_{idx}")

    if st.button("送出", type="primary", key=f"toeic_reading_submit_{idx}"):
        if choice == q["answer"]:
            st.session_state[score_key] += 1
            st.toast("✓ 正確")
        else:
            st.toast(f"✗ 正解：{q['answer']}")
        st.session_state[idx_key] += 1
        st.rerun()

    if q.get("explanation_zh"):
        st.caption(f"💡 {q['explanation_zh']}")
