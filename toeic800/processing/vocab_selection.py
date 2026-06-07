"""單字學習範圍：納入／不納入／自動（依多益 800+ 規則）。"""
from __future__ import annotations

from typing import Any

from toeic800.processing.word_levels import is_toeic800_word

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
