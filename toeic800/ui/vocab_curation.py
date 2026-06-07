"""文章單字管理：納入／不納入、按需產生語音與例句。"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

import streamlit as st

from toeic800.db.database import ToeicDatabase
from toeic800.processing.japanese_vocabulary import ensure_ja_pronunciation
from toeic800.processing.translator import translate_text
from toeic800.processing.tts import ACCENT_LABELS, ensure_tts
from toeic800.processing.vocab_glossary import apply_glossary
from toeic800.processing.vocab_selection import (
    STATUS_LABELS,
    STUDY_AUTO,
    STUDY_EXCLUDED,
    STUDY_INCLUDED,
    filter_active_vocabulary,
    normalize_study_status,
    vocab_is_active,
)
from toeic800.processing.vocabulary import ensure_pronunciation, lookup_word, vocab_dict_fields
from toeic800.processing.word_levels import is_toeic800_word
from toeic800.ui.vocab_attribution import render_dict_attribution


def _dict_fields(info: dict[str, Any]) -> dict[str, Any]:
    return vocab_dict_fields(info)


def _fresh_db() -> ToeicDatabase:
    """略過 cache_resource，取得目前程式碼的 ToeicDatabase。"""
    return ToeicDatabase()


def _set_study_status(db: ToeicDatabase, vocab_id: int, status: str) -> None:
    """寫入 study_status；相容舊版快取 db 實例。"""
    setter = getattr(db, "set_vocab_study_status", None)
    if callable(setter):
        setter(vocab_id, status)
        return
    updater = getattr(db, "update_vocab_entry", None)
    if callable(updater):
        updater(vocab_id, study_status=status)
        return
    _fresh_db().set_vocab_study_status(vocab_id, status)


def _update_vocab(db: ToeicDatabase, vocab_id: int, **fields: Any) -> None:
    updater = getattr(db, "update_vocab_entry", None)
    if callable(updater):
        updater(vocab_id, **fields)
    else:
        _fresh_db().update_vocab_entry(vocab_id, **fields)


def _invalidate_db_cache() -> None:
    st.cache_resource.clear()


def _status_badge(status: str) -> str:
    label = STATUS_LABELS.get(status, status)
    if status == STUDY_INCLUDED:
        return f"🟢 {label}"
    if status == STUDY_EXCLUDED:
        return f"⚪ {label}"
    return f"🔵 {label}"


def scan_article_word_candidates(paragraphs: list[dict[str, Any]], limit: int = 40) -> list[str]:
    text = " ".join(p.get("text_en") or "" for p in paragraphs)
    words = re.findall(r"[A-Za-z][A-Za-z'-]{3,}", text)
    counts = Counter(w.lower().strip("'-") for w in words if len(w) >= 4)
    return [w for w, _ in counts.most_common(limit)]


def render_article_vocab_curation(
    db: ToeicDatabase,
    article: dict[str, Any],
    *,
    accent: str = "US",
    toeic: bool = True,
    japanese: bool = False,
) -> None:
    aid = article["id"]
    vocabulary: list[dict[str, Any]] = list(article.get("vocabulary") or [])
    paragraphs = article.get("paragraphs") or []

    with st.expander("📚 單字管理（納入／不納入 · 按需產生語音與例句）", expanded=False):
        st.caption(
            "「納入」→ 黃標＋單字表＋可產生語音例句；"
            "「不納入」→ 移除黃標與單字表；"
            "「恢復自動」→ 依系統 800+ 規則。"
        )

        active = filter_active_vocabulary(vocabulary, toeic=toeic)
        c1, c2, c3 = st.columns(3)
        c1.metric("文章單字", len(vocabulary))
        c2.metric("已納入學習", len(active))
        c3.metric("不納入", sum(1 for v in vocabulary if normalize_study_status(v.get("study_status")) == STUDY_EXCLUDED))

        if not vocabulary:
            st.info("此篇尚無單字條目。")
        else:
            for v in vocabulary:
                _render_vocab_row(
                    db,
                    v,
                    article_id=aid,
                    accent=accent,
                    toeic=toeic,
                    japanese=japanese,
                )

        if toeic:
            _render_add_word_section(db, aid, vocabulary, paragraphs)


def _render_vocab_row(
    db: ToeicDatabase,
    v: dict[str, Any],
    *,
    article_id: int,
    accent: str,
    toeic: bool,
    japanese: bool,
) -> None:
    vid = v.get("id")
    if not vid:
        st.warning(f"「{v.get('word', '?')}」缺少 id，請重新抓取文章或更新 App。")
        return
    word = v["word"]
    status = normalize_study_status(v.get("study_status"))
    active = vocab_is_active(v, toeic=toeic)
    auto_hint = ""
    if toeic and status == STUDY_AUTO:
        auto_hint = "（800+）" if is_toeic800_word(word) else "（未達 800+）"

    with st.container(border=True):
        h1, h2 = st.columns([3, 2])
        with h1:
            st.markdown(f"**{word}** {auto_hint} · {_status_badge(status)}")
            if v.get("meaning_zh"):
                st.caption(f"{v.get('pos') or ''} · {v['meaning_zh']}")
        with h2:
            b1, b2, b3 = st.columns(3)
            if b1.button("納入", key=f"vin_{vid}", type="primary" if status != STUDY_INCLUDED else "secondary"):
                _set_study_status(db, vid, STUDY_INCLUDED)
                _invalidate_db_cache()
                st.toast(f"已納入：{word}")
                st.rerun()
            if b2.button("不納入", key=f"vex_{vid}"):
                _set_study_status(db, vid, STUDY_EXCLUDED)
                _invalidate_db_cache()
                st.toast(f"已不納入：{word}")
                st.rerun()
            if b3.button("恢復自動", key=f"vauto_{vid}"):
                _set_study_status(db, vid, STUDY_AUTO)
                _invalidate_db_cache()
                st.toast(f"已恢復自動：{word}")
                st.rerun()

        if not active:
            st.caption("此詞目前不在黃標與單字表中。")
            return

        m1, m2 = st.columns(2)
        with m1:
            if st.button(f"🔊 產生語音", key=f"vtts_{vid}"):
                with st.spinner("語音合成中…"):
                    if japanese:
                        path = ensure_ja_pronunciation(word)
                    else:
                        path = ensure_pronunciation(word, accent=accent)
                if path and Path(path).exists():
                    _update_vocab(db, vid, audio_path=path)
                    _invalidate_db_cache()
                    st.toast("語音已儲存")
                    st.rerun()
                else:
                    st.warning("無法產生語音")
        with m2:
            if st.button("📖 查 Cambridge", key=f"vcam_{vid}", disabled=japanese):
                with st.spinner("查詢 Cambridge Dictionary…"):
                    info = lookup_word(word)
                if info:
                    _update_vocab(db, vid, **_dict_fields(info))
                    _invalidate_db_cache()
                    st.toast("已更新釋義與例句")
                    st.rerun()
                else:
                    st.warning("Cambridge 查無此詞，請稍後再試")

        if v.get("example_en"):
            st.markdown(f"**例句：** {v['example_en']}")
            if v.get("example_zh"):
                st.caption(v["example_zh"])
            render_dict_attribution(v)
            if st.button("🔊 例句朗讀", key=f"vextts_{vid}"):
                lang = "ja" if japanese else "en"
                with st.spinner("例句語音…"):
                    ex_path = ensure_tts(v["example_en"], lang=lang, accent=accent if toeic else "US")
                if ex_path and Path(ex_path).exists():
                    st.audio(ex_path)
                else:
                    st.warning("無法產生例句語音")

        audio = v.get("audio_path")
        if audio and Path(str(audio)).exists():
            st.caption(f"單字發音 · {ACCENT_LABELS.get(accent, accent) if toeic else '日語'}")
            st.audio(audio)


def _render_add_word_section(
    db: ToeicDatabase,
    article_id: int,
    vocabulary: list[dict[str, Any]],
    paragraphs: list[dict[str, Any]],
) -> None:
    st.markdown("---")
    st.markdown("**從文章加入單字**（手動納入，可產生語音與例句）")
    existing = {v["word"].lower() for v in vocabulary}
    candidates = [w for w in scan_article_word_candidates(paragraphs) if w not in existing]

    custom = st.text_input("或輸入英文單字", key=f"add_word_{article_id}", placeholder="例如 volatility")
    pick = st.selectbox(
        "文章常見詞",
        ["—"] + candidates[:30],
        key=f"pick_word_{article_id}",
    )
    word = custom.strip().lower() or (pick if pick != "—" else "")
    if not word:
        return
    if db.article_has_vocab_word(article_id, word):
        st.caption(f"「{word}」已在本文單字列表中，請至上方調整納入狀態。")
        return
    if st.button("➕ 加入並納入", key=f"add_btn_{article_id}"):
        with st.spinner("查詢字典…"):
            info = lookup_word(word) or apply_glossary(word, {"word": word, "meaning_en": word, "meaning_zh": ""})
            if not info.get("meaning_zh") and info.get("meaning_en"):
                info["meaning_zh"] = translate_text(info["meaning_en"])
        adder = getattr(db, "add_vocab_entry", None)
        if callable(adder):
            adder(
                article_id,
                {
                    "word": word,
                    "study_status": STUDY_INCLUDED,
                    **_dict_fields(info),
                },
            )
        else:
            _fresh_db().add_vocab_entry(
                article_id,
                {
                    "word": word,
                    "study_status": STUDY_INCLUDED,
                    **_dict_fields(info),
                },
            )
        _invalidate_db_cache()
        st.success(f"已加入：{word}")
        st.rerun()
