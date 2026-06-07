"""
多益800分專案 CLI。

用法：
  python main.py fetch-weekly          # 每週 BBC/CNN 抓取
  python main.py import-url --url ...  # 手動匯入單篇
  python main.py serve                 # 啟動 Streamlit
"""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("toeic800")


def cmd_fetch_weekly(_: argparse.Namespace) -> None:
    from toeic800.processing.pipeline import run_weekly_fetch

    ids = run_weekly_fetch()
    print(f"新增 {len(ids)} 篇: {ids}")


def cmd_import_url(args: argparse.Namespace) -> None:
    from toeic800.processing.pipeline import process_url

    aid = process_url(args.url, source=args.source)
    print(f"article_id={aid}")


def cmd_serve(_: argparse.Namespace) -> None:
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py")],
        cwd=str(ROOT),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="多益800分 · 經濟英文週報")
    sub = parser.add_subparsers(dest="command", required=True)

    p_week = sub.add_parser("fetch-weekly", help="每週抓取 BBC/CNN")
    p_week.set_defaults(func=cmd_fetch_weekly)

    p_url = sub.add_parser("import-url", help="匯入單篇文章")
    p_url.add_argument("--url", required=True)
    p_url.add_argument("--source", default="Manual")
    p_url.set_defaults(func=cmd_import_url)

    p_serve = sub.add_parser("serve", help="啟動 Streamlit 網站")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
