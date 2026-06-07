"""單字 PDF 匯出（精美排版）。"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from fpdf import FPDF

from toeic800.config import DATA_DIR, ROOT
from toeic800.utils.zh_tw import ensure_zh_tw

logger = logging.getLogger(__name__)

_BUNDLED_FONT = ROOT / "toeic800" / "assets" / "fonts" / "NotoSansTC-Regular.ttf"
_CACHED_FONT = DATA_DIR / "fonts" / "NotoSansTC-Regular.ttf"
_FONT_CDN_URL = (
    "https://cdn.jsdelivr.net/fontsource/fonts/noto-sans-tc@5.2.5/"
    "chinese-traditional-400-normal.ttf"
)

# 配色：深藍 + 金 + 灰
C_NAVY = (30, 58, 95)
C_GOLD = (201, 162, 39)
C_SLATE = (100, 116, 139)
C_LIGHT = (248, 250, 252)
C_BORDER = (226, 232, 240)
C_TEXT = (30, 41, 59)


def build_vocab_pdf(
    vocabulary: list[dict[str, Any]] | None = None,
    *,
    title: str = "單字表",
    jlpt_level: str = "",
    week_label: str = "",
    style: str = "default",
    sections: list[dict[str, Any]] | None = None,
) -> bytes:
    if style == "toeic":
        return _build_toeic_pdf(
            vocabulary or [],
            title=title,
            week_label=week_label,
            sections=sections,
        )
    if style in ("japanese", "default"):
        return _build_japanese_pdf(vocabulary or [], title=title, jlpt_level=jlpt_level)
    return _build_japanese_pdf(vocabulary or [], title=title, jlpt_level=jlpt_level)


def _font_candidates() -> list[Path]:
    linux = [
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
        Path("/usr/share/fonts/truetype/arphic/uming.ttc"),
    ]
    windows = [
        Path(r"C:\Windows\Fonts\msjh.ttc"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\mingliu.ttc"),
    ]
    return [_BUNDLED_FONT, _CACHED_FONT, *linux, *windows]


def _download_cjk_font(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(_FONT_CDN_URL, timeout=60)
    resp.raise_for_status()
    if len(resp.content) < 100_000:
        raise RuntimeError("下載的字型檔案大小異常")
    dest.write_bytes(resp.content)
    logger.info("已下載 PDF 字型至 %s", dest)
    return dest


def _font_path() -> Path:
    for p in _font_candidates():
        if p.exists():
            return p
    try:
        return _download_cjk_font(_CACHED_FONT)
    except Exception as exc:
        raise FileNotFoundError(
            "找不到中文字型（內建 Noto Sans TC、系統字型或 CDN 下載均失敗）"
        ) from exc


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
    sections: list[dict[str, Any]] | None = None,
) -> bytes:
    from toeic800.processing.vocab_selection import dedupe_vocabulary_by_word

    subtitle = " · ".join(x for x in (week_label, datetime.now().strftime("%Y-%m-%d")) if x)
    pdf = _VocabPDF(header_title=title, subtitle=subtitle)
    pdf.set_auto_page_break(auto=False, margin=18)
    pdf.add_page()

    page_w = 210 - 28
    x = 14

    pdf.set_fill_color(*C_NAVY)
    pdf.rect(0, 0, 210, 48, style="F")
    pdf.set_fill_color(*C_GOLD)
    pdf.rect(0, 48, 210, 3, style="F")

    pdf.set_xy(14, 12)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(pdf._family, size=20)
    pdf.multi_cell(page_w, 10, title)

    pdf.set_xy(14, 30)
    pdf.set_font(pdf._family, size=10)
    pdf.set_text_color(220, 230, 245)
    total_words = sum(len(s.get("vocabulary") or []) for s in sections) if sections else len(vocabulary)
    meta = f"多益 800–900 週報 · {subtitle} · 共 {total_words} 詞"
    pdf.multi_cell(page_w, 6, meta)

    pdf.set_xy(14, 56)
    pdf.set_text_color(*C_TEXT)
    pdf.set_font(pdf._family, size=8)
    pdf.multi_cell(
        page_w,
        4.5,
        "釋義／例句引用 Cambridge Dictionary（© Cambridge University Press），"
        "僅摘錄一義一例供個人學習；TOEIC® 為 ETS 註冊商標，本表與 ETS／IIBC 無關。",
    )
    pdf.set_y(68)

    if sections:
        word_idx = 0
        for sec in sections:
            word_idx = _draw_newspaper_section(
                pdf, sec, x=x, page_w=page_w, word_idx=word_idx
            )
    else:
        flat = dedupe_vocabulary_by_word(vocabulary)
        word_idx = 0
        for v in flat:
            y = pdf.get_y()
            if y > 250:
                pdf.add_page()
                y = pdf.get_y()
            word_idx += 1
            card_h = _draw_vocab_card(
                pdf,
                x=x,
                y=y,
                w=page_w,
                idx=word_idx,
                word=v.get("word", ""),
                pos=v.get("pos") or "",
                phonetic=v.get("phonetic") or "",
                meaning_zh=ensure_zh_tw(v.get("meaning_zh") or ""),
                meaning_en=v.get("meaning_en") or "",
                example_en=v.get("example_en") or "",
                example_zh=ensure_zh_tw(v.get("example_zh") or ""),
                secondary_label="EN",
            )
            pdf.set_y(y + card_h + 5)

    out = pdf.output()
    if isinstance(out, bytearray):
        return bytes(out)
    return out if isinstance(out, bytes) else out.encode("latin-1", errors="ignore")


def _ensure_page_space(pdf: _VocabPDF, needed: float, *, top: float = 22) -> None:
    if pdf.get_y() + needed > 285:
        pdf.add_page()
        pdf.set_y(top)


def _draw_newspaper_section(
    pdf: _VocabPDF,
    section: dict[str, Any],
    *,
    x: float,
    page_w: float,
    word_idx: int,
) -> int:
    title = section.get("title") or ""
    source = section.get("source") or ""
    week = section.get("week_label") or ""
    paragraphs = section.get("paragraphs") or []
    vocabulary = section.get("vocabulary") or []

    _ensure_page_space(pdf, 24)
    pdf.ln(4)
    pdf.set_fill_color(*C_NAVY)
    y0 = pdf.get_y()
    pdf.rect(x, y0, page_w, 10, style="F")
    pdf.set_xy(x + 3, y0 + 2)
    pdf.set_font(pdf._family, size=11)
    pdf.set_text_color(255, 255, 255)
    head = title if len(title) <= 72 else title[:69] + "…"
    pdf.cell(page_w - 6, 6, head)
    pdf.set_y(y0 + 12)

    pdf.set_font(pdf._family, size=8)
    pdf.set_text_color(*C_SLATE)
    meta = " · ".join(x for x in (source, week) if x)
    if meta:
        pdf.set_x(x)
        pdf.cell(page_w, 4, meta)
        pdf.ln(5)

    if section.get("summary_zh"):
        pdf.set_x(x)
        pdf.set_font(pdf._family, size=9)
        pdf.set_text_color(*C_TEXT)
        summary = ensure_zh_tw(section["summary_zh"])
        pdf.multi_cell(page_w, 4.5, summary)
        pdf.ln(2)

    pdf.set_font(pdf._family, size=10)
    pdf.set_text_color(*C_TEXT)
    for para in paragraphs:
        en = (para.get("text_en") or "").strip()
        zh = ensure_zh_tw(para.get("text_zh") or "").strip()
        if not en and not zh:
            continue
        block_h = 8.0
        if en:
            block_h += _text_block_height(pdf, en, page_w, 10, 4.8)
        if zh:
            block_h += _text_block_height(pdf, zh, page_w, 9, 4.5)
        _ensure_page_space(pdf, block_h)
        if en:
            pdf.set_x(x)
            pdf.set_font(pdf._family, size=10)
            pdf.set_text_color(*C_TEXT)
            pdf.multi_cell(page_w, 4.8, en)
        if zh:
            pdf.set_x(x)
            pdf.set_font(pdf._family, size=9)
            pdf.set_text_color(*C_SLATE)
            pdf.multi_cell(page_w, 4.5, zh)
        pdf.ln(3)

    if vocabulary:
        _ensure_page_space(pdf, 14)
        pdf.ln(2)
        pdf.set_draw_color(*C_GOLD)
        pdf.set_line_width(0.4)
        y_line = pdf.get_y()
        pdf.line(x, y_line, x + page_w, y_line)
        pdf.ln(4)
        pdf.set_x(x)
        pdf.set_font(pdf._family, size=11)
        pdf.set_text_color(*C_NAVY)
        pdf.cell(page_w, 6, f"精選單字（{len(vocabulary)} 詞）")
        pdf.ln(7)
        word_idx = _draw_vocab_two_column_grid(
            pdf, vocabulary, x=x, page_w=page_w, start_idx=word_idx
        )

    pdf.ln(6)
    return word_idx


def _draw_vocab_two_column_grid(
    pdf: _VocabPDF,
    vocabulary: list[dict[str, Any]],
    *,
    x: float,
    page_w: float,
    start_idx: int,
) -> int:
    gap = 6.0
    col_w = (page_w - gap) / 2
    left_x = x
    right_x = x + col_w + gap
    idx = start_idx
    i = 0
    while i < len(vocabulary):
        pair = vocabulary[i : i + 2]
        heights = []
        for v in pair:
            heights.append(
                _estimate_card_height(
                    pdf,
                    v.get("word", ""),
                    ensure_zh_tw(v.get("meaning_zh") or ""),
                    v.get("meaning_en") or "",
                    v.get("example_en") or "",
                    ensure_zh_tw(v.get("example_zh") or ""),
                    col_w,
                    phonetic=v.get("phonetic") or "",
                )
            )
        row_h = max(heights) if heights else 0
        _ensure_page_space(pdf, row_h + 4, top=22)
        y = pdf.get_y()

        v0 = pair[0]
        idx += 1
        _draw_vocab_card(
            pdf,
            x=left_x,
            y=y,
            w=col_w,
            idx=idx,
            word=v0.get("word", ""),
            pos=v0.get("pos") or "",
            phonetic=v0.get("phonetic") or "",
            meaning_zh=ensure_zh_tw(v0.get("meaning_zh") or ""),
            meaning_en=v0.get("meaning_en") or "",
            example_en=v0.get("example_en") or "",
            example_zh=ensure_zh_tw(v0.get("example_zh") or ""),
            secondary_label="EN",
        )

        if len(pair) > 1:
            v1 = pair[1]
            idx += 1
            _draw_vocab_card(
                pdf,
                x=right_x,
                y=y,
                w=col_w,
                idx=idx,
                word=v1.get("word", ""),
                pos=v1.get("pos") or "",
                phonetic=v1.get("phonetic") or "",
                meaning_zh=ensure_zh_tw(v1.get("meaning_zh") or ""),
                meaning_en=v1.get("meaning_en") or "",
                example_en=v1.get("example_en") or "",
                example_zh=ensure_zh_tw(v1.get("example_zh") or ""),
                secondary_label="EN",
            )

        pdf.set_y(y + row_h + 4)
        i += 2
    return idx


def _build_japanese_pdf(
    vocabulary: list[dict[str, Any]],
    *,
    title: str,
    jlpt_level: str,
) -> bytes:
    from toeic800.ui.ja_disclaimer import JA_DICT_PDF_NOTICE

    subtitle = " · ".join(
        x for x in (jlpt_level, datetime.now().strftime("%Y-%m-%d")) if x
    )
    pdf = _VocabPDF(header_title=title, subtitle=subtitle)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_fill_color(*C_NAVY)
    pdf.rect(0, 0, 210, 52, style="F")
    pdf.set_fill_color(*C_GOLD)
    pdf.rect(0, 52, 210, 3, style="F")

    pdf.set_xy(14, 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(pdf._family, size=22)
    pdf.multi_cell(182, 12, title)

    pdf.set_xy(14, 32)
    pdf.set_font(pdf._family, size=11)
    pdf.set_text_color(220, 230, 245)
    meta = f"共 {len(vocabulary)} 詞 · JLPT {jlpt_level or '—'} · {subtitle}"
    pdf.multi_cell(182, 7, meta)

    pdf.set_xy(14, 62)
    pdf.set_text_color(*C_TEXT)
    pdf.set_font(pdf._family, size=9)
    pdf.multi_cell(182, 5, JA_DICT_PDF_NOTICE)
    pdf.ln(6)

    page_w = 210 - 28
    x = 14

    for i, v in enumerate(vocabulary, 1):
        word = v.get("word", "")
        pos = v.get("pos") or ""
        phonetic = v.get("phonetic") or ""
        meaning_zh = ensure_zh_tw(v.get("meaning_zh") or "")
        meaning_en = v.get("meaning_en") or ""
        example_en = v.get("example_en") or ""
        example_zh = ensure_zh_tw(v.get("example_zh") or "")

        y = pdf.get_y()
        if y > 250:
            pdf.add_page()
            y = pdf.get_y()

        card_h = _draw_vocab_card(
            pdf,
            x=x,
            y=y,
            w=page_w,
            idx=i,
            word=word,
            pos=pos,
            phonetic=phonetic,
            meaning_zh=meaning_zh,
            meaning_en=meaning_en,
            example_en=example_en,
            example_zh=example_zh,
            secondary_label="羅馬字",
            phonetic_label="読み",
        )
        pdf.set_y(y + card_h + 5)

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
    *,
    secondary_label: str = "EN",
    phonetic_label: str = "",
    phonetic: str = "",
) -> float:
    line_w = w - 10
    h = 10.0
    if word:
        h += 7
    if phonetic:
        h += 6
    h += 6
    h += _text_block_height(pdf, f"中文　{meaning_zh or '—'}", line_w, 10, 5)
    if meaning_en:
        en_line = meaning_en if len(meaning_en) <= 120 else meaning_en[:117] + "…"
        h += _text_block_height(pdf, f"{secondary_label}　{en_line}", line_w, 8, 4)
    if example_en:
        ex = example_en if len(example_en) <= 140 else example_en[:137] + "…"
        h += _text_block_height(pdf, f"例句　{ex}", line_w, 8, 4)
        if example_zh:
            zh_ex = example_zh if len(example_zh) <= 80 else example_zh[:77] + "…"
            h += _text_block_height(pdf, zh_ex, line_w, 8, 4)
    return h + 6


def _text_block_height(
    pdf: _VocabPDF, text: str, width: float, font_size: int, line_h: float
) -> float:
    pdf.set_font(pdf._family, size=font_size)
    lines = pdf.multi_cell(width, line_h, text, dry_run=True, output="LINES")
    return max(1, len(lines)) * line_h


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
    secondary_label: str = "EN",
    phonetic_label: str = "",
) -> float:
    inner_x = x + 7
    line_w = w - 10
    h = _estimate_card_height(
        pdf,
        word,
        meaning_zh,
        meaning_en,
        example_en,
        example_zh,
        w,
        secondary_label=secondary_label,
        phonetic_label=phonetic_label,
        phonetic=phonetic,
    )

    pdf.set_fill_color(*C_LIGHT)
    pdf.set_draw_color(*C_BORDER)
    pdf.rect(x, y, w, h, style="FD")

    pdf.set_fill_color(*C_GOLD)
    pdf.rect(x, y, 4, h, style="F")

    pdf.set_xy(inner_x, y + 4)
    pdf.set_text_color(*C_NAVY)
    pdf.set_font(pdf._family, size=12)
    head = f"{idx}. {word}"
    if pos:
        head += f"  [{pos}]"
    pdf.cell(line_w, 6, head)

    if phonetic:
        pdf.set_xy(inner_x, pdf.get_y() + 1)
        pdf.set_font(pdf._family, size=8)
        pdf.set_text_color(*C_SLATE)
        ph_line = f"{phonetic_label}　{phonetic}" if phonetic_label else phonetic
        pdf.cell(line_w, 4, ph_line)

    pdf.set_xy(inner_x, pdf.get_y() + 2)
    pdf.set_font(pdf._family, size=10)
    pdf.set_text_color(*C_TEXT)
    pdf.multi_cell(line_w, 5, f"中文　{meaning_zh or '—'}")

    if meaning_en:
        pdf.set_xy(inner_x, pdf.get_y() + 1)
        pdf.set_font(pdf._family, size=8)
        pdf.set_text_color(*C_SLATE)
        en_line = meaning_en if len(meaning_en) <= 120 else meaning_en[:117] + "…"
        pdf.multi_cell(line_w, 4, f"{secondary_label}　{en_line}")

    if example_en:
        pdf.set_xy(inner_x, pdf.get_y() + 1)
        pdf.set_font(pdf._family, size=8)
        pdf.set_text_color(71, 85, 105)
        ex = example_en if len(example_en) <= 140 else example_en[:137] + "…"
        pdf.multi_cell(line_w, 4, f"例句　{ex}")
        if example_zh:
            pdf.set_xy(inner_x, pdf.get_y() + 1)
            pdf.set_text_color(*C_SLATE)
            zh_ex = example_zh if len(example_zh) <= 80 else example_zh[:77] + "…"
            pdf.multi_cell(line_w, 4, zh_ex)

    return h
