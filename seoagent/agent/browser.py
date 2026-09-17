"""Playwright helpers shared by playbooks: session handling and field finding heuristics."""
from __future__ import annotations

import os
import re
from contextlib import contextmanager
from typing import Iterator, Optional

from playwright.sync_api import Locator, Page, TimeoutError as PWTimeout, sync_playwright

URL_HINTS = ("url", "link", "http", "website", "web address", "address", "long")
SUBMIT_HINTS = ("shorten", "submit", "add", "create", "go", "generate", "make", "save", "post", "send")
COOKIE_HINTS = ("accept", "agree", "got it", "allow", "ok", "consent", "i understand")


@contextmanager
def session(headless: bool = True, viewport: tuple[int, int] = (1366, 900)) -> Iterator[Page]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(
            viewport={"width": viewport[0], "height": viewport[1]},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            locale="en-US",
        )
        page = ctx.new_page()
        page.set_default_timeout(15000)
        try:
            yield page
        finally:
            ctx.close()
            browser.close()


DEFAULT_PROFILE = os.path.join(os.path.expanduser("~"), ".linkengine", "profiles")


def profile_dir(name: str = "default") -> str:
    return os.environ.get("LINKENGINE_PROFILES") or os.path.join(DEFAULT_PROFILE, name)


@contextmanager
def signed_in_session(name: str = "default", headless: bool = False, viewport: tuple[int, int] = (1300, 900),
                      url: str = "") -> Iterator[Page]:
    """A browser the person can sign into, and that stays signed in.

    Two things here are not cosmetic. It runs **real Chrome**, not Playwright's bundled Chromium, and it turns off
    the flag that makes the page see `navigator.webdriver === true`. Google refuses to complete a sign-in in a
    browser advertising itself as automated -- deliberately, to stop phishing -- and since some sites route their
    own verification through Google, a person can end up unable to sign into their own account at all. Nothing
    here defeats a security check: the human types their own password into their own account. It stops the browser
    falsely announcing itself as a robot while they do it.

    The profile is kept on disk, so this is asked for once and every later build starts already signed in."""
    d = profile_dir(name)
    os.makedirs(d, exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            d,
            channel="chrome",
            headless=headless,
            viewport={"width": viewport[0], "height": viewport[1]},
            locale="en-US",
            args=["--disable-blink-features=AutomationControlled",
                  "--no-default-browser-check", "--no-first-run",
                  f"--window-size={viewport[0] + 40},{viewport[1] + 120}"],
            ignore_default_args=["--enable-automation"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_default_timeout(30000)
        if url:
            try:
                page.goto(url, wait_until="domcontentloaded")
            except Exception:
                pass
        try:
            yield page
        finally:
            ctx.close()


def signed_in_to(page: Page, host: str) -> bool:
    """Whether the profile holds a live session for this host, read from the cookie the site itself sets."""
    marker = {"facebook.com": r"c_user=\d+", "x.com": r"auth_token=", "linkedin.com": r"li_at=",
              "reddit.com": r"reddit_session=", "medium.com": r"sid="}.get(host, r"session")
    try:
        return bool(page.evaluate(f"() => !!document.cookie.match(/{marker}/)"))
    except Exception:
        return False


def quoted_names(texts: list[str]) -> list[str]:
    """Button and field names the guide quotes, e.g. Click "Shorten URL"."""
    out: list[str] = []
    for t in texts:
        for m in re.findall(r'[“"]([^”"]{2,40})[”"]', t):
            m = m.strip()
            if m and m.lower() not in (x.lower() for x in out):
                out.append(m)
    return out


def dismiss_banners(page: Page) -> None:
    for hint in COOKIE_HINTS:
        try:
            btn = page.get_by_role("button", name=re.compile(rf"^\s*{re.escape(hint)}", re.I)).first
            if btn.is_visible(timeout=800):
                btn.click(timeout=2000)
                page.wait_for_timeout(300)
                return
        except Exception:
            continue


# First-run and welcome dialogs sit on top of everything and swallow the click you meant to make. They are not
# consent banners -- the wording is different and so is the button -- so they need their own pass.
DIALOG_BUTTONS = ("Use Page", "Not now", "Not Now", "Skip", "Skip for now", "Maybe later", "Got it", "OK",
                  "Okay", "Done", "Close", "Continue", "Dismiss", "No thanks")


def dismiss_dialogs(page: Page, rounds: int = 3) -> list[str]:
    """Close whatever modal is covering the page, and say what was closed.

    A welcome dialog looks harmless in a screenshot and is fatal to automation: every control behind it is
    present in the DOM, visible to a query, and impossible to click. Returns the buttons it pressed so a failure
    later can be read against what was in the way."""
    closed: list[str] = []
    for _ in range(rounds):
        hit = False
        for name in DIALOG_BUTTONS:
            try:
                btn = page.get_by_role("button", name=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)).first
                if btn.is_visible(timeout=600):
                    btn.click(timeout=2500)
                    closed.append(name)
                    page.wait_for_timeout(1200)
                    hit = True
                    break
            except Exception:
                continue
        if not hit:
            try:                                  # a dialog with only an X, or one that closes on Escape
                x = page.locator("div[role=dialog] [aria-label='Close']").first
                if x.is_visible(timeout=600):
                    x.click(timeout=2000); closed.append("Close"); page.wait_for_timeout(1000); continue
            except Exception:
                pass
            break
    return closed


def _attr_blob(loc: Locator) -> str:
    try:
        return loc.evaluate(
            "e => [e.type, e.name, e.id, e.placeholder, e.getAttribute('aria-label'), e.title, "
            "(e.labels && e.labels[0] ? e.labels[0].innerText : '')].join(' ').toLowerCase()"
        )
    except Exception:
        return ""


def find_url_input(page: Page) -> Optional[Locator]:
    """The most likely field for a URL: typed url first, then hinted names, then the largest visible text input."""
    typed = page.locator("input[type=url]")
    for i in range(typed.count()):
        if typed.nth(i).is_visible():
            return typed.nth(i)
    cands = page.locator("input[type=text], input:not([type]), textarea")
    scored: list[tuple[int, Locator]] = []
    for i in range(min(cands.count(), 40)):
        loc = cands.nth(i)
        try:
            if not loc.is_visible():
                continue
        except Exception:
            continue
        blob = _attr_blob(loc)
        s = sum(3 for h in URL_HINTS if h in blob)
        if "search" in blob or "email" in blob or "password" in blob:
            s -= 5
        try:
            box = loc.bounding_box()
            if box:
                s += min(int(box["width"] // 100), 4)
        except Exception:
            pass
        scored.append((s, loc))
    scored.sort(key=lambda t: -t[0])
    return scored[0][1] if scored and scored[0][0] > 0 else (scored[0][1] if scored else None)


def find_submit(page: Page, near: Optional[Locator] = None, names: Optional[list[str]] = None) -> Optional[Locator]:
    """A submit control: the input's own form submit first (it is the one wired to the field), then the guide's
    quoted button name, then generic verbs. Guide names come second because sites often repeat them on
    decorative call-to-action links elsewhere on the page."""
    if near is not None:
        try:
            form = near.locator("xpath=ancestor::form[1]")
            if form.count():
                subs = form.locator("button[type=submit], input[type=submit], button:not([type]), input[type=image], button[type=button]")
                ranked: list[tuple[int, Locator]] = []
                wanted = [n.lower() for n in (names or [])]
                for i in range(min(subs.count(), 8)):
                    sub = subs.nth(i)
                    if not sub.is_visible(timeout=300):
                        continue
                    try:
                        label = sub.evaluate("e => (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().toLowerCase()")
                    except Exception:
                        label = ""
                    rank = 0
                    if label:
                        rank = 1
                        if any(h in label for h in SUBMIT_HINTS) or any(w in label for w in wanted):
                            rank = 2
                    ranked.append((rank, sub))
                if ranked:
                    ranked.sort(key=lambda t: -t[0])
                    return ranked[0][1]
        except Exception:
            pass
    for name in names or []:
        for role in ("button", "link"):
            try:
                b = page.get_by_role(role, name=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)).first
                if b.is_visible(timeout=500):
                    return b
            except Exception:
                pass
    for hint in SUBMIT_HINTS:
        try:
            b = page.get_by_role("button", name=re.compile(hint, re.I)).first
            if b.is_visible(timeout=300):
                return b
        except Exception:
            pass
    try:
        b = page.locator("input[type=submit]").first
        if b.is_visible(timeout=300):
            return b
    except Exception:
        pass
    return None


def visible_urls(page: Page) -> list[str]:
    """Every http(s) URL currently shown as a link href, input value or bare text on the page."""
    try:
        return page.evaluate(
            """() => {
              const out = new Set();
              for (const a of document.querySelectorAll('a[href]')) out.add(a.href);
              for (const i of document.querySelectorAll('input, textarea')) { const v = (i.value||'').trim(); if (/^https?:\\/\\//i.test(v)) out.add(v); }
              const re = /https?:\\/\\/[^\\s"'<>]+/g; const m = document.body.innerText.match(re) || [];
              for (const x of m) out.add(x.replace(/[).,]+$/, ''));
              return [...out];
            }"""
        )
    except Exception:
        return []


def bot_gate(page: Page, check_empty: bool = True) -> Optional[str]:
    """Why an automated browser cannot proceed here, or None: a challenge page, a captcha widget, or nothing rendered.
    The empty-page signal only means anything on first load; after a submit a short confirmation page is normal."""
    try:
        title = (page.title() or "").lower()
        if "just a moment" in title or "attention required" in title or "access denied" in title:
            return "bot challenge page"
        body = (page.inner_text("body") or "")[:2000].lower()
        if "you have been blocked" in body or "verify you are human" in body and "cloudflare" in body:
            return "blocked by the site's firewall"
        has = page.evaluate(
            "() => ({turn: !!document.querySelector('input[name=cf-turnstile-response], .cf-turnstile, iframe[src*=challenges]'),"
            " recap: !!document.querySelector('.g-recaptcha, iframe[src*=recaptcha], .h-captcha, iframe[src*=hcaptcha]'),"
            " empty: (document.body ? document.body.innerText.trim().length : 0) < 20})"
        )
        if has["turn"]:
            return "Cloudflare Turnstile on the form"
        if has["recap"]:
            return "captcha on the form"
        if has["empty"] and check_empty:
            return "page rendered empty for an automated browser"
    except Exception:
        return None
    return None


def safe_goto(page: Page, url: str) -> bool:
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1200)
        return True
    except PWTimeout:
        return False
    except Exception:
        return False
