"""單字學習範圍：納入／不納入／自動（依多益 800+ 規則）。"""
from __future__ import annotations

import re
from typing import Any

from toeic800.processing.word_levels import is_toeic800_word

_WORD_KEY_RE = re.compile(r"[^a-z0-9\-']+")

STUDY_AUTO = "auto"
STUDY_INCLUDED = "included"
STUDY_EXCLUDED = "excluded"

STATUS_LABELS = {
    STUDY_AUTO: "自動",
    STUDY_INCLUDED: "已納入",
    STUDY_EXCLUDED: "不納入",
}


def normalize_study_status(status: str | None) -> str:
    s = (status or STUDY_AUTO).lower().strip()
    if s in (STUDY_INCLUDED, STUDY_EXCLUDED):
        return s
    return STUDY_AUTO


def vocab_is_active(v: dict[str, Any], *, toeic: bool = True) -> bool:
    """是否顯示於黃標、單字表、複習。"""
    status = normalize_study_status(v.get("study_status"))
    if status == STUDY_EXCLUDED:
        return False
    if status == STUDY_INCLUDED:
        return True
    if toeic:
        return is_toeic800_word(v.get("word", ""))
    return True


def filter_active_vocabulary(
    vocabulary: list[dict[str, Any]], *, toeic: bool = True
) -> list[dict[str, Any]]:
    return [v for v in vocabulary if vocab_is_active(v, toeic=toeic)]


def normalize_vocab_word_key(word: str) -> str:
    """英文單字比對鍵（跨文章去重用）。"""
    w = (word or "").lower().strip().strip("'\"")
    w = _WORD_KEY_RE.sub("", w)
    return w.strip("'-")


def _vocab_entry_rank(v: dict[str, Any]) -> tuple[int, int, int, int, int]:
    src = (v.get("dict_source") or "").lower()
    status = normalize_study_status(v.get("study_status"))
    ex = (v.get("example_en") or "").strip()
    return (
        1 if src == "cambridge" else 0,
        1 if ex else 0,
        1 if status == STUDY_INCLUDED else 0,
        len(v.get("meaning_en") or ""),
        int(v.get("id") or 0),
    )


def dedupe_vocabulary_by_word(
    vocabulary: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """同一單字只保留一筆（優先 Cambridge、有例句、已納入）；保留原列表順序。"""
    best: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for v in vocabulary:
        key = normalize_vocab_word_key(v.get("word") or "")
        if not key:
            continue
        if key not in best:
            order.append(key)
        prev = best.get(key)
        if prev is None or _vocab_entry_rank(v) > _vocab_entry_rank(prev):
            best[key] = v
    return [best[k] for k in order if k in best]


def group_vocabulary_by_article(
    vocabulary: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """依文章分組；跨篇重複單字只保留首次出現（依週次／排序）。"""
    seen: set[str] = set()
    buckets: dict[int, dict[str, Any]] = {}
    order: list[int] = []
    for v in vocabulary:
        key = normalize_vocab_word_key(v.get("word") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        aid = int(v.get("article_id") or 0)
        if aid not in buckets:
            buckets[aid] = {
                "article_id": aid,
                "article_title": v.get("article_title") or "",
                "week_label": v.get("week_label") or "",
                "source": v.get("source") or "",
                "items": [],
            }
            order.append(aid)
        buckets[aid]["items"].append(v)
    return [buckets[aid] for aid in order if buckets[aid]["items"]]
