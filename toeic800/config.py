"""多益800分專案 — 設定。"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
AUDIO_DIR = DATA_DIR / "audio"
DB_PATH = Path(os.getenv("TOEIC800_DB", str(DATA_DIR / "toeic800.db")))

DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# 每週抓取篇數（各來源加總上限）
WEEKLY_ARTICLE_LIMIT = int(os.getenv("WEEKLY_ARTICLE_LIMIT", "6"))
VOCAB_PER_ARTICLE = int(os.getenv("VOCAB_PER_ARTICLE", "15"))

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
