"""
多益800分 + 日文 JLPT 專案 CLI。

用法：
  python main.py fetch-weekly              # 每週 BBC/CNN
  python main.py fetch-weekly-japanese     # 每週 N5–N1 各 1 篇
  python main.py fetch-weekly-all          # 全部
  python main.py import-url --url ...
  python main.py import-japanese --url ... --level N5
  python main.py serve
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
    print(f"多益新增 {len(ids)} 篇: {ids}")


def cmd_fetch_weekly_japanese(_: argparse.Namespace) -> None:
    from toeic800.processing.japanese_pipeline import run_japanese_weekly_fetch

    saved = run_japanese_weekly_fetch()
    print(f"日文新增: {saved}")


def cmd_fetch_weekly_all(_: argparse.Namespace) -> None:
    from toeic800.processing.japanese_pipeline import run_japanese_weekly_fetch
    from toeic800.processing.pipeline import run_weekly_fetch

    ids = run_weekly_fetch()
    saved = run_japanese_weekly_fetch()
    print(f"多益 {len(ids)} 篇 · 日文 {saved}")


def cmd_import_url(args: argparse.Namespace) -> None:
    from toeic800.processing.pipeline import process_url

    aid = process_url(args.url, source=args.source)
    print(f"article_id={aid}")


def cmd_import_japanese(args: argparse.Namespace) -> None:
    from toeic800 import config
    from toeic800.processing.japanese_pipeline import process_japanese_url

    meta = config.JLPT_SOURCES.get(args.level, {})
    aid = process_japanese_url(
        args.url,
        jlpt_level=args.level,
        source=args.source or meta.get("source", "Manual"),
        parser=meta.get("parser", "generic"),
    )
    print(f"article_id={aid}")


def cmd_serve(_: argparse.Namespace) -> None:
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py")],
        cwd=str(ROOT),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="多益800 · 日文新聞學習")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("fetch-weekly").set_defaults(func=cmd_fetch_weekly)
    sub.add_parser("fetch-weekly-japanese").set_defaults(func=cmd_fetch_weekly_japanese)
    sub.add_parser("fetch-weekly-all").set_defaults(func=cmd_fetch_weekly_all)

    p_url = sub.add_parser("import-url")
    p_url.add_argument("--url", required=True)
    p_url.add_argument("--source", default="Manual")
    p_url.set_defaults(func=cmd_import_url)

    p_ja = sub.add_parser("import-japanese")
    p_ja.add_argument("--url", required=True)
    p_ja.add_argument("--level", default="N5", choices=["N5", "N4", "N3", "N2", "N1"])
    p_ja.add_argument("--source", default="")
    p_ja.set_defaults(func=cmd_import_japanese)

    sub.add_parser("serve").set_defaults(func=cmd_serve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
