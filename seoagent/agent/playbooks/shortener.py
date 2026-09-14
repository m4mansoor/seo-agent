"""Tier A playbook: URL shorteners. Paste the target, submit, capture the short link, verify it resolves."""
from __future__ import annotations

import re
from urllib.parse import urlparse

from playwright.sync_api import Page

from ...models import Site
from ...gates import gate_from_reason
from ..browser import bot_gate, dismiss_banners, find_submit, find_url_input, quoted_names, safe_goto, visible_urls

NOT_A_SHORT_LINK = re.compile(r"/(human|captcha|login|signin|signup|register|create|preview|stats?|info|terms|privacy|about|contact|api|blog)\b", re.I)


def _host(u: str) -> str:
    return urlparse(u).netloc.lower().removeprefix("www.")


def _same_site(u: str, domain: str) -> bool:
    host = _host(u)
    return host == domain or host.endswith("." + domain) or domain.endswith("." + host)


def pick_short_link(before: set[str], after: list[str], site_domain: str, site_url: str, target_url: str) -> list[str]:
    """Candidate short links among URLs that appeared after submitting, best first.
    A short link lives on the shortener's own domain, has a short opaque path, and does not carry the target as a
    query parameter or point at a utility page."""
    tgt = target_url.rstrip("/").lower()
    cands = []
    for u in after:
        if u in before or not _same_site(u, site_domain):
            continue
        if u.rstrip("/") == site_url.rstrip("/") or tgt in u.lower():
            continue
        p = urlparse(u)
        segs = [s for s in p.path.split("/") if s]
        if not segs or len(segs) > 2 or p.query or NOT_A_SHORT_LINK.search(p.path):
            continue
        if not re.fullmatch(r"[A-Za-z0-9_\-]{2,32}", segs[-1]):
            continue
        cands.append(u)
    cands.sort(key=lambda u: (len(urlparse(u).path.strip("/").split("/")), len(u)))
    return cands


def verify(page: Page, short: str, target_url: str) -> bool:
    """The short link resolves to the target, or shows an interstitial that references it."""
    try:
        resp = page.request.get(short, max_redirects=5, timeout=15000)
        if _host(resp.url) == _host(target_url):
            return True
        body = resp.text()[:200000]
        return target_url.rstrip("/") in body
    except Exception:
        return False


def run(page: Page, site: Site, target_url: str, proof_path: str) -> dict:
    if not safe_goto(page, site.url):
        return {"status": "failed", "notes": "site did not load"}
    dismiss_banners(page)
    gate = bot_gate(page)
    if gate:
        page.screenshot(path=proof_path)
        return {"status": "gated", "notes": f"needs a human: {gate}", "gate": gate_from_reason(gate, site.name).model_dump()}
    field = find_url_input(page)
    if field is None:
        page.screenshot(path=proof_path)
        return {"status": "failed", "notes": "no URL input found"}
    before = set(visible_urls(page))
    field.click()
    field.fill(target_url)
    names = quoted_names([s.text for s in site.steps])
    btn = find_submit(page, near=field, names=names)
    if btn is not None:
        btn.click()
    else:
        field.press("Enter")
    page.wait_for_timeout(3500)
    gate = bot_gate(page)
    if gate:
        page.screenshot(path=proof_path)
        return {"status": "gated", "notes": f"needs a human: {gate} after submitting", "gate": gate_from_reason(gate, site.name).model_dump()}
    cands = pick_short_link(before, visible_urls(page), site.domain, site.url, target_url)
    page.screenshot(path=proof_path)
    if not cands:
        return {"status": "failed", "notes": "submitted but no short link appeared"}
    for short in cands[:3]:
        if verify(page, short, target_url):
            return {"status": "placed", "live_url": short, "notes": "short link verified"}
    return {"status": "unverified", "live_url": cands[0], "notes": "short link captured; could not confirm it resolves to the target (interstitial or script redirect)"}
