"""JLPT 文法點偵測。"""
from __future__ import annotations

import re
from typing import Any

from toeic800.processing.japanese_translator import translate_ja_to_zh

# 各級常見文法（pattern, 說明）
GRAMMAR_BY_LEVEL: dict[str, list[tuple[str, str]]] = {
    "N5": [
        (r"です", "丁寧体断定「是…」"),
        (r"ます", "丁寧体動詞結尾"),
        (r"ません", "丁寧否定"),
        (r"でした", "過去式丁寧"),
        (r"から", "因為、從"),
        (r"が\b", "主語標記"),
        (r"を\b", "受詞標記"),
        (r"に\b", "時間/方向/對象"),
        (r"と\b", "和、引用"),
        (r"も\b", "也"),
    ],
    "N4": [
        (r"ている", "進行/狀態"),
        (r"てください", "請…"),
        (r"なければならない", "必須"),
        (r"そうです", "聽說、好像"),
        (r"ように", "為了、以便"),
        (r"ば\b", "條件「若…就…」"),
        (r"たり", "又…又…"),
    ],
    "N3": [
        (r"ようにする", "設法做到"),
        (r"ことにする", "決定"),
        (r"わけではない", "並非一定"),
        (r"おそれがある", "有可能（負面）"),
        (r"に対して", "對於"),
        (r"に関して", "關於"),
    ],
    "N2": [
        (r"に伴って", "隨著"),
        (r"をめぐって", "圍繞…"),
        (r"にわたって", "遍及"),
        (r"にとどまらず", "不僅限於"),
        (r"ものの", "雖然…但是"),
        (r"からには", "既然…就"),
    ],
    "N1": [
        (r"を余儀なく", "不得不"),
        (r"に他ならない", "正是…"),
        (r"をものともせず", "不顧"),
        (r"に足る", "足以"),
        (r"を禁じ得ない", "不禁"),
        (r"ともなれば", "一旦…就"),
    ],
}


def extract_grammar(
    paragraphs: list[str], jlpt_level: str, max_items: int = 8
) -> list[dict[str, Any]]:
    text = "\n".join(paragraphs)
    patterns = GRAMMAR_BY_LEVEL.get(jlpt_level, [])
    # 也加入較低級別的複習
    idx = ["N5", "N4", "N3", "N2", "N1"].index(jlpt_level) if jlpt_level in ["N5", "N4", "N3", "N2", "N1"] else 4
    for lv in ["N5", "N4", "N3", "N2", "N1"][: idx + 1]:
        patterns = patterns + GRAMMAR_BY_LEVEL.get(lv, [])

    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for pattern, meaning in patterns:
        if len(found) >= max_items:
            break
        if pattern in seen:
            continue
        if re.search(pattern, text):
            seen.add(pattern)
            example = _find_example(pattern, paragraphs)
            found.append(
                {
                    "pattern": pattern.replace(r"\b", ""),
                    "meaning_zh": meaning,
                    "example_ja": example,
                    "example_zh": translate_ja_to_zh(example) if example else "",
                    "jlpt_level": jlpt_level,
                }
            )
    return found


def _find_example(pattern: str, paragraphs: list[str]) -> str:
    for para in paragraphs:
        if re.search(pattern, para):
            sents = re.split(r"(?<=[。！？])", para)
            for s in sents:
                if re.search(pattern, s):
                    return s.strip()[:150]
            return para.strip()[:150]
    return ""
