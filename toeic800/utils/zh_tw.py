"""強制繁體中文（簡體自動轉換）。"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_converter = None


def _get_converter():
    global _converter
    if _converter is not None:
        return _converter
    try:
        import opencc

        _converter = opencc.OpenCC("s2twp")
        return _converter
    except Exception:
        pass
    try:
        import zhconv

        _converter = lambda t: zhconv.convert(t, "zh-tw")  # type: ignore[assignment]
        return _converter
    except Exception as exc:
        logger.debug("zhconv 不可用: %s", exc)
        _converter = False
        return _converter


def ensure_zh_tw(text: str | None) -> str:
    """將中文統一為繁體；已是繁體則保持。"""
    if not text:
        return ""
    s = str(text).strip()
    if not s:
        return ""
    conv = _get_converter()
    if conv is False:
        return s
    try:
        return conv.convert(s) if hasattr(conv, "convert") else conv(s)
    except Exception as exc:
        logger.debug("繁體轉換失敗: %s", exc)
        return s


def normalize_article_zh(article: dict) -> dict:
    """讀取／顯示前將所有中文字段轉為繁體。"""
    import json

    for key in ("title_zh", "summary_zh"):
        if article.get(key):
            article[key] = ensure_zh_tw(article[key])
    for para in article.get("paragraphs") or []:
        if para.get("text_zh"):
            para["text_zh"] = ensure_zh_tw(para["text_zh"])
    for v in article.get("vocabulary") or []:
        for key in ("meaning_zh", "example_zh"):
            if v.get(key):
                v[key] = ensure_zh_tw(v[key])
    for sub in article.get("subtitles") or []:
        if sub.get("text_zh"):
            sub["text_zh"] = ensure_zh_tw(sub["text_zh"])
    for g in article.get("grammar") or []:
        for key in ("meaning_zh", "example_zh"):
            if g.get(key):
                g[key] = ensure_zh_tw(g[key])
    for q in article.get("quiz") or []:
        if q.get("question"):
            q["question"] = ensure_zh_tw(q["question"])
        if q.get("answer"):
            q["answer"] = ensure_zh_tw(q["answer"])
        if q.get("options_json"):
            try:
                opts = json.loads(q["options_json"])
                q["options_json"] = json.dumps(
                    [ensure_zh_tw(o) for o in opts], ensure_ascii=False
                )
            except json.JSONDecodeError:
                pass
    return article


def normalize_vocab_row(row: dict) -> dict:
    for key in ("meaning_zh", "example_zh"):
        if row.get(key):
            row[key] = ensure_zh_tw(row[key])
    return row
