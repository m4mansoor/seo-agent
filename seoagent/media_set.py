"""Facebook media set: a public album that ranks, and sends the searcher on to the customer's page.

This is the one method in the library bought for traffic rather than authority. A new domain has no history and
may wait months for Google to trust it; facebook.com is trusted already and its public album pages are crawled
without a login. A keyword-titled album whose description opens with the customer's URL is, in effect, a small
landing page on a domain that already ranks.

The link it carries is nofollow and Facebook rewrites it through its own redirector, so nothing here passes
authority and the module never pretends it does. What it reports is the asset: published, public to a logged-out
visitor, and submitted for indexing. Whether it then ranks is answered days later by the monitor, not at build
time.

Method from the operator's own guide (Facebook Media Set SEO, 2026). Everything decided here is a pure function;
the browser work lives in the executor and the playbook.
"""
from __future__ import annotations

import os
import re
from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

MIN_IMAGES = 3
MAX_IMAGES = 8
TITLE_MAX = 60           # longer is cut off in a search result, which is the whole shop window
NAME_MAX = 80            # a file name longer than this is unusable in the upload dialog
ALBUM_RE = re.compile(r"^a\.\d{5,}$")


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name) or default)
    except ValueError:
        return default


def min_images() -> int:
    return _int("MEDIA_SET_MIN_IMAGES", MIN_IMAGES)


def max_images() -> int:
    return _int("MEDIA_SET_MAX_IMAGES", MAX_IMAGES)


# ---------------------------------------------------------------- the album address

def is_album_url(url: str) -> bool:
    """True only for the album's own address. A single photo opened from the album has a /photo/ path and an
    fbid, looks almost identical in the address bar, and is the wrong page to promote or to track."""
    try:
        p = urlparse((url or "").strip())
    except Exception:
        return False
    if "facebook.com" not in p.netloc.lower():
        return False
    if not p.path.rstrip("/").endswith("/media/set"):
        return False
    sets = parse_qs(p.query).get("set") or []
    return bool(sets) and bool(ALBUM_RE.match(sets[0]))


def clean_album_url(url: str) -> str:
    """The address without Facebook's click-tracking. `__cft__` and `__tn__` are per-visit and per-surface, so a
    tracked copy is a different string every time it is shared and useless as the identity of the asset."""
    p = urlparse((url or "").strip())
    q = parse_qs(p.query)
    keep = {k: v[0] for k, v in q.items() if k in ("set", "type")}
    keep.setdefault("type", "3")
    path = p.path if p.path.endswith("/") else p.path + "/"
    return urlunparse((p.scheme or "https", p.netloc, path, "", urlencode(keep), ""))


# ---------------------------------------------------------------- the description

def title(keyword: str, benefit: str = "") -> str:
    """A title a person would click, not a keyword list. Cut to what a search result shows."""
    kw = " ".join((keyword or "").split())
    if not kw:
        raise ValueError("a media set needs one keyword; it becomes the title and the title is the ranking signal")
    t = kw[:1].upper() + kw[1:]
    if benefit and len(t) + len(benefit) + 3 <= TITLE_MAX:
        t = f"{t} — {benefit}"
    return t[:TITLE_MAX].rstrip(" —-")


def description(target_url: str, tool_name: str, keyword: str, benefit: str = "", audience: str = "",
                steps: Optional[list[str]] = None, why: str = "", kind: str = "tool") -> str:
    """The album body. The URL is the first line because that line is what the search snippet shows above the
    fold, and it is repeated at the end as the call to action.

    `kind` matters more than it looks. The boilerplate that suits a tool -- no sign-up, no watermark, everything
    happens in your browser -- is nonsense on a review article, and a description that describes the wrong thing
    reads as spam to the person who clicked and tells Google the page is not what it claims. "tool" for something
    you operate, "article" for something you read."""
    kw = " ".join((keyword or "").split())
    if not kw:
        raise ValueError("a media set needs one keyword; without it there is nothing to rank for")
    url = (target_url or "").strip()
    name = tool_name.strip() or kw[:1].upper() + kw[1:]
    audience = audience.strip() or "anyone who needs it"
    why = why.strip() or f"finding a straightforward {kw} took longer than it should"
    article = kind == "article"

    benefit = benefit.strip() or ("see the whole picture in one place" if article else "do it in seconds")
    steps = [s.strip() for s in (steps or []) if s.strip()] or (
        ["start with the quick answer if you are in a hurry", "compare the options side by side",
         "read the full write-up on the one you like"] if article else
        ["open the link above", "make your choices", "get your result"])
    how = "\n".join(f"{i}. {s[:1].upper() + s[1:]}." for i, s in enumerate(steps[:4], 1))

    if article:
        opener = f"{name} is a {kw} written for {audience}. It lets you {benefit}, with the real numbers rather than a list of links."
        middle = (f"Who it is for: {audience}, and anyone tired of comparisons that never say which one to buy. "
                  f"It is free to read, there is no sign-up, and nothing is hidden behind an email form.")
        closer = (f"We wrote it because {why}. Every figure in it comes from the specifications and the listed price, "
                  f"so you can check any of it yourself.")
    else:
        opener = f"{name} is a free {kw} built for {audience}. It lets you {benefit}, with no sign-up and no watermark."
        middle = (f"Who uses it: {audience}, and anyone who needs a quick answer without installing software. It works "
                  f"on desktop and on mobile, and there is no account to create before you can use it.")
        closer = (f"We built {name} because {why}. Everything happens in your browser, so nothing you enter is stored "
                  f"or sent anywhere after you close the page.")

    body = f"""{url}

{opener}

What is in it:
{how}

{middle}

{closer}

Read it here: {url}""" if article else f"""{url}

{opener}

How it works:
{how}

{middle}

{closer}

Try it now: {url}"""
    return _pad_to_minimum(body, kw, name, article)


def _pad_to_minimum(body: str, kw: str, name: str, article: bool = False) -> str:
    """The guide's floor is 150 words; a thin description gets the wrong snippet and ranks for nothing. Rather
    than repeat the keyword to make weight, add a sentence that is actually about the thing."""
    extra = ([
        "It is one page, it loads fast, and it says which one to buy rather than leaving you to guess.",
        "No email form, no pop-up, and nothing is held back for a newsletter.",
        "If a price or a specification is out of date, tell us and we will correct it.",
    ] if article else [
        "It is one page, it loads fast, and it does the one job it says it does.",
        "There is no queue, no watermark on the result and no limit on how often you use it.",
        "If something does not work the way you expect, tell us and we will fix it.",
    ])
    tail = "\n\nRead it here:" if article else "\n\nTry it now:"
    i = 0
    while len(body.split()) < 155 and i < len(extra):
        body = body.replace(tail, f"\n\n{extra[i]}{tail}", 1)
        i += 1
    return body


# ---------------------------------------------------------------- the images

def slugify(text: str, limit: int = NAME_MAX) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:limit].rstrip("-")


def image_names(keyword: str, count: int = 5, ext: str = "png") -> list[str]:
    """File names Google can read. The name is a ranking signal of its own and IMG_4821.jpg says nothing, so each
    file is named for the keyword plus what that particular image shows."""
    count = max(min_images(), min(count, max_images()))
    base = slugify(keyword, limit=NAME_MAX - 16) or "media-set"
    shots = ["", "screenshot", "example", "how-it-works", "result", "on-mobile", "settings", "output"]
    out, seen = [], set()
    for i in range(count):
        suffix = shots[i] if i < len(shots) else f"view-{i}"
        stem = f"{base}-{suffix}".strip("-") if suffix else base
        stem = stem[: NAME_MAX - len(ext) - 1].rstrip("-")
        n, name = 1, f"{stem}.{ext}"
        while name in seen:
            n += 1
            name = f"{stem}-{n}.{ext}"
        seen.add(name)
        out.append(name)
    return out


def shot_plan(target_url: str, keyword: str, count: int = 5) -> list[dict]:
    """What to capture and under what name. The customer's own page is the source: a screenshot of the thing
    being promoted is honest, needs no design work, and is what a searcher wants to see before clicking."""
    names = image_names(keyword, count)
    recipes = [
        {"what": "the page as it first loads", "viewport": (1280, 800), "full_page": False},
        {"what": "the whole page", "viewport": (1280, 800), "full_page": True},
        {"what": "the page on a phone", "viewport": (390, 844), "full_page": False},
        {"what": "the page after scrolling to the main control", "viewport": (1280, 800), "full_page": False, "scroll": 600},
        {"what": "the page lower down", "viewport": (1280, 800), "full_page": False, "scroll": 1400},
        {"what": "a wide view", "viewport": (1600, 900), "full_page": False},
        {"what": "a tablet view", "viewport": (820, 1180), "full_page": False},
        {"what": "the foot of the page", "viewport": (1280, 800), "full_page": False, "scroll": 2400},
    ]
    return [{"file": n, "url": target_url, "caption": _caption(keyword, r["what"]), **r}
            for n, r in zip(names, recipes)]


def _caption(keyword: str, what: str) -> str:
    return f"{keyword[:1].upper() + keyword[1:]} — {what}."


# ---------------------------------------------------------------- pictures the person gives us

MAGIC = {b"\x89PNG\r\n\x1a\n": "png", b"\xff\xd8\xff": "jpg", b"GIF87a": "gif", b"GIF89a": "gif",
         b"RIFF": "webp", b"<svg": "svg", b"<?xml": "svg"}


def image_kind(path: str) -> Optional[str]:
    """What the file actually is, read from its first bytes. An extension is a claim, not evidence, and an album
    upload that silently drops a renamed PDF wastes the person's time at the worst moment."""
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError:
        return None
    for magic, kind in MAGIC.items():
        if head.startswith(magic):
            return kind
    return None


def use_images(paths: list[str], keyword: str, out_dir: str) -> list[dict]:
    """Take the person's own pictures over our screenshots, but rename them for the keyword just the same.

    Their graphics are better than a screenshot whenever they have them. What cannot survive is IMG_4821.jpg:
    the file name is one of the three things a search engine reads off an album, so it is renamed here rather
    than left to chance."""
    import shutil
    os.makedirs(out_dir, exist_ok=True)
    base = slugify(keyword, limit=NAME_MAX - 16) or "media-set"
    shots = ["", "screenshot", "example", "how-it-works", "result", "on-mobile", "settings", "output"]
    out: list[dict] = []
    for i, src in enumerate(paths):
        if not os.path.isfile(src):
            out.append({"source": src, "ok": False, "error": f"could not find {os.path.basename(src)}"})
            continue
        kind = image_kind(src)
        if not kind:
            out.append({"source": src, "ok": False,
                        "error": f"{os.path.basename(src)} is not an image Facebook will take"})
            continue
        suffix = shots[i] if i < len(shots) else f"view-{i}"
        stem = (f"{base}-{suffix}".strip("-") if suffix else base)[: NAME_MAX - len(kind) - 1].rstrip("-")
        name = f"{stem}.{kind}"
        n = 1
        while any(o.get("file") == name for o in out):
            n += 1
            name = f"{stem}-{n}.{kind}"
        dest = os.path.join(out_dir, name)
        try:
            shutil.copyfile(src, dest)
            out.append({"source": src, "file": name, "path": dest, "ok": True,
                        "caption": _caption(keyword, shots[i] if i < len(shots) and shots[i] else "the page")})
        except OSError as e:
            out.append({"source": src, "ok": False, "error": f"could not copy: {type(e).__name__}"})
    return out


def enough(images: list[dict]) -> bool:
    """An album with one picture looks abandoned and gives a search engine almost nothing to read."""
    return sum(1 for i in images if i.get("ok")) >= min_images()


# ---------------------------------------------------------------- is it really behind a wall?

BLOCKED_PHRASES = ("you must log in to continue", "content isn't available", "content is not available",
                   "this page isn't available", "sorry, this content isn't available")


def readable_logged_out(text: str, expect: list[str]) -> dict:
    """Can a signed-out visitor read the thing, which is the only test that matters for search.

    Judge by whether the content is there, never by whether the words "log in" appear. Facebook puts a login
    banner on every page a signed-out visitor sees, so treating that as a wall would send a customer back to fix
    settings that were already correct. A wall hides the content; a banner sits next to it."""
    if not expect:
        raise ValueError("say what to look for, or this cannot tell a wall from a banner")
    low = (text or "").lower()
    found = [e for e in expect if e.lower() in low]
    missing = [e for e in expect if e.lower() not in low]
    hard = next((p for p in BLOCKED_PHRASES if p in low), "")
    readable = bool(found) and not missing and not hard
    why = (f"the page says {hard!r}" if hard else
           f"could not find {missing}" if missing else
           "the content is there, and the login banner next to it is on every signed-out page")
    return {"readable": readable, "found": found, "missing": missing, "why": why}


# ---------------------------------------------------------------- what we report

def outcome(album_url: str, target_url: str, keyword: str, public: bool, indexed: Optional[bool] = None) -> dict:
    """What the album is worth, said plainly. It is finished when a logged-out visitor can read it, because a
    login wall is what stops Google too. Ranking is not claimed here; it is checked later."""
    url = clean_album_url(album_url) if is_album_url(album_url) else album_url
    if not public:
        return {
            "status": "unverified", "kind": "traffic", "dofollow": False, "live_url": url,
            "say": "The album is up but it still asks for a login, so no one can read it yet.",
            "detail": [
                "Opened it logged out and got a sign-in prompt. Search engines see the same wall, so it cannot rank.",
                "Check three settings on the page: published, no country restriction, and age set to anyone.",
                "Then set the album's own audience to Public — the globe icon, not a lock.",
            ],
        }
    detail = [
        f"The album is public and readable without signing in, which is how a search engine reads it too.",
        f"It targets **{keyword}** and your link is the first line of the description, where the search snippet shows it.",
        "The link is a mention rather than a followed link, so it passes no ranking strength. What it sends you is visitors.",
        "Submitted for indexing. It usually appears in search within a few days; ranking takes longer.",
    ]
    if indexed is True:
        detail.append("It is already showing in Google.")
    elif indexed is False:
        detail.append("Not in Google yet. That is normal this early; it is worth checking again in a week.")
    return {
        "status": "placed", "kind": "traffic", "dofollow": False, "live_url": url,
        "say": f"Your album is live on Facebook and aiming to rank for “{keyword}”, sending traffic to your page.",
        "detail": detail,
    }


# ---------------------------------------------------------------- the pictures

def capture(plan: list[dict], out_dir: str, page_factory=None) -> list[dict]:
    """Take the screenshots the plan asks for, named as the plan names them.

    The customer's own page is the subject, so there is nothing to design and nothing to invent: what a searcher
    sees in the album is the thing they are about to click through to. `page_factory` is injected so this is
    testable without a browser."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    made: list[dict] = []
    if page_factory is None:
        from contextlib import contextmanager

        from .agent.browser import session

        @contextmanager
        def page_factory(viewport):                      # noqa: F811 - the real one, when nobody injected a fake
            with session(headless=True, viewport=viewport) as p:
                yield p

    for shot in plan:
        path = os.path.join(out_dir, shot["file"])
        try:
            with page_factory(tuple(shot.get("viewport", (1280, 800)))) as page:
                page.goto(shot["url"], wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1200)
                if shot.get("scroll"):
                    page.evaluate(f"window.scrollTo(0, {int(shot['scroll'])})")
                    page.wait_for_timeout(500)
                page.screenshot(path=path, full_page=bool(shot.get("full_page")))
            made.append({**shot, "path": path, "ok": os.path.exists(path)})
        except Exception as e:
            made.append({**shot, "path": path, "ok": False, "error": f"{type(e).__name__}: {str(e)[:120]}"})
    return made
