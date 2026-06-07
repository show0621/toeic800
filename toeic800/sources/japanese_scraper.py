"""NHK やさしいニュース 等日文頁面解析。"""
from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urljoin

import requests
import trafilatura
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.9",
}


def fetch_japanese_article(url: str, parser: str = "generic") -> dict[str, Any]:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text

    if parser == "nhk_easy" or "news/easy" in url or "news.web.nhk" in url:
        parsed = _parse_nhk_web(html, url)
        if parsed.get("paragraphs_raw"):
            return parsed

    return _parse_generic(html, url)


def _parse_nhk_web(html: str, url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.select_one("h1, title")
    title = title_el.get_text(strip=True) if title_el else ""
    title = re.sub(r"\s*-+\s*NHK.*$", "", title).strip()

    paragraphs: list[str] = []
    for sel in (
        "article p",
        "div[data-testid='article-body'] p",
        "section.body-text p",
        "div.article-body p",
        "p",
    ):
        for p in soup.select(sel):
            text = p.get_text(" ", strip=True)
            if text and len(text) > 8 and text not in paragraphs:
                paragraphs.append(text)
        if paragraphs:
            break

    if not paragraphs:
        body = trafilatura.extract(html, url=url) or ""
        paragraphs = [p.strip() for p in body.split("\n") if len(p.strip()) > 8]

    audio_url = None
    for a in soup.select("a[href*='.mp3'], audio source, source[src*='.mp3']"):
        href = a.get("href") or a.get("src")
        if href and ".mp3" in href:
            audio_url = urljoin(url, href)
            break
    if not audio_url:
        m = re.search(r'(https?://[^"\']+\.mp3)', html)
        if m:
            audio_url = m.group(1)

    return {
        "title": title,
        "paragraphs_raw": paragraphs[:20],
        "summary_en": paragraphs[0][:200] if paragraphs else "",
        "audio_url": audio_url,
        "has_video": False,
        "published_at": None,
    }


def _parse_nhk_easy(html: str, url: str) -> dict[str, Any]:
    return _parse_nhk_web(html, url)


def _parse_generic(html: str, url: str) -> dict[str, Any]:
    downloaded = trafilatura.extract(
        html, url=url, output_format="json", with_metadata=True
    )
    title = ""
    body = ""
    published = None
    if downloaded:
        import json

        meta = json.loads(downloaded)
        title = meta.get("title") or ""
        body = meta.get("text") or ""
        published = meta.get("date")
    if not body:
        body = trafilatura.extract(html, url=url) or ""

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if len(p.strip()) > 8]
    if len(paragraphs) == 1 and len(paragraphs[0]) > 400:
        sents = re.split(r"(?<=[。！？])\s*", paragraphs[0])
        paragraphs = [s for s in sents if len(s.strip()) > 8]

    return {
        "title": title,
        "paragraphs_raw": paragraphs,
        "summary_en": paragraphs[0][:200] if paragraphs else "",
        "audio_url": None,
        "has_video": False,
        "published_at": published,
    }
