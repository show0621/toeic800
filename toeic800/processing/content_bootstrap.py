"""首次啟動時抓取新聞並寫入 DB；之後一律從 DB 載入。"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from toeic800 import config
from toeic800.db.database import ToeicDatabase
from toeic800.processing.japanese_pipeline import run_japanese_weekly_fetch
from toeic800.processing.pipeline import run_weekly_fetch

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BootstrapResult:
    skipped: bool
    reason: str
    toeic_added: int = 0
    japanese_added: int = 0


def needs_bootstrap(db: ToeicDatabase) -> bool:
    """DB 內某模組尚無任何文章，且允許自動 bootstrap。"""
    if not config.AUTO_BOOTSTRAP_NEWS:
        return False
    toeic = db.stats(track="toeic")["articles"]
    japanese = db.stats(track="japanese")["articles"]
    return toeic == 0 or japanese == 0


def bootstrap_news_if_needed(db: ToeicDatabase) -> BootstrapResult:
    """僅在該模組 DB 為空時抓取一次；已有資料則直接跳過。"""
    if not config.AUTO_BOOTSTRAP_NEWS:
        return BootstrapResult(skipped=True, reason="disabled")

    toeic_count = db.stats(track="toeic")["articles"]
    ja_count = db.stats(track="japanese")["articles"]

    if toeic_count > 0 and ja_count > 0:
        return BootstrapResult(skipped=True, reason="db_ready")

    toeic_added = 0
    ja_added = 0

    if toeic_count == 0:
        logger.info("多益模組 DB 為空，執行首次抓取…")
        toeic_added = len(run_weekly_fetch(db, force=False))

    if ja_count == 0:
        logger.info("日文模組 DB 為空，執行首次抓取…")
        ja_added = len(run_japanese_weekly_fetch(db))

    return BootstrapResult(
        skipped=False,
        reason="fetched",
        toeic_added=toeic_added,
        japanese_added=ja_added,
    )
