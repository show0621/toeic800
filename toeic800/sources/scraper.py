"""抓取單篇文章正文、影片與字幕線索。"""
from __future__ import annotations

import json
import logging
import re
from typing import Any
from urllib.parse import urljoin

import requests
import trafilatura

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_article_content(url: str) -> dict[str, Any]:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text

    downloaded = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=False,
        output_format="json",
        with_metadata=True,
    )
    meta: dict[str, Any] = {}
    body = ""
    if downloaded:
        meta = json.loads(downloaded)
        body = meta.get("text") or ""

    if not body:
        body = trafilatura.extract(html, url=url) or ""

    paragraphs = _split_paragraphs(body)
    video = _extract_video(html, url)
    subtitles = _extract_subtitles_from_html(html)

    return {
        "title": meta.get("title") or _og_title(html) or "",
        "summary_en": meta.get("description") or (paragraphs[0][:280] if paragraphs else ""),
        "paragraphs_raw": paragraphs,
        "published_at": meta.get("date"),
        "has_video": bool(video.get("video_url") or video.get("video_embed_html")),
        **video,
        "subtitles_raw": subtitles,
    }


def _split_paragraphs(text: str) -> list[str]:
    chunks = [p.strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]
    if len(chunks) == 1 and len(chunks[0]) > 400:
        sents = re.split(r"(?<=[.!?])\s+", chunks[0])
        grouped: list[str] = []
        buf = ""
        for s in sents:
            s = s.strip()
            if not s:
                continue
            if len(buf) + len(s) > 320:
                if buf:
                    grouped.append(buf.strip())
                buf = s if s.endswith((".", "!", "?")) else s + "."
            else:
                buf = (buf + " " + s).strip() if buf else s
        if buf:
            grouped.append(buf.strip())
        if grouped:
            return grouped
    if not chunks and text:
        chunks = [s.strip() for s in text.split(". ") if len(s.strip()) > 40]
    return chunks


def _og_title(html: str) -> str:
    m = re.search(
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)',
        html,
        re.I,
    )
    return m.group(1).strip() if m else ""


def _extract_video(html: str, base_url: str) -> dict[str, Any]:
    video_url = None
    embed_html = None
    thumb = None

    for pattern in (
        r'<meta[^>]+property=["\']og:video(?::url)?["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+name=["\']twitter:player:stream["\'][^>]+content=["\']([^"\']+)',
    ):
        m = re.search(pattern, html, re.I)
        if m:
            video_url = urljoin(base_url, m.group(1))
            break

    iframe = re.search(
        r'<iframe[^>]+src=["\']([^"\']+(?:youtube|bbc|cnn)[^"\']*)["\']',
        html,
        re.I,
    )
    if iframe:
        src = urljoin(base_url, iframe.group(1))
        embed_html = (
            f'<iframe src="{src}" width="100%" height="400" '
            'frameborder="0" allowfullscreen></iframe>'
        )
        if not video_url:
            video_url = src

    yt = re.search(
        r'"(?:embedUrl|contentUrl)"\s*:\s*"(https://[^"]+youtube[^"]+)"',
        html,
    )
    if yt and not video_url:
        video_url = yt.group(1)

    tm = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        html,
        re.I,
    )
    if tm:
        thumb = tm.group(1)

    return {
        "video_url": video_url,
        "video_embed_html": embed_html,
        "thumbnail_url": thumb,
    }


def _extract_subtitles_from_html(html: str) -> list[dict[str, Any]]:
    """從頁面 JSON-LD / transcript 區塊擷取英文字幕片段。"""
    subs: list[dict[str, Any]] = []

    for block in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        subs.extend(_subs_from_ld(data))

    transcript = re.search(
        r'class=["\'][^"\']*transcript[^"\']*["\'][^>]*>(.*?)</div>',
        html,
        re.I | re.S,
    )
    if transcript:
        text = re.sub(r"<[^>]+>", " ", transcript.group(1))
        for i, sent in enumerate(_split_paragraphs(text)):
            if len(sent) > 20:
                subs.append({"en": sent, "start_sec": float(i * 5), "end_sec": float((i + 1) * 5)})

    return subs


def _subs_from_ld(data: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if isinstance(data, list):
        for item in data:
            out.extend(_subs_from_ld(item))
        return out
    if not isinstance(data, dict):
        return out

    if data.get("@type") == "VideoObject":
        desc = data.get("description") or data.get("transcript") or ""
        if isinstance(desc, str) and len(desc) > 30:
            for i, sent in enumerate(_split_paragraphs(desc)):
                out.append({"en": sent, "start_sec": float(i * 6), "end_sec": float((i + 1) * 6)})

    for key in ("@graph", "hasPart", "subjectOf"):
        child = data.get(key)
        if child:
            out.extend(_subs_from_ld(child))
    return out
