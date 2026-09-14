"""Tier A playbook: open submission forms (no account). Fill URL, title and description, submit, verify."""
from __future__ import annotations

import re
from typing import Optional

from playwright.sync_api import Locator, Page

from ...models import Site
from ...gates import gate_from_reason
from ..browser import dismiss_banners, find_submit, find_url_input, quoted_names, safe_goto, visible_urls


def _find_text(page: Page, hints: tuple[str, ...], exclude: Optional[Locator] = None) -> Optional[Locator]:
    cands = page.locator("input[type=text], input:not([type]), textarea")
    for i in range(min(cands.count(), 40)):
        loc = cands.nth(i)
        try:
            if not loc.is_visible():
                continue
            blob = loc.evaluate("e => [e.name, e.id, e.placeholder, e.getAttribute('aria-label')].join(' ').toLowerCase()")
        except Exception:
            continue
        if any(h in blob for h in hints):
            if exclude is not None:
                try:
                    if loc.evaluate("e => e") == exclude.evaluate("e => e"):
                        continue
                except Exception:
                    pass
            return loc
    return None


def run(page: Page, site: Site, target_url: str, anchor_text: str, proof_path: str, description: str = "") -> dict:
    if not safe_goto(page, site.url):
        return {"status": "failed", "notes": "site did not load"}
    dismiss_banners(page)
    names = quoted_names([s.text for s in site.steps])
    # follow an "Add link / Submit" entry point if the form is not on the landing page
    if find_url_input(page) is None:
        for name in names + ["Submit", "Add link", "Add URL", "Add site", "Submit URL", "Suggest"]:
            try:
                link = page.get_by_role("link", name=re.compile(re.escape(name), re.I)).first
                if link.is_visible(timeout=400):
                    link.click(); page.wait_for_timeout(1500); break
            except Exception:
                continue
    field = find_url_input(page)
    if field is None:
        page.screenshot(path=proof_path)
        return {"status": "failed", "notes": "no URL input found"}
    field.fill(target_url)
    title = _find_text(page, ("title", "name", "subject"), exclude=field)
    if title:
        title.fill(anchor_text)
    desc = _find_text(page, ("desc", "summary", "about", "comment", "text"), exclude=field)
    if desc:
        desc.fill(description or f"{anchor_text} - {target_url}")
    btn = find_submit(page, near=field, names=names)
    if btn is not None:
        btn.click()
    else:
        field.press("Enter")
    page.wait_for_timeout(3500)
    page.screenshot(path=proof_path)
    body = ""
    try:
        body = page.inner_text("body").lower()
    except Exception:
        pass
    if "captcha" in body or "verify you are human" in body:
        return {"status": "gated", "notes": "captcha shown after submit", "gate": gate_from_reason("captcha on the form", site.name).model_dump()}
    urls = visible_urls(page)
    if any(target_url.rstrip("/") in u for u in urls) or target_url.rstrip("/").lower() in body:
        return {"status": "placed", "live_url": page.url, "notes": "target URL visible on result page"}
    if any(w in body for w in ("thank", "submitted", "pending", "review", "approved", "success")):
        return {"status": "placed", "live_url": page.url, "notes": "submission acknowledged; listing may await moderation"}
    return {"status": "failed", "notes": "submitted but target URL not found on result page"}
