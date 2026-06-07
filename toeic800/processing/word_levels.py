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
    "significant", "specification", "procurement", "remittance", "sovereign",
    "quantitative", "amortization", "underwriting", "privatization", "nationalization",
    "contentious", "burgeoning", "stagnation", "depreciation", "appreciation",
    "counterpart", "contingency", "delinquent", "disclosure", "expenditure",
    "formulation", "indemnity", "litigation", "malpractice", "negotiation",
    "obligation", "preliminary", "profitable", "redemption", "refinance",
    "reimburse", "relocation", "repatriate", "revocation", "shortfall",
    "streamline", "subordinate", "supplement", "surcharge", "throughput",
    "trajectory", "underwrite", "withdrawal", "withholding", "workforce",
}

# 新聞常見但多益800以下 — 不列入單字表／黃標
INTERMEDIATE_NEWS = {
    "official", "officials", "government", "president", "minister", "election",
    "campaign", "security", "military", "industry", "industries", "company",
    "companies", "business", "consumer", "consumers", "market", "markets",
    "service", "services", "product", "products", "customer", "customers",
    "employee", "employees", "technology", "technologies", "program", "programme",
    "project", "projects", "system", "systems", "policy", "policies", "agency",
    "agencies", "sector", "sectors", "region", "regions", "regional", "national",
    "international", "economic", "financial", "political", "social", "digital",
    "online", "global", "foreign", "domestic", "annual", "monthly", "quarterly",
    "growth", "decline", "increase", "decrease", "strong", "weak", "record",
    "impact", "issue", "issues", "report", "reports", "reported", "according",
    "however", "therefore", "meanwhile", "overall", "recent", "latest", "current",
    "former", "future", "possible", "likely", "unlikely", "million", "billion",
    "percent", "century", "history", "historical", "community", "communities",
    "population", "education", "university", "hospital", "weather", "climate",
    "environment", "environmental", "health", "medical", "family", "children",
    "woman", "women", "people", "person", "public", "private", "local", "major",
    "minor", "chief", "leader", "leaders", "team", "group", "party", "parties",
    "support", "supported", "opposition", "debate", "discussion", "statement",
    "announce", "announced", "announcement", "decision", "decisions", "change",
    "changes", "changed", "develop", "development", "research", "scientists",
    "production", "manufacturing", "construction", "operation", "operations",
    "management", "manager", "managers", "director", "directors", "department",
    "organization", "organisation", "association", "committee", "conference",
    "agreement", "contract", "contracts", "partnership", "relationship",
    "situation", "condition", "conditions", "problem", "problems", "solution",
    "response", "action", "actions", "activity", "activities", "process",
    "information", "communication", "transport", "transportation", "energy",
    "power", "water", "food", "price", "prices", "cost", "costs", "money",
    "bank", "banks", "trade", "export", "imports", "import", "exports",
    "investment", "investments", "investing", "invest", "invested",
    "optimistic", "pessimistic", "cautious", "important",
    # 職場／教育／商業常見詞（多益 700 以下，不黃標）
    "training", "trained", "train", "trainer", "trainers", "trainee",
    "employment", "employ", "employed", "employer", "employers", "employee",
    "employees", "workplace", "worker", "workers", "working",
    "businesses", "business", "corporate", "corporation", "corporations",
    "education", "educational", "educator", "educators", "school", "schools",
    "student", "students", "teacher", "teachers", "college", "university",
    "graduate", "graduates", "graduation", "undergraduate", "course", "courses",
    "classroom", "learning", "learner", "learners", "skill", "skills",
    "career", "careers", "hiring", "hire", "hired", "layoff", "layoffs",
    "full-time", "fulltime", "part-time", "parttime", "part", "time",
    "professional", "professionals", "experience", "experienced", "intern",
    "internship", "internships", "apprentice", "vocational", "certificate",
    "certification", "requirement", "requirements", "application", "applications",
    "benefit", "benefits", "salary", "salaries", "wage", "wages", "bonus",
    "promotion", "promotions", "position", "positions", "job", "jobs",
    "office", "offices", "staff", "staffing", "recruit", "recruitment",
    "recruiting", "resume", "interview", "interviews", "candidate", "candidates",
    "announce", "announced", "announcement", "announcements",
    "launch", "launched", "release", "released", "introduce", "introduced",
    "offer", "offered", "offering", "provide", "provided", "providing",
    "supply", "supplier", "suppliers", "demand", "customer", "client", "clients",
    "marketing", "sales", "selling", "retail", "commercial", "industrial",
    "competition", "competitor", "competitors", "competitive", "marketplace",
    "startup", "startups", "funding", "funded", "finance", "financing",
    "loan", "loans", "credit", "debts", "debt", "interest", "insurance",
    "profit", "profits", "loss", "losses", "resource", "resources",
    "strategy", "strategies", "strategic", "planning", "planned", "plan",
    "expansion", "expanding", "expanded", "growth", "growing",
    "technology", "technical", "technological", "software", "hardware",
    "network", "networks", "internet", "website", "platform", "platforms",
    "security", "secure", "safety", "risk", "risks", "crisis", "crises",
    "reform", "reforms", "reformed", "reformers", "reforming",
    "reformist", "reforming", "standard", "standards", "quality",
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
    "near", "far", "around", "along",     "despite", "according", "recent", "latest",
    "current", "former", "future", "past", "possible", "likely", "unlikely",
    "however", "therefore", "meanwhile", "overall", "annual", "monthly",
    "quarter", "quarterly", "growth", "decline", "increase", "decrease",
    "strong", "weak", "higher", "lower", "record", "impact", "issue", "issues",
    "market", "stock", "stocks", "company", "business", "news", "world",
    "country", "state", "city", "government", "president", "group", "number",
    "part", "place", "case", "fact", "point", "much", "many", "large", "small",
    "include", "including", "follow", "following", "support", "supported",
    "continue", "continued", "remain", "remains", "return", "returns", "create",
    "created", "develop", "developed", "developing", "produce", "produced",
    "reduce", "reduced", "raise", "raised", "lower", "lowest", "highest",
    "global", "local", "national", "international", "regional", "central",
    "major", "minor", "chief", "main", "primary", "secondary", "general",
    "specific", "special", "common", "popular", "public", "private",
    "American", "Chinese", "European", "Asian", "British", "Japanese", "Korean",
    "Trump", "Fed", "Wall", "Street", "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday", "January", "February", "March", "April",
    "June", "July", "August", "September", "October", "November", "December",
}

# 僅用於未知長詞的進階字尾（不含 -ment / -ance，避免 employment 等誤判）
_ADVANCED_SUFFIXES = ("tion", "sion", "ious", "eous", "ivity", "ancy", "ency", "ness", "ism")


def normalize_word(word: str) -> str:
    return word.lower().strip("'-").replace("'", "")


def _is_excluded_common(w: str) -> bool:
    """常見詞及其複數／時態／分詞變化一律排除。"""
    if w in COMMON_BASIC or w in INTERMEDIATE_NEWS:
        return True
    if w.endswith("ies") and len(w) > 4:
        if f"{w[:-3]}y" in INTERMEDIATE_NEWS or f"{w[:-3]}y" in COMMON_BASIC:
            return True
    if w.endswith("es") and len(w) > 4:
        stem = w[:-2]
        if stem in INTERMEDIATE_NEWS or stem in COMMON_BASIC:
            return True
        if w[:-1] in INTERMEDIATE_NEWS or w[:-1] in COMMON_BASIC:
            return True
    if w.endswith("s") and len(w) > 3:
        if w[:-1] in INTERMEDIATE_NEWS or w[:-1] in COMMON_BASIC:
            return True
    if w.endswith("ed") and len(w) > 4:
        if w[:-2] in INTERMEDIATE_NEWS or w[:-2] in COMMON_BASIC:
            return True
        if w[:-1] in INTERMEDIATE_NEWS or w[:-1] in COMMON_BASIC:
            return True
    if w.endswith("ing") and len(w) > 5:
        stem = w[:-3]
        if stem in INTERMEDIATE_NEWS or stem in COMMON_BASIC:
            return True
        if f"{stem}e" in INTERMEDIATE_NEWS or f"{stem}e" in COMMON_BASIC:
            return True
    return False


def is_toeic800_word(word: str) -> bool:
    """多益 800–900 較難單字（白名單優先；常見詞一律不標）。"""
    w = normalize_word(word)
    if not w or len(w) < 8:
        return False
    if _is_excluded_common(w):
        return False
    if w in ADVANCED_SEED:
        return True
    if len(w) >= 13:
        return True
    if len(w) >= 11 and any(w.endswith(s) for s in _ADVANCED_SUFFIXES):
        return True
    if "-" in w and len(w) >= 12 and w in ADVANCED_SEED:
        return True
    return False


def is_advanced_word(word: str) -> bool:
    """相容舊名稱；多益模組請用 is_toeic800_word。"""
    return is_toeic800_word(word)


def score_word(word: str, freq: int = 1) -> float:
    w = normalize_word(word)
    if not is_toeic800_word(w):
        return -1.0
    score = freq * 1.0
    if w in ADVANCED_SEED:
        score += 10
    if len(w) >= 10:
        score += 3
    if len(w) >= 12:
        score += 2
    if "-" in w:
        score += 2
    if any(w.endswith(s) for s in _ADVANCED_SUFFIXES):
        score += 2
    return score


def filter_toeic800_vocabulary(
    vocabulary: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [v for v in vocabulary if is_toeic800_word(v.get("word", ""))]


def filter_advanced_vocabulary(
    vocabulary: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return filter_toeic800_vocabulary(vocabulary)


def filter_advanced_vocab_map(
    vocab_map: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {k: v for k, v in vocab_map.items() if is_toeic800_word(k)}
