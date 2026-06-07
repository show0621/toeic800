"""TOEIC L&R 官方格式規範（2018 改版後）— 供 RAG 擬真出題參考。

資料來源（公開格式說明，非試題原文）：
- IIBC TOEIC Official Format: https://www.iibc-global.org/english/toeic/test/lr/about/format.html
- Part 5 常考主題：office, finance, sales, travel, HR, manufacturing (800+ 實戰論壇整理)
"""
from __future__ import annotations

TOEIC_TOPICS_800 = (
    "office_admin",      # 辦公行政、會議、排程
    "finance_banking",   # 財務、銀行、會計
    "sales_marketing",   # 銷售、行銷、客戶
    "hr_personnel",      # 人資、招募、培訓
    "manufacturing",     # 製造、品管、物流
    "travel_hospitality",# 差旅、酒店、交通
    "it_tech",           # 資訊、軟體、網路
    "contracts_legal",   # 合約、法務、合規
)

PART5_GRAMMAR_TYPES = (
    "tense_aspect",       # 時態、完成式
    "word_form",          # 詞性轉換
    "preposition",        # 介系詞、固定搭配
    "conjunction",        # 連接詞、從屬子句
    "pronoun_agreement",  # 代名詞、主詞一致
    "conditional",        # 條件句、虛擬語氣
    "collocation",        # 商業搭配詞
)

PART_SPEC = {
    "vocab": {"part": "Part 5", "label": "Incomplete Sentences · 單字／詞性", "count_exam": 30},
    "grammar": {"part": "Part 5/6", "label": "Grammar & Text Completion · 文法", "count_exam": 46},
    "listening": {"part": "Part 3/4", "label": "Conversations & Talks · 聽力", "count_exam": 69},
    "reading_single": {"part": "Part 7", "label": "Single Passages · 單篇", "count_exam": 29},
    "reading_double": {"part": "Part 7", "label": "Double Passages · 雙篇", "count_exam": 25},
    "reading_triple": {"part": "Part 7", "label": "Triple Passages · 三篇", "count_exam": 25},
}

SCORE_BAND = "800-900"
