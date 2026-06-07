"""多益 800+ 每日擬真練習出題 — 委派 RAG 引擎。"""
from __future__ import annotations

from datetime import date
from typing import Any

from toeic800.db.database import ToeicDatabase
from toeic800.processing.toeic_rag_generator import (
    DAILY_COUNT,
    READING_SPLIT,
    build_daily_set,
    build_daily_grammar,
    build_daily_listening,
    build_daily_reading,
    build_daily_vocab,
    corpus_stats,
)

__all__ = [
    "DAILY_COUNT",
    "READING_SPLIT",
    "build_daily_set",
    "build_daily_vocab",
    "build_daily_grammar",
    "build_daily_listening",
    "build_daily_reading",
    "corpus_stats",
]
