"""原創多益風格例句（非新聞摘錄）。"""

from __future__ import annotations



import hashlib

import re

from typing import Any



# 常見進階詞：原創例句 + 較貼近考場的中文

_SEED_EXAMPLES: dict[str, dict[str, str]] = {

    "slump": {

        "example_en": "Consumer spending may slump if borrowing costs remain elevated through the year.",

        "example_zh": "若借款成本全年維持偏高，消費支出可能驟降。",

    },

    "inflation": {

        "example_en": "The central bank raised rates to keep inflation from undermining long-term growth.",

        "example_zh": "央行升息以抑制通膨對長期成長的侵蝕。",

    },

    "volatility": {

        "example_en": "Market volatility increased after the firm missed its earnings forecast.",

        "example_zh": "該公司未達盈餘預測後，市場波動加劇。",

    },

    "merger": {

        "example_en": "The merger requires regulatory approval before shareholders can vote on the deal.",

        "example_zh": "併購案須取得監管核准，股東才能對交易表決。",

    },

    "dividend": {

        "example_en": "The board approved a higher dividend despite weaker quarterly revenue.",

        "example_zh": "儘管季度營收走弱，董事會仍核准提高股利。",

    },

    "recession": {

        "example_en": "Analysts warned that a prolonged recession could strain corporate liquidity.",

        "example_zh": "分析師警告，長期衰退可能擠壓企業流動性。",

    },

    "tariff": {

        "example_en": "The new tariff on imported components will affect manufacturing costs.",

        "example_zh": "進口零件的新關稅將影響製造成本。",

    },

    "sanction": {

        "example_en": "International sanctions limited the company's access to overseas capital.",

        "example_zh": "國際制裁限制了該公司取得海外資金。",

    },

    "forecast": {

        "example_en": "Management revised its sales forecast after supply disruptions continued.",

        "example_zh": "供應中斷持續，管理層下修銷售預測。",

    },

    "surge": {

        "example_en": "Energy prices surged when production cuts were announced unexpectedly.",

        "example_zh": "減產消息意外公布後，能源價格飆升。",

    },

    "plunge": {

        "example_en": "Share prices plunged following the unexpected resignation of the CEO.",

        "example_zh": "執行長意外請辭後，股價暴跌。",

    },

    "rally": {

        "example_en": "Technology stocks rallied after the firm reported stronger-than-expected profits.",

        "example_zh": "公司公布優於預期獲利後，科技股反彈。",

    },

    "portfolio": {

        "example_en": "Investors diversified their portfolio to reduce exposure to a single sector.",

        "example_zh": "投資人分散投資組合，以降低單一產業曝險。",

    },

    "liquidity": {

        "example_en": "The lender demanded additional collateral to improve balance-sheet liquidity.",

        "example_zh": "放款銀行要求追加擔保以改善資產負債表流動性。",

    },

    "leverage": {

        "example_en": "The private equity firm used leverage to finance the acquisition.",

        "example_zh": "私募股權公司運用槓桿為併購案融資。",

    },

    "compliance": {

        "example_en": "All regional offices must follow the updated compliance procedures immediately.",

        "example_zh": "各區辦公室須立即遵循更新後的合規流程。",

    },

    "procurement": {

        "example_en": "Procurement managers negotiated longer contracts to stabilize input prices.",

        "example_zh": "採購主管洽談較長合約以穩定投入成本。",

    },

    "infrastructure": {

        "example_en": "The government pledged funding for infrastructure projects in rural areas.",

        "example_zh": "政府承諾撥款支持偏鄉基礎建設計畫。",

    },

    "consolidate": {

        "example_en": "The airline plans to consolidate operations at its main hub next year.",

        "example_zh": "該航空公司計畫明年將營運整合至主要樞紐。",

    },

    "mitigate": {

        "example_en": "Hedging strategies can mitigate currency risk for exporters.",

        "example_zh": "避險策略可減輕出口商的匯率風險。",

    },

    "exacerbate": {

        "example_en": "Delays in shipping could exacerbate shortages across the supply chain.",

        "example_zh": "運輸延誤可能加劇供應鏈各環節的短缺。",

    },

    "substantial": {

        "example_en": "The company reported a substantial increase in overseas sales.",

        "example_zh": "公司公布海外銷售大幅成長。",

    },

    "unprecedented": {

        "example_en": "The board called an unprecedented meeting to address the data breach.",

        "example_zh": "董事會召開罕見的臨時會議因應資料外洩。",

    },

    "regulatory": {

        "example_en": "Regulatory changes may require firms to revise their disclosure policies.",

        "example_zh": "法規變動可能要求企業修訂資訊揭露政策。",

    },

    "shareholder": {

        "example_en": "Shareholders will receive the proxy statement before the annual meeting.",

        "example_zh": "股東將在年度大會前收到委託書。",

    },

    "default": {

        "example_en": "The borrower could default if refinancing terms are not renegotiated.",

        "example_zh": "若無法重新協商再融資條件，借款人可能違約。",

    },

    "stimulus": {

        "example_en": "Fiscal stimulus measures were designed to support small businesses.",

        "example_zh": "財政刺激措施旨在支援小型企業。",

    },

    "sentiment": {

        "example_en": "Investor sentiment improved after inflation data came in lower than expected.",

        "example_zh": "通膨數據低於預期後，投資人情緒改善。",

    },

    "benchmark": {

        "example_en": "The fund aims to outperform its benchmark index over a five-year period.",

        "example_zh": "該基金目標在五年內超越基準指數。",

    },

    "commodity": {

        "example_en": "Commodity prices fluctuated as demand from emerging markets softened.",

        "example_zh": "新興市場需求放緩，大宗商品價格波動。",

    },

}



# 依詞性選模板（{word} 會依詞性調整）

_TEMPLATES: dict[str, list[str]] = {

    "noun": [

        "The committee reviewed the {word} before approving the revised budget.",

        "Rising costs related to {word} have pressured profit margins this quarter.",

        "The report highlights how {word} affects long-term competitiveness.",

        "Managers discussed strategies to address issues involving {word}.",

    ],

    "verb": [

        "The firm may {word} its operations if market conditions do not improve.",

        "Analysts expect the sector to {word} once interest rates stabilize.",

        "The contract allows either party to {word} under specific circumstances.",

        "Executives plan to {word} resources toward high-growth regions.",

    ],

    "adjective": [

        "The board issued a {word} statement regarding the restructuring plan.",

        "Investors remain cautious amid {word} economic signals from overseas.",

        "The {word} proposal received approval after a lengthy review.",

        "A {word} approach to risk management helped limit losses.",

    ],

    "adverb": [

        "The subsidiary performed {word} better than analysts had predicted.",

        "Costs rose {word} after the supplier changed its delivery schedule.",

        "The team responded {word} to shifts in customer demand.",

    ],

    "default": [

        "The finance department will monitor trends related to {word} throughout the fiscal year.",

        "Understanding {word} is essential for professionals working in international business.",

        "The training session focused on how {word} appears in workplace communication.",

    ],

}





def _pos_bucket(pos: str | None) -> str:

    if not pos:

        return "default"

    low = pos.lower()

    if "noun" in low or low.startswith("n."):

        return "noun"

    if "verb" in low or low.startswith("v."):

        return "verb"

    if "adj" in low or low.startswith("adj"):

        return "adjective"

    if "adv" in low or low.startswith("adv"):

        return "adverb"

    return "default"





def _pick_template(word: str, bucket: str) -> str:

    templates = _TEMPLATES.get(bucket) or _TEMPLATES["default"]

    idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % len(templates)

    return templates[idx]





def generate_example_sentence(word: str, pos: str | None = None) -> str:

    """產生原創例句（非新聞原文）。"""

    key = word.lower().strip()

    seed = _SEED_EXAMPLES.get(key)

    if seed:

        return seed["example_en"]

    bucket = _pos_bucket(pos)

    tpl = _pick_template(key, bucket)

    display = word if bucket != "verb" else _verb_form(key)

    return tpl.format(word=display)





def generate_example_zh(word: str) -> str:

    key = word.lower().strip()

    seed = _SEED_EXAMPLES.get(key)

    if seed:

        return seed["example_zh"]

    return ""





def _verb_form(word: str) -> str:

    if word.endswith("e") and len(word) > 3:

        return word  # mitigate, consolidate

    if word.endswith("y") and len(word) > 2 and word[-2] not in "aeiou":

        return word[:-1] + "ies"

    if word.endswith(("s", "x", "z", "ch", "sh")):

        return word + "es"

    return word





def enrich_vocab_example(v: dict[str, Any]) -> dict[str, Any]:
    """確保單字條目有例句；Cambridge 引用資料不覆寫。"""
    from toeic800.processing.vocab_glossary import apply_glossary

    if (v.get("dict_source") or "").lower() == "cambridge":
        return apply_glossary(v.get("word") or "", dict(v))

    word = v.get("word") or ""
    if not word:
        return v
    out = apply_glossary(word, dict(v))
    ex = generate_example_sentence(word, out.get("pos"))
    out["example_en"] = ex
    zh = generate_example_zh(word)
    if zh:
        out["example_zh"] = zh
    elif not out.get("example_zh"):
        from toeic800.processing.translator import translate_text

        out["example_zh"] = translate_text(ex)
    return out


