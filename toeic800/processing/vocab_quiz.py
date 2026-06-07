"""單字複習：中文答案比對。"""
from __future__ import annotations

import re

from toeic800.utils.zh_tw import ensure_zh_tw

_SPLIT_RE = re.compile(r"[；;，,、／/|·（）()\[\]【】\s]+")


def _tokens(text: str) -> set[str]:
    text = ensure_zh_tw(text.strip())
    parts = _SPLIT_RE.split(text)
    return {p.strip() for p in parts if len(p.strip()) >= 2}


def check_zh_answer(user: str, expected: str) -> tuple[bool, str]:
    """比對使用者輸入的中文意思。允許同義片段、部分匹配。"""
    user = ensure_zh_tw((user or "").strip())
    expected = ensure_zh_tw((expected or "").strip())

    if not user:
        return False, "請輸入中文意思後再確認。"

    if not expected or expected in ("—", "-"):
        return True, "此詞尚無標準中文，請對照下方完整釋義。"

    if user == expected:
        return True, "✓ 完全正確！"

    user_compact = re.sub(r"\s+", "", user)
    exp_compact = re.sub(r"\s+", "", expected)
    if user_compact in exp_compact or exp_compact in user_compact:
        return True, "✓ 正確！"

    user_t = _tokens(user)
    exp_t = _tokens(expected)
    overlap = user_t & exp_t
    if overlap:
        hint = "、".join(sorted(overlap, key=len, reverse=True)[:3])
        return True, f"✓ 正確！（符合：{hint}）"

    for et in exp_t:
        if len(et) >= 2 and et in user:
            return True, f"✓ 正確！（含「{et}」）"
        for ut in user_t:
            if len(ut) >= 2 and (ut in et or et in ut):
                return True, "✓ 正確！"

    return False, f"✗ 尚未答對。參考答案：{expected}"


def check_ja_answer(user: str, expected_zh: str, expected_reading: str = "") -> tuple[bool, str]:
    """日文模式：可輸入中文或讀音。"""
    ok, msg = check_zh_answer(user, expected_zh)
    if ok:
        return ok, msg
    if expected_reading:
        u = user.strip()
        if u and (u in expected_reading or expected_reading in u):
            return True, "✓ 正確！"
    return False, msg
