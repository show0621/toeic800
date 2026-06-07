"""合法可用的公開學習資源登錄（格式／詞彙／例句，非官方考古題）。"""
from __future__ import annotations

from typing import Any

# 僅收錄允許引用或僅取「格式／事實」的來源；禁止 ETS／商業題庫原文
OPEN_SOURCES: dict[str, dict[str, Any]] = {
    "iibc_format": {
        "name": "IIBC TOEIC Official Format",
        "url": "https://www.iibc-global.org/english/toeic/test/lr/about/format.html",
        "license": "公開格式說明（非試題）",
        "use": "Part 5–7 題型、時間、主題類別",
        "attribution": "題型結構參考 IIBC 公開格式說明。",
    },
    "cambridge": {
        "name": "Cambridge Dictionary (繁中)",
        "url": "https://dictionary.cambridge.org/zht/",
        "license": "© Cambridge University Press · 摘錄一義一例",
        "use": "單字釋義、例句（非完整詞典）",
        "attribution": "釋義／例句引用 Cambridge Dictionary，僅摘錄一義一例。",
    },
    "tatoeba": {
        "name": "Tatoeba",
        "url": "https://tatoeba.org/",
        "license": "CC BY 2.0 FR（依各句作者）",
        "use": "片語、例句改編為克漏字／聽力對話",
        "attribution": "例句改編自 Tatoeba（CC BY 2.0 FR），僅個人學習。",
    },
    "wiktionary": {
        "name": "Wiktionary",
        "url": "https://en.wiktionary.org/",
        "license": "CC BY-SA 3.0",
        "use": "片語／搭配詞簡短說明（摘錄）",
        "attribution": "片語說明引用 Wiktionary（CC BY-SA 3.0）。",
    },
    "article_db": {
        "name": "本 App 新聞資料庫",
        "url": "",
        "license": "原文著作權屬 BBC/CNN 等；本 App 僅摘錄短段落出題",
        "use": "Part 7 閱讀（短摘錄＋理解題）",
        "attribution": "閱讀短文摘錄自已儲存之新聞連結，請至原文網站閱讀全文。",
    },
    "original": {
        "name": "本專案原創",
        "url": "",
        "license": "原創擬真",
        "use": "模板展開、對話腳本、題幹改寫",
        "attribution": "本題為原創擬真練習，非 ETS／IIBC 官方試題。",
    },
}

FORBIDDEN_SOURCES = (
    "ETS 官方考古題",
    "商業機構題庫（如某某多益書）",
    "付費 App 題目原文",
    "完整 Cambridge 詞典批量複製",
)


def source_attribution_line(source_id: str, *, url: str = "") -> str:
    meta = OPEN_SOURCES.get(source_id, OPEN_SOURCES["original"])
    line = meta["attribution"]
    link = url or meta.get("url") or ""
    if link:
        line += f" 來源：{link}"
    return line
