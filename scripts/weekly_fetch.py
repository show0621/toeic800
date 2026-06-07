"""Windows 工作排程器：每週一 08:00 抓取。

PowerShell 建立排程（以系統管理員執行一次）：
  schtasks /Create /TN "Toeic800Weekly" /TR "powershell -File scripts\\weekly_task.ps1" /SC WEEKLY /D MON /ST 08:00
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from toeic800.processing.pipeline import run_weekly_fetch

if __name__ == "__main__":
    ids = run_weekly_fetch()
    print(f"weekly fetch done: {len(ids)} articles")
