"""從單字/文法產生小考題。"""
from __future__ import annotations

import json
import random
from typing import Any


def build_quiz(
    vocabulary: list[dict[str, Any]],
    grammar: list[dict[str, Any]],
    max_q: int = 8,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    pool = vocabulary[:]

    for v in pool[: max_q - 1]:
        if not v.get("meaning_zh"):
            continue
        distractors = [
            x.get("meaning_zh", "")
            for x in pool
            if x["word"] != v["word"] and x.get("meaning_zh")
        ]
        random.shuffle(distractors)
        options = [v["meaning_zh"]] + distractors[:3]
        random.shuffle(options)
        items.append(
            {
                "question": f"「{v['word']}」的意思是？",
                "options_json": json.dumps(options, ensure_ascii=False),
                "answer": v["meaning_zh"],
                "qtype": "vocab",
            }
        )

    for g in grammar[:2]:
        if not g.get("meaning_zh"):
            continue
        opts = [g["meaning_zh"], "表示過去", "表示否定", "表示疑問"]
        random.shuffle(opts)
        items.append(
            {
                "question": f"文法「{g['pattern']}」的用法？",
                "options_json": json.dumps(opts, ensure_ascii=False),
                "answer": g["meaning_zh"],
                "qtype": "grammar",
            }
        )

    return items[:max_q]
