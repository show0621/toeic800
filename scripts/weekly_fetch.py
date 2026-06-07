"""每週一抓取：多益 + 日文 N5–N1。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from toeic800.processing.japanese_pipeline import run_japanese_weekly_fetch
from toeic800.processing.pipeline import run_weekly_fetch

if __name__ == "__main__":
    toeic = run_weekly_fetch()
    japanese = run_japanese_weekly_fetch()
    print(f"weekly: toeic={len(toeic)} japanese={japanese}")
