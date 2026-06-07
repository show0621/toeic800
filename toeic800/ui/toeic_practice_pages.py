"""多益 800+ 每日擬真練習 UI。"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.processing.toeic_practice import DAILY_COUNT, build_daily_set, corpus_stats
from toeic800.processing.tts import (
    ACCENT_LABELS,
    dialogue_voice_summary,
    ensure_dialogue_tts,
    format_dialogue_script,
    parse_dialogue,
)


def render_daily_practice_page(db: ToeicDatabase) -> None:
    today = date.today()
    st.markdown("### 每日擬真練習 · 800–900 分")
    st.caption(
        f"📅 {today.isoformat()} · 聽力 / 文法 / 單字 / 閱讀 各 {DAILY_COUNT} 題 · "
        "TOEIC 800–900 RAG 原創擬真題庫（Part 5–7 · 非新聞）· 可點「查看答案與解析」"
    )

    accent_options = ["US", "UK", "AU", "IN", "MIX"]
    accent = st.selectbox(
        "聽力語音",
        accent_options,
        index=0,
        format_func=lambda k: ACCENT_LABELS.get(k, k),
        key="toeic_practice_accent",
        help="同一題對話中，女聲與男聲使用相同國別口音；「混合各國」則每題隨機換口音。",
    )

    tab_vocab, tab_grammar, tab_listen, tab_read = st.tabs(
        ["📝 單字", "📐 文法", "🔊 聽力", "📖 閱讀"]
    )
    stats = corpus_stats()
    st.caption(
        f"題庫規模：單字 {stats['vocab']} · 文法 {stats['grammar']} · "
        f"聽力 {stats['listening']} · 閱讀 {stats['reading']} 題（原創擬真）"
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


def _options(q: dict) -> list[str]:
    if isinstance(q.get("options"), list):
        return q["options"]
    return json.loads(q["options_json"])


def _render_answer_popover(q: dict, choice: str | None, *, key: str) -> None:
    """可點擊查看正解與詳細解析。"""
    with st.popover("📖 查看答案與解析", use_container_width=True):
        st.markdown(q.get("part_label") or "多益擬真題")
        st.markdown("---")
        is_correct = choice == q["answer"] if choice else None
        if choice:
            icon = "✅" if is_correct else "❌"
            st.markdown(f"{icon} **你的選擇：** {choice}")
        st.markdown(f"✅ **正解：** {q['answer']}")
        st.markdown(q.get("detail_zh") or q.get("explanation_zh") or "—")
        if q.get("detail_en"):
            st.markdown("---")
            st.caption("English explanation")
            st.markdown(q["detail_en"])


def _render_submit_result(q: dict, choice: str, *, show_only: bool = False) -> None:
    """顯示作答結果與完整解析。"""
    correct = choice == q["answer"]
    if correct:
        st.success("✅ 答對了！")
    else:
        st.error(f"❌ 答錯了。正解：**{q['answer']}**")
    with st.expander("📖 詳細解析（必讀）", expanded=True):
        st.markdown(q.get("detail_zh") or q.get("explanation_zh") or "—")
        if q.get("detail_en"):
            st.caption("English")
            st.markdown(q["detail_en"])


def _render_listening_audio(q: dict, idx: int, accent: str | None) -> None:
    if not q.get("audio_text"):
        return
    turns = parse_dialogue(q["audio_text"])
    is_dialogue = len(turns) >= 2 or (len(turns) == 1 and turns[0][0] in ("W", "M"))
    st.markdown("#### Part 3 · 簡短對話" if is_dialogue else "#### Part 4 · 簡短獨白")

    seed = hash(f"{date.today().isoformat()}:{q.get('qid', idx)}:{q['audio_text']}") & 0xFFFFFFFF
    cache_key = f"listen_audio_{seed}_{accent}"
    voice_info = dialogue_voice_summary(q["audio_text"], accent=accent or "US", seed=seed)

    if cache_key not in st.session_state:
        with st.spinner("Neural 語音合成中…"):
            st.session_state[cache_key] = ensure_dialogue_tts(
                q["audio_text"],
                accent=accent or "US",
                seed=seed,
            )

    audio_result = st.session_state[cache_key]
    st.caption(f"🔊 請先聽音檔再作答 · {voice_info}")

    if isinstance(audio_result, list):
        script = format_dialogue_script(q["audio_text"])
        for i, seg in enumerate(audio_result):
            if seg and Path(seg).exists():
                role = script[i][0] if i < len(script) else f"片段 {i + 1}"
                st.caption(f"{'👩' if role == '女' else '👨'} {role}聲")
                st.audio(seg)
    elif audio_result and Path(str(audio_result)).exists():
        st.audio(str(audio_result))
    else:
        st.warning("音檔載入失敗，請稍後再試。")

    with st.expander("顯示聽力原文（建議先聽再開）"):
        script = format_dialogue_script(q["audio_text"])
        if script and script[0][0] != "旁白":
            for role, line in script:
                icon = "👩" if role == "女" else "👨"
                st.markdown(f"**{icon} {role}：** {line}")
        else:
            st.write(q["audio_text"])


def _render_skill_tab(
    db: ToeicDatabase,
    skill: str,
    label: str,
    *,
    accent: str | None,
) -> None:
    idx_key, score_key, _, qkey = _session_keys(skill)
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
        st.success(f"今日{label}完成！得分 {st.session_state[score_key]}/{len(questions)}")
        pct = st.session_state[score_key] / len(questions) * 100
        if pct >= 85:
            st.balloons()
            st.caption("🎯 優秀！已達 800+ 水準，繼續保持。")
        elif pct >= 70:
            st.caption("💪 良好！再複習錯題可望突破 800 分。")
        else:
            st.caption("📚 建議搭配文章閱讀與單字複習後再挑戰。")
        if st.button(f"重新作答今日{label}", key=f"retry_{skill}"):
            _clear_skill_session(skill, idx_key, score_key, qkey)
            st.rerun()
        return

    q = questions[idx]
    options = _options(q)
    submit_state_key = f"toeic_{skill}_submitted_{idx}"
    pending_key = f"toeic_{skill}_pending_{idx}"

    st.progress((idx + 1) / len(questions), text=f"第 {idx + 1} / {len(questions)} 題 · {label}")
    st.caption(q.get("part_label") or label)

    if skill == "listening":
        _render_listening_audio(q, idx, accent)

    st.markdown(f"**{q['question']}**")
    choice = st.radio("選擇答案", options, key=f"toeic_{skill}_q_{idx}")

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        submit = st.button("送出答案", type="primary", key=f"toeic_{skill}_submit_{idx}")
    with c2:
        _render_answer_popover(q, choice, key=f"toeic_{skill}_ans_{idx}")
    with c3:
        if st.session_state.get(submit_state_key):
            if st.button("下一題 →", key=f"toeic_{skill}_next_{idx}"):
                st.session_state.pop(submit_state_key, None)
                st.session_state.pop(pending_key, None)
                st.session_state[idx_key] += 1
                st.rerun()

    if submit:
        st.session_state[submit_state_key] = True
        st.session_state[pending_key] = choice
        if choice == q["answer"]:
            st.session_state[score_key] = st.session_state.get(score_key, 0) + 1
        st.rerun()

    if st.session_state.get(submit_state_key):
        _render_submit_result(q, st.session_state.get(pending_key, choice), show_only=True)


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
    if idx >= len(questions):
        st.success(f"今日閱讀完成！得分 {st.session_state[score_key]}/{len(questions)}")
        singles = sum(1 for q in questions if q.get("format") == "single")
        doubles = sum(1 for q in questions if q.get("format") == "double")
        triples = sum(1 for q in questions if q.get("format") == "triple")
        st.caption(f"題型分布：單篇 {singles} · 雙篇 {doubles} · 三篇 {triples}")
        if st.button("重新作答今日閱讀", key="retry_reading"):
            _clear_skill_session(skill, idx_key, score_key, qkey)
            st.rerun()
        return

    q = questions[idx]
    options = _options(q)
    submit_state_key = f"toeic_reading_submitted_{idx}"
    pending_key = f"toeic_reading_pending_{idx}"

    st.progress((idx + 1) / len(questions), text=f"第 {idx + 1} / {len(questions)} 題 · 閱讀")
    st.caption(q.get("part_label") or "Part 7 · 閱讀")

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

    st.markdown(f"**{q['question']}**")
    choice = st.radio("選擇答案", options, key=f"toeic_reading_q_{idx}")

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        submit = st.button("送出答案", type="primary", key=f"toeic_reading_submit_{idx}")
    with c2:
        _render_answer_popover(q, choice, key=f"toeic_reading_ans_{idx}")
    with c3:
        if st.session_state.get(submit_state_key):
            if st.button("下一題 →", key=f"toeic_reading_next_{idx}"):
                st.session_state.pop(submit_state_key, None)
                st.session_state.pop(pending_key, None)
                st.session_state[idx_key] += 1
                st.rerun()

    if submit:
        st.session_state[submit_state_key] = True
        st.session_state[pending_key] = choice
        if choice == q["answer"]:
            st.session_state[score_key] = st.session_state.get(score_key, 0) + 1
        st.rerun()

    if st.session_state.get(submit_state_key):
        _render_submit_result(q, st.session_state.get(pending_key, choice), show_only=True)


def _clear_skill_session(skill: str, idx_key: str, score_key: str, qkey: str) -> None:
    for k in (idx_key, score_key, qkey):
        st.session_state.pop(k, None)
    if skill == "listening":
        for k in list(st.session_state.keys()):
            if str(k).startswith("listen_audio_"):
                st.session_state.pop(k, None)
    prefix = f"toeic_{skill}_"
    for k in list(st.session_state.keys()):
        if str(k).startswith(prefix) and ("submitted_" in str(k) or "pending_" in str(k)):
            st.session_state.pop(k, None)
