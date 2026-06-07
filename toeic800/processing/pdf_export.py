"""單字 PDF 匯出（精美排版）。"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF

from toeic800.utils.zh_tw import ensure_zh_tw

# 配色：深藍 + 金 + 灰
C_NAVY = (30, 58, 95)
C_GOLD = (201, 162, 39)
C_SLATE = (100, 116, 139)
C_LIGHT = (248, 250, 252)
C_BORDER = (226, 232, 240)
C_TEXT = (30, 41, 59)


def build_vocab_pdf(
    vocabulary: list[dict[str, Any]],
    *,
    title: str = "單字表",
    jlpt_level: str = "",
    week_label: str = "",
    style: str = "default",
) -> bytes:
    if style == "toeic":
        return _build_toeic_pdf(vocabulary, title=title, week_label=week_label)
    return _build_simple_pdf(vocabulary, title=title, jlpt_level=jlpt_level)


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


class _VocabPDF(FPDF):
    def __init__(self, *, header_title: str, subtitle: str = "") -> None:
        super().__init__()
        self._header_title = header_title
        self._subtitle = subtitle
        self._family = "CJK"
        font_path = _font_path()
        self.add_font(self._family, "", str(font_path))

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_fill_color(*C_NAVY)
        self.rect(0, 0, 210, 14, style="F")
        self.set_text_color(255, 255, 255)
        self.set_font(self._family, size=9)
        self.set_xy(10, 4)
        self.cell(0, 6, self._header_title)
        self.set_text_color(*C_SLATE)
        self.set_xy(10, 18)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font(self._family, size=8)
        self.set_text_color(*C_SLATE)
        self.cell(0, 8, f"第 {self.page_no()} 頁", align="C")


def _build_toeic_pdf(
    vocabulary: list[dict[str, Any]],
    *,
    title: str,
    week_label: str,
) -> bytes:
    subtitle = " · ".join(x for x in (week_label, datetime.now().strftime("%Y-%m-%d")) if x)
    pdf = _VocabPDF(header_title=title, subtitle=subtitle)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # 封面標題區
    pdf.set_fill_color(*C_NAVY)
    pdf.rect(0, 0, 210, 52, style="F")
    pdf.set_fill_color(*C_GOLD)
    pdf.rect(0, 52, 210, 3, style="F")

    pdf.set_xy(14, 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(pdf._family, size=22)
    pdf.multi_cell(0, 12, title)

    pdf.set_xy(14, 32)
    pdf.set_font(pdf._family, size=11)
    pdf.set_text_color(220, 230, 245)
    meta = f"共 {len(vocabulary)} 詞 · 多益 800–900 進階 · {subtitle}"
    pdf.multi_cell(0, 7, meta)

    pdf.set_xy(14, 62)
    pdf.set_text_color(*C_TEXT)
    pdf.set_font(pdf._family, size=9)
    pdf.multi_cell(
        0,
        5,
        "例句為原創練習用語，非新聞原文。TOEIC® 為 ETS 註冊商標；本表與 ETS／IIBC 無關。",
    )
    pdf.ln(6)

    col_w = (210 - 28) / 2
    x_left, x_right = 14, 14 + col_w + 4
    y_start = pdf.get_y()
    col = 0

    for i, v in enumerate(vocabulary, 1):
        word = v.get("word", "")
        pos = v.get("pos") or ""
        phonetic = v.get("phonetic") or ""
        meaning_zh = ensure_zh_tw(v.get("meaning_zh") or "")
        meaning_en = v.get("meaning_en") or ""
        example_en = v.get("example_en") or ""
        example_zh = ensure_zh_tw(v.get("example_zh") or "")

        x = x_left if col == 0 else x_right
        if col == 0:
            y = pdf.get_y()
        else:
            y = max(pdf.get_y(), y_start)

        card_h = _estimate_card_height(pdf, word, meaning_zh, meaning_en, example_en, example_zh, col_w)
        if y + card_h > 275:
            if col == 1:
                pdf.add_page()
                y_start = pdf.get_y()
                y = y_start
                x = x_left
                col = 0
            else:
                col = 1
                x = x_right
                y = y_start
                if y + card_h > 275:
                    pdf.add_page()
                    y_start = pdf.get_y()
                    y = y_start
                    x = x_left
                    col = 0

        _draw_vocab_card(
            pdf,
            x=x,
            y=y,
            w=col_w,
            idx=i,
            word=word,
            pos=pos,
            phonetic=phonetic,
            meaning_zh=meaning_zh,
            meaning_en=meaning_en,
            example_en=example_en,
            example_zh=example_zh,
        )

        if col == 0:
            pdf.set_y(y + card_h + 4)
            col = 1
        else:
            new_y = y + card_h + 4
            pdf.set_y(max(new_y, pdf.get_y()))
            y_start = pdf.get_y()
            col = 0

    out = pdf.output()
    if isinstance(out, bytearray):
        return bytes(out)
    return out if isinstance(out, bytes) else out.encode("latin-1", errors="ignore")


def _estimate_card_height(
    pdf: _VocabPDF,
    word: str,
    meaning_zh: str,
    meaning_en: str,
    example_en: str,
    example_zh: str,
    w: float,
) -> float:
    h = 8 + 10 + 6 + 6
    if meaning_en:
        h += 6
    if example_en:
        h += 12
    if example_zh:
        h += 6
    if len(meaning_zh) > 24:
        h += 4
    if len(meaning_en) > 50:
        h += 4
    return min(h, 58)


def _draw_vocab_card(
    pdf: _VocabPDF,
    *,
    x: float,
    y: float,
    w: float,
    idx: int,
    word: str,
    pos: str,
    phonetic: str,
    meaning_zh: str,
    meaning_en: str,
    example_en: str,
    example_zh: str,
) -> None:
    h = _estimate_card_height(pdf, word, meaning_zh, meaning_en, example_en, example_zh, w)
    pdf.set_fill_color(*C_LIGHT)
    pdf.set_draw_color(*C_BORDER)
    pdf.rect(x, y, w, h, style="FD")

    pdf.set_fill_color(*C_GOLD)
    pdf.rect(x, y, 4, h, style="F")

    pdf.set_xy(x + 7, y + 3)
    pdf.set_text_color(*C_NAVY)
    pdf.set_font(pdf._family, size=12)
    head = f"{idx}. {word}"
    if pos:
        head += f"  [{pos}]"
    pdf.cell(w - 10, 7, head, new_x="LMARGIN", new_y="NEXT")

    if phonetic:
        pdf.set_x(x + 7)
        pdf.set_font(pdf._family, size=8)
        pdf.set_text_color(*C_SLATE)
        pdf.cell(w - 10, 4, phonetic, new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(x + 7)
    pdf.set_font(pdf._family, size=10)
    pdf.set_text_color(*C_TEXT)
    pdf.multi_cell(w - 10, 5, f"中文  {meaning_zh or '—'}")

    if meaning_en:
        pdf.set_x(x + 7)
        pdf.set_font(pdf._family, size=8)
        pdf.set_text_color(*C_SLATE)
        en_line = meaning_en if len(meaning_en) <= 90 else meaning_en[:87] + "…"
        pdf.multi_cell(w - 10, 4, f"EN  {en_line}")

    if example_en:
        pdf.set_x(x + 7)
        pdf.set_font(pdf._family, size=8)
        pdf.set_text_color(71, 85, 105)
        ex = example_en if len(example_en) <= 100 else example_en[:97] + "…"
        pdf.multi_cell(w - 10, 4, f"例  {ex}")
        if example_zh:
            pdf.set_x(x + 7)
            pdf.set_text_color(*C_SLATE)
            zh_ex = example_zh if len(example_zh) <= 60 else example_zh[:57] + "…"
            pdf.multi_cell(w - 10, 4, f"    {zh_ex}")


def _build_simple_pdf(
    vocabulary: list[dict[str, Any]],
    *,
    title: str,
    jlpt_level: str,
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
        pdf.multi_cell(0, 5, f"中文：{ensure_zh_tw(v.get('meaning_zh', ''))}")
        if v.get("meaning_en"):
            pdf.multi_cell(0, 5, f"讀音：{v.get('meaning_en', '')}")
        if v.get("example_en"):
            pdf.multi_cell(0, 5, f"例句：{v.get('example_en', '')}")
            pdf.multi_cell(0, 5, f"      {ensure_zh_tw(v.get('example_zh', ''))}")
        pdf.ln(2)

    out = pdf.output()
    if isinstance(out, bytearray):
        return bytes(out)
    return out if isinstance(out, bytes) else out.encode("latin-1", errors="ignore")
