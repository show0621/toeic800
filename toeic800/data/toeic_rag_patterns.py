"""RAG 模式展開：依 TOEIC Part 5–7 公開題型原創變形題（非新聞、非真題原文）。"""
from __future__ import annotations

import random
from typing import Any

# Part 5 模式種子 — 800+ 商務場景
_VOCAB_PATTERNS: list[dict[str, Any]] = [
    {
        "topic": "office_admin",
        "grammar_type": "word_form",
        "template": "All {noun} must be {verb} to the regional manager by noon.",
        "slots": {
            "noun": ["reports", "invoices", "proposals"],
            "verb": ["submitted", "forwarded", "delivered"],
        },
        "answer_key": "verb",
        "wrong_forms": {"submitted": ["submit", "submitting", "submission"], "forwarded": ["forward", "forwarding", "forwards"], "delivered": ["deliver", "delivering", "delivery"]},
        "explanation_zh": "被動語態 be + 過去分詞。",
    },
    {
        "topic": "hr_personnel",
        "grammar_type": "word_form",
        "template": "The {noun} committee will conduct {adj} interviews next week.",
        "slots": {"noun": ["hiring", "selection", "recruitment"], "adj": ["comprehensive", "structured", "final"]},
        "answer_key": "adj",
        "wrong_forms": {"comprehensive": ["comprehensively", "comprehend", "comprehension"], "structured": ["structure", "structurally", "structuring"], "final": ["finally", "finalize", "finalized"]},
        "explanation_zh": "形容詞修飾 interviews。",
    },
    {
        "topic": "finance_banking",
        "grammar_type": "collocation",
        "template": "The loan is contingent ___ approval from the credit committee.",
        "slots": {},
        "fixed": {"question": "The loan is contingent ___ approval from the credit committee.", "answer": "on", "options": ["on", "to", "for", "with"], "explanation_zh": "contingent on（取決於）固定搭配。"},
    },
    {
        "topic": "sales_marketing",
        "grammar_type": "word_form",
        "template": "The marketing team achieved a {adj} increase in customer retention.",
        "slots": {"adj": ["significant", "substantial", "remarkable"]},
        "answer_key": "adj",
        "wrong_forms": {"significant": ["significantly", "significance", "signify"], "substantial": ["substantially", "substance", "substantiate"], "remarkable": ["remarkably", "remark", "remarked"]},
        "explanation_zh": "形容詞修飾 increase。",
    },
    {
        "topic": "manufacturing",
        "grammar_type": "tense_aspect",
        "template": "Production {verb} suspended until the safety inspection is completed.",
        "slots": {"verb": ["has been", "will be", "was"]},
        "answer_key": "verb",
        "wrong_forms": {"has been": ["have been", "had been", "is"], "will be": ["will", "would be", "is"], "was": ["were", "is", "has"]},
        "explanation_zh": "現在完成被動 has been suspended。",
    },
    {
        "topic": "travel_hospitality",
        "grammar_type": "preposition",
        "template": "Guests are requested to check ___ of their rooms by 11 a.m.",
        "slots": {},
        "fixed": {"question": "Guests are requested to check ___ of their rooms by 11 a.m.", "answer": "out", "options": ["out", "in", "off", "over"], "explanation_zh": "check out（退房）固定片語。"},
    },
    {
        "topic": "it_tech",
        "grammar_type": "word_form",
        "template": "The software update will be {verb} deployed across all regional servers.",
        "slots": {"verb": ["gradually", "immediately", "automatically"]},
        "answer_key": "verb",
        "wrong_forms": {"gradually": ["gradual", "grade", "grading"], "immediately": ["immediate", "immense", "immensely"], "automatically": ["automatic", "automate", "automated"]},
        "explanation_zh": "副詞修飾 deployed。",
    },
    {
        "topic": "contracts_legal",
        "grammar_type": "collocation",
        "template": "Both parties agreed to abide ___ the terms outlined in Appendix B.",
        "slots": {},
        "fixed": {"question": "Both parties agreed to abide ___ the terms outlined in Appendix B.", "answer": "by", "options": ["by", "with", "to", "on"], "explanation_zh": "abide by（遵守）固定搭配。"},
    },
]

_GRAMMAR_PATTERNS: list[dict[str, Any]] = [
    {
        "topic": "office_admin",
        "grammar_type": "conditional",
        "question": "If the shipment arrives late, we ___ rescheduled the product launch.",
        "options": ["would have", "will have", "would", "had"],
        "answer": "would have",
        "explanation_zh": "與過去事實相反的第三類條件句。",
    },
    {
        "topic": "finance_banking",
        "grammar_type": "pronoun_agreement",
        "question": "Each of the branch managers ___ responsible for submitting quarterly reports.",
        "options": ["is", "are", "were", "have been"],
        "answer": "is",
        "explanation_zh": "Each of + 複數名詞，動詞用單數 is。",
    },
    {
        "topic": "hr_personnel",
        "grammar_type": "conjunction",
        "question": "The training session was postponed ___ several instructors were unavailable.",
        "options": ["because", "although", "unless", "whereas"],
        "answer": "because",
        "explanation_zh": "原因狀語從句 because。",
    },
    {
        "topic": "manufacturing",
        "grammar_type": "tense_aspect",
        "question": "By the time the inspectors arrive, the factory ___ all safety protocols.",
        "options": ["will have implemented", "will implement", "has implemented", "implemented"],
        "answer": "will have implemented",
        "explanation_zh": "By the time + 未來完成式。",
    },
    {
        "topic": "sales_marketing",
        "grammar_type": "preposition",
        "question": "The promotional campaign resulted ___ a 15 percent rise in online sales.",
        "options": ["in", "to", "from", "at"],
        "answer": "in",
        "explanation_zh": "result in（導致）固定搭配。",
    },
]

_LISTENING_PATTERNS: list[dict[str, Any]] = [
    {
        "topic": "office_admin",
        "audio_text": "W: Has the conference room been booked for Monday's client meeting? M: Yes, but we may need a larger room if all ten attendees confirm.",
        "question": "What concern does the man mention?",
        "options": ["The room size may be insufficient", "The meeting was cancelled", "The client declined to attend", "The booking fee was too high"],
        "answer": "The room size may be insufficient",
        "explanation_zh": "may need a larger room。",
    },
    {
        "topic": "hr_personnel",
        "audio_text": "M: When does the new employee orientation begin? W: It starts at nine, and HR will distribute the handbooks beforehand.",
        "question": "What will HR provide?",
        "options": ["Handbooks for new staff", "Travel reimbursement forms", "Updated salary schedules", "Parking permits"],
        "answer": "Handbooks for new staff",
        "explanation_zh": "distribute the handbooks。",
    },
    {
        "topic": "travel_hospitality",
        "audio_text": "W: Our flight has been delayed two hours due to weather. M: Then we'd better notify the hotel about our late check-in.",
        "question": "What will the speakers probably do next?",
        "options": ["Contact the hotel", "Cancel their reservation", "Book a different flight", "Request a refund"],
        "answer": "Contact the hotel",
        "explanation_zh": "notify the hotel about late check-in。",
    },
]

_READING_PATTERNS: list[dict[str, Any]] = [
    {
        "format": "single",
        "topic": "office_admin",
        "passages": [{"label": "Memo", "text": "To all staff: Please submit your expense reports through the online portal no later than the 25th of each month. Late submissions may delay reimbursement. Contact Finance if you encounter technical issues with the system."}],
        "question": "What is the purpose of this memo?",
        "options": ["To explain expense report deadlines", "To announce staff layoffs", "To introduce a new product line", "To schedule annual vacations"],
        "answer": "To explain expense report deadlines",
        "explanation_zh": "submit expense reports... no later than the 25th。",
    },
    {
        "format": "double",
        "topic": "sales_marketing",
        "passages": [
            {"label": "Email — Sales Director", "text": "Team, Q2 targets were exceeded in the Northeast region. Please prepare case studies for next week's review."},
            {"label": "Reply — Regional Manager", "text": "I'll compile client feedback and revenue data by Thursday as requested."},
        ],
        "question": "What will the regional manager do?",
        "options": ["Gather data for a presentation", "Transfer to another department", "Decline the director's request", "Cancel the quarterly review"],
        "answer": "Gather data for a presentation",
        "explanation_zh": "compile client feedback and revenue data。",
    },
]


def _expand_vocab_pattern(p: dict[str, Any], rng: random.Random) -> dict[str, Any] | None:
    if p.get("fixed"):
        return dict(p["fixed"], topic=p["topic"], grammar_type=p["grammar_type"])
    tpl = p["template"]
    slots = p.get("slots") or {}
    if not slots:
        return None
    chosen: dict[str, str] = {}
    for key, vals in slots.items():
        chosen[key] = rng.choice(vals)
    question = tpl.format(**chosen)
    ans_key = p["answer_key"]
    answer = chosen[ans_key]
    wrong_map = p.get("wrong_forms", {})
    distractors = list(wrong_map.get(answer, [answer + "s", answer + "ed", answer + "ing"]))[:3]
    options = [answer] + distractors
    rng.shuffle(options)
    return {
        "question": question,
        "options": options,
        "answer": answer,
        "topic": p["topic"],
        "grammar_type": p["grammar_type"],
        "explanation_zh": p.get("explanation_zh", ""),
    }


def expand_pattern_pool(skill: str, *, variants: int = 40) -> list[dict[str, Any]]:
    """從模式種子展開原創變形題。"""
    rng = random.Random(42)
    if skill == "vocab":
        patterns = _VOCAB_PATTERNS
    elif skill == "grammar":
        patterns = _GRAMMAR_PATTERNS
    elif skill == "listening":
        patterns = _LISTENING_PATTERNS
    elif skill == "reading":
        patterns = _READING_PATTERNS
    else:
        return []

    out: list[dict[str, Any]] = []
    if skill == "grammar":
        for p in patterns:
            out.append(dict(p))
        return out

    if skill == "listening":
        for p in patterns:
            out.append(dict(p))
        return out

    if skill == "reading":
        for p in patterns:
            out.append(dict(p))
        return out

    for _ in range(variants):
        p = rng.choice(patterns)
        q = _expand_vocab_pattern(p, rng)
        if q:
            out.append(q)
    return out
