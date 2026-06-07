"""多益練習題：詳細解析與題型標籤。"""
from __future__ import annotations

import json
from typing import Any

PART_LABELS: dict[str, str] = {
    "vocab": "Part 5 · 單字／詞性",
    "grammar": "Part 5/6 · 文法結構",
    "phrase": "Part 5 · 片語／搭配詞",
    "listening": "Part 3/4 · 聽力理解",
    "reading_single": "Part 7 · 單篇閱讀",
    "reading_double": "Part 7 · 雙篇閱讀",
    "reading_triple": "Part 7 · 三篇閱讀",
}


def enrich_question(q: dict[str, Any], skill: str) -> dict[str, Any]:
    """補齊題型標籤與詳細解析欄位。"""
    item = dict(q)
    if skill == "reading":
        fmt = item.get("format", "single")
        item["part_label"] = PART_LABELS.get(f"reading_{fmt}", PART_LABELS["reading_single"])
    else:
        item["part_label"] = PART_LABELS.get(skill, skill)

    item["detail_zh"] = build_detail_zh(item, skill)
    item["detail_en"] = build_detail_en(item, skill)
    return item


def _options(q: dict[str, Any]) -> list[str]:
    if isinstance(q.get("options"), list):
        return q["options"]
    raw = q.get("options_json")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    return []


def build_detail_zh(q: dict[str, Any], skill: str) -> str:
    ans = q.get("answer", "")
    lines = [f"**正解：** {ans}"]

    if q.get("explanation_zh"):
        lines.append(f"**考點：** {q['explanation_zh']}")

    opts = _options(q)
    wrong = [o for o in opts if o != ans]
    if wrong:
        lines.append("**錯誤選項分析：**")
        for w in wrong:
            note = _wrong_option_note(w, ans, skill, q)
            lines.append(f"- {w} → {note}")

    if skill == "listening" and q.get("audio_text"):
        lines.append(f"**聽力原文：** {q['audio_text']}")

    if skill == "reading" and q.get("passages"):
        cites = []
        for p in q["passages"]:
            label = p.get("label", "Passage")
            snippet = (p.get("text") or "")[:120].strip()
            if snippet:
                cites.append(f"・{label}：「{snippet}…」")
        if cites:
            lines.append("**文章依據：**")
            lines.extend(cites)

    if q.get("source_note"):
        lines.append(f"**內容來源：** {q['source_note']}")
    elif q.get("content_source"):
        lines.append(f"**內容來源：** {q['content_source']}")

    return "\n\n".join(lines)


def build_detail_en(q: dict[str, Any], skill: str) -> str:
    ans = q.get("answer", "")
    if q.get("explanation_en"):
        return q["explanation_en"]

    if skill == "vocab":
        return (
            f"The correct choice is '{ans}'. In TOEIC Part 5, you must select the word "
            f"form that fits both grammar (tense, part of speech) and business collocation."
        )
    if skill == "grammar":
        return (
            f"'{ans}' is correct because it satisfies the grammatical structure and "
            f"standard business English usage required in Part 5/6."
        )
    if skill == "listening":
        return (
            f"The answer '{ans}' follows directly from the speakers' intent and the "
            f"details stated in the conversation (Part 3/4 inference or detail question)."
        )
    if skill == "reading":
        return (
            f"'{ans}' is supported by explicit or inferential evidence across the "
            f"passage(s), consistent with Part 7 reading comprehension at the 800+ level."
        )
    return f"Correct answer: {ans}"


def _wrong_option_note(wrong: str, correct: str, skill: str, q: dict[str, Any]) -> str:
    if skill == "vocab":
        if wrong.endswith(("tion", "ment", "ness", "ity")) and not correct.endswith(
            ("tion", "ment", "ness", "ity")
        ):
            return "名詞形式，句中需要動詞／形容詞／副詞"
        if wrong.endswith("ly") and not correct.endswith("ly"):
            return "副詞形式，句中詞性不符"
        if wrong.endswith(("ed", "ing")) and correct != wrong:
            return "動詞時態或分詞形式不符"
        return "詞性、時態或商業搭配不符"
    if skill == "grammar":
        return "文法結構或固定搭配錯誤"
    if skill == "listening":
        return "與對話內容或說話者意圖不符"
    if skill == "reading":
        return "文章未支持此說法，或過度推論"
    return "不符合題意"
