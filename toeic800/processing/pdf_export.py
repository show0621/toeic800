"""單字 PDF 匯出。"""
from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF


def build_vocab_pdf(
    vocabulary: list[dict[str, Any]],
    *,
    title: str = "單字表",
    jlpt_level: str = "",
) -> bytes:
    font_path = _font_path()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    family = "CJK"
    pdf.add_font(family, "", str(font_path))
    pdf.set_font(family, size=14)
    header = f"{title} {jlpt_level}".strip()
    pdf.cell(0, 10, header, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(family, size=9)
    pdf.cell(0, 6, datetime.now().strftime("%Y-%m-%d"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    for i, v in enumerate(vocabulary, 1):
        line1 = f"{i}. {v.get('word', '')}  [{v.get('pos', '')}]  {v.get('phonetic', '')}"
        pdf.set_font(family, size=11)
        pdf.multi_cell(0, 6, line1)
        pdf.set_font(family, size=9)
        pdf.multi_cell(0, 5, f"中文：{v.get('meaning_zh', '')}")
        if v.get("meaning_en"):
            pdf.multi_cell(0, 5, f"讀音：{v.get('meaning_en', '')}")
        if v.get("example_en"):
            pdf.multi_cell(0, 5, f"例句：{v.get('example_en', '')}")
            pdf.multi_cell(0, 5, f"      {v.get('example_zh', '')}")
        pdf.ln(2)

    out = pdf.output()
    return out if isinstance(out, bytes) else out.encode("latin-1", errors="ignore")


def _font_path() -> Path:
    candidates = [
        Path(r"C:\Windows\Fonts\msjh.ttc"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\mingliu.ttc"),
        Path(r"C:\Windows\Fonts\msgothic.ttc"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("找不到中文字型（微軟正黑體 / 細明體）")
