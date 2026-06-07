"""多益800分專案 — 設定。"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
AUDIO_DIR = DATA_DIR / "audio"
JA_AUDIO_DIR = DATA_DIR / "audio_ja"
DB_PATH = Path(os.getenv("TOEIC800_DB", str(DATA_DIR / "toeic800.db")))

DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
JA_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

JLPT_LEVELS = ("N5", "N4", "N3", "N2", "N1")
VOCAB_PER_JA_ARTICLE = int(os.getenv("VOCAB_PER_JA_ARTICLE", "12"))

# 來源參考：https://vocus.cc/article/6837b674fd8978000142bdb4
JLPT_SOURCES = {
    "N5": {
        "rss": "https://www.nhk.or.jp/rss/news/cat0.xml",
        "source": "NHKやさしいことばニュース",
        "parser": "nhk_easy",
        "pick": 0,
    },
    "N4": {
        "rss": "https://news.yahoo.co.jp/rss/categories/domestic.xml",
        "source": "毎日小学生新聞（Yahoo社会）",
        "parser": "generic",
        "pick": 1,
    },
    "N3": {
        "rss": "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
        "source": "Yahoo!ニュース",
        "parser": "generic",
        "pick": 0,
    },
    "N2": {
        "rss": "https://www.nhk.or.jp/rss/news/cat0.xml",
        "source": "NHKニュース",
        "parser": "generic",
        "pick": 1,
    },
    "N1": {
        "rss": "https://www.asahi.com/rss/asahi/national.rdf",
        "source": "朝日新聞",
        "parser": "generic",
        "pick": 0,
    },
}

# 每週抓取篇數（各來源加總上限）
WEEKLY_ARTICLE_LIMIT = int(os.getenv("WEEKLY_ARTICLE_LIMIT", "6"))
VOCAB_PER_ARTICLE = int(os.getenv("VOCAB_PER_ARTICLE", "15"))

# 多益 800+ 每日擬真練習
DAILY_PRACTICE_COUNT = int(os.getenv("DAILY_PRACTICE_COUNT", "20"))
DAILY_READING_SPLIT = {"single": 8, "double": 7, "triple": 5}
TOEIC_RAG_CORPUS_VERSION = "v2"

# RSS 來源
RSS_FEEDS = {
    "bbc_business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "bbc_world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "cnn_business": "http://rss.cnn.com/rss/money_latest.rss",
    "cnn_world": "http://rss.cnn.com/rss/cnn_world.rss",
}

# 經濟／股市／國際情勢關鍵字（標題或摘要命中即納入）
TOPIC_KEYWORDS = (
    "economy", "economic", "market", "stock", "trade", "inflation", "fed",
    "interest rate", "gdp", "tariff", "wall street", "nasdaq", "dow",
    "bitcoin", "crypto", "central bank", "recession", "jobs", "employment",
    "finance", "investor", "business", "global", "war", "sanction",
    "oil", "energy", "currency", "dollar", "yuan", "euro",
    "股市", "經濟", "通膨", "利率", "貿易",
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
TRANSLATOR = os.getenv("TRANSLATOR", "google")  # google | openai
