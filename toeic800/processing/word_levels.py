"""多益700+ / 托福雅思級單字篩選（排除太簡單的詞）。"""
from __future__ import annotations

import re
from typing import Any

# 多益800 / 托福雅思常見進階詞
ADVANCED_SEED = {
    "slump", "mounting", "sustainable", "sell-off", "investor", "inflation",
    "borrowing", "likelihood", "overvalued", "utilities", "staples", "vulnerable",
    "sentiment", "emphasis", "acquiring", "stake", "executive", "debut",
    "recession", "tariff", "sanction", "forecast", "surge", "plunge", "rally",
    "volatility", "portfolio", "dividend", "earnings", "merger", "acquisition",
    "commodity", "sovereign", "fiscal", "monetary", "stimulus", "deficit",
    "unemployment", "payroll", "benchmark", "equity", "yield", "hedge",
    "derivative", "liquidity", "capital", "revenue", "speculation", "consolidate",
    "depreciation", "appreciation", "amortization", "leverage", "underwriting",
    "collateral", "bankruptcy", "insolvency", "austerity", "protectionism",
    "globalization", "diversification", "remittance", "subsidy", "embargo",
    "geopolitical", "unprecedented", "substantial", "significant", "exacerbate",
    "mitigate", "fluctuation", "instability", "intervention", "quantitative",
    "hawkish", "dovish", "stagflation", "hyperinflation", "cryptocurrency",
    "blockchain", "regulatory", "compliance", "transparency", "accountability",
    "shareholder", "bondholder", "creditor", "debtor", "solvent", "insolvent",
    "overhaul", "restructure", "privatize", "nationalize", "bailout", "default",
    "downgrade", "upgrade", "outperform", "underperform", "overhead", "turnover",
    "milestone", "breakthrough", "setback", "headwind", "tailwind", "macroeconomic",
    "microeconomic", "procurement", "inventory", "logistics", "infrastructure",
    "legislation", "bureaucracy", "diplomatic", "multilateral", "bilateral",
    "unilateral", "contentious", "controversial", "unanimous", "consensus",
    "advocate", "opponent", "proponent", "skeptic", "optimistic", "pessimistic",
    "cautious", "robust", "sluggish", "stagnant", "burgeoning", "diminish",
    "escalate", "alleviate", "aggravate", "jeopardize", "undermine", "bolster",
    "scrutinize", "articulate", "compelling", "untenable", "plausible",
    "formidable", "unprecedented", "notwithstanding", "albeit", "henceforth",
}

# 多益700以下 / 日常常見詞 — 不做黃標
COMMON_BASIC = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "as", "is", "was", "are", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "must", "can", "this", "that", "these", "those", "it", "its",
    "they", "them", "their", "we", "our", "you", "your", "he", "she", "his", "her",
    "who", "which", "what", "when", "where", "why", "how", "not", "no", "yes",
    "all", "each", "every", "both", "few", "more", "most", "other", "some", "such",
    "than", "too", "very", "just", "also", "into", "over", "after", "before",
    "between", "through", "during", "without", "within", "about", "said", "says",
    "one", "two", "new", "year", "week", "day", "time", "people", "us", "get",
    "got", "make", "made", "go", "goes", "going", "come", "take", "see", "know",
    "think", "want", "use", "find", "give", "tell", "work", "seem", "feel", "try",
    "leave", "call", "keep", "let", "begin", "show", "hear", "play", "run", "move",
    "live", "believe", "hold", "bring", "happen", "write", "provide", "sit", "stand",
    "lose", "pay", "meet", "include", "continue", "set", "learn", "change", "lead",
    "read", "allow", "add", "spend", "grow", "open", "walk", "win", "offer",
    "remember", "love", "consider", "appear", "buy", "wait", "serve", "send",
    "expect", "build", "stay", "fall", "cut", "reach", "pass", "sell", "require",
    "report", "decide", "pull", "market", "stock", "stocks", "company", "business",
    "news", "world", "country", "state", "city", "government", "president", "group",
    "number", "part", "place", "case", "fact", "point", "much", "many", "large",
    "small", "big", "old", "good", "bad", "great", "high", "low", "long", "short",
    "first", "last", "next", "early", "late", "public", "national", "local",
    "economic", "political", "social", "financial", "money", "bank", "banks", "rate",
    "rates", "price", "prices", "trade", "job", "jobs", "work", "working", "firm",
    "firms", "deal", "deals", "plan", "plans", "help", "need", "needs", "look",
    "looks", "looking", "back", "down", "up", "out", "off", "still", "even", "only",
    "well", "way", "ways", "right", "left", "own", "same", "different", "another",
    "today", "yesterday", "tomorrow", "now", "then", "here", "there", "while",
    "since", "because", "although", "however", "million", "billion", "percent",
    "index", "share", "shares", "fund", "funds", "cost", "costs", "tax", "taxes",
    "oil", "gas", "food", "house", "home", "homes", "car", "cars", "tech", "data",
    "online", "digital", "global", "foreign", "domestic", "major", "minor", "key",
    "top", "chief", "head", "team", "official", "officials", "leader", "leaders",
    "war", "peace", "law", "laws", "rule", "rules", "power", "energy", "water",
    "area", "areas", "line", "lines", "end", "start", "close", "closed", "open",
    "rise", "rose", "rising", "drop", "dropped", "gain", "gains", "loss", "losses",
    "hit", "hits", "amid", "among", "across", "against", "under", "above", "below",
    "near", "far", "around", "along", "despite", "according", "recent", "latest",
    "current", "former", "future", "past", "possible", "likely", "unlikely",
    "American", "Chinese", "European", "Asian", "British", "Japanese", "Korean",
    "Trump", "Fed", "Wall", "Street", "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday", "January", "February", "March", "April",
    "June", "July", "August", "September", "October", "November", "December",
}

_ADVANCED_SUFFIXES = ("tion", "sion", "ment", "ance", "ence", "ious", "eous", "ize", "ify", "ism")


def normalize_word(word: str) -> str:
    return word.lower().strip("'-").replace("'", "")


def is_advanced_word(word: str) -> bool:
    """是否為多益700+ / 托福雅思級生字（非基礎詞）。"""
    w = normalize_word(word)
    if not w or len(w) < 5:
        return False
    if w in COMMON_BASIC:
        return False
    if w in ADVANCED_SEED:
        return True
    if len(w) >= 9:
        return True
    if len(w) >= 7 and w not in COMMON_BASIC:
        # 7+ 字母且非基礎詞，多半是進階詞
        if any(w.endswith(s) for s in _ADVANCED_SUFFIXES):
            return True
        if "-" in w:
            return True
        # 長詞預設進階
        return len(w) >= 8
    if len(w) >= 6 and any(w.endswith(s) for s in _ADVANCED_SUFFIXES):
        return True
    return False


def score_word(word: str, freq: int = 1) -> float:
    w = normalize_word(word)
    score = freq * 1.0
    if w in ADVANCED_SEED:
        score += 8
    if is_advanced_word(w):
        score += 4
    if len(w) >= 8:
        score += 2
    if "-" in w:
        score += 1
    if w in COMMON_BASIC:
        score -= 10
    return score


def filter_advanced_vocabulary(
    vocabulary: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [v for v in vocabulary if is_advanced_word(v.get("word", ""))]


def filter_advanced_vocab_map(
    vocab_map: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {k: v for k, v in vocab_map.items() if is_advanced_word(k)}
