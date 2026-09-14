"""Deterministic check that a live page really carries the backlink."""
from __future__ import annotations

import re
import ssl
import urllib.request
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


class LinkCheck(BaseModel):
    live_url: str
    fetched: bool
    status: Optional[int] = None
    found: bool = False
    anchor_matches: bool = False
    anchor_found: Optional[str] = None
    nofollow: Optional[bool] = None
    href: Optional[str] = None
    notes: str = ""


class _Anchors(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict] = []
        self._cur: Optional[dict] = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            a = dict(attrs)
            self._cur = {"href": a.get("href", ""), "rel": (a.get("rel") or "").lower(), "text": ""}

    def handle_data(self, data):
        if self._cur is not None:
            self._cur["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._cur is not None:
            self._cur["text"] = " ".join(self._cur["text"].split())
            self.links.append(self._cur)
            self._cur = None


def _norm(u: str) -> str:
    p = urlparse(u.strip())
    return (p.netloc.lower().removeprefix("www.") + p.path.rstrip("/")).lower()


def check_html(html: str, target_url: str, anchor_text: str = "", live_url: str = "") -> LinkCheck:
    parser = _Anchors()
    parser.feed(html)
    tgt = _norm(target_url)
    hits = [l for l in parser.links if l["href"] and _norm(l["href"]) == tgt]
    out = LinkCheck(live_url=live_url, fetched=True, found=bool(hits))
    if not hits:
        # bare URL in text counts as present but is not a hyperlink
        if re.search(re.escape(target_url.rstrip("/")), html, re.I):
            out.notes = "target URL appears as plain text, not as a hyperlink"
        else:
            out.notes = "target URL not found on the page"
        return out
    best = hits[0]
    if anchor_text:
        for h in hits:
            if h["text"].strip().lower() == anchor_text.strip().lower():
                best = h
                break
        out.anchor_matches = best["text"].strip().lower() == anchor_text.strip().lower()
    out.anchor_found = best["text"]
    out.href = best["href"]
    out.nofollow = "nofollow" in best["rel"] or "ugc" in best["rel"] or "sponsored" in best["rel"]
    out.notes = "hyperlink to target found" + ("" if out.anchor_matches or not anchor_text else f"; anchor is {best['text']!r}, not {anchor_text!r}")
    return out


def check_live(live_url: str, target_url: str, anchor_text: str = "", timeout: int = 20) -> LinkCheck:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(live_url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            html = r.read(2_000_000).decode("utf-8", "replace")
            out = check_html(html, target_url, anchor_text, live_url)
            out.status = r.status
            return out
    except Exception as e:
        return LinkCheck(live_url=live_url, fetched=False, notes=f"could not fetch: {type(e).__name__}: {str(e)[:100]}")
