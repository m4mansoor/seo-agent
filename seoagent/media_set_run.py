"""Building the album itself, unattended.

Everything else in the media set method is decidable offline. This is the part that has to touch Facebook: switch
into the Page, open the album form, type the title and the description, set the audience, upload the pictures with
a caption each, publish, and read back the album's own address.

Two rules run through it. Type, never fill: `fill()` sets a value without firing the events a scripted editor
listens for, so a box looks full and posts empty, which is the single most expensive mistake this codebase has
made. And report the address only when it is the album's own -- a single photo opened from an album has a nearly
identical address and is the wrong page to promote, track or submit.

The page object is passed in, so the whole sequence is testable against a fake and the browser stays in one place.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Optional

from . import media_set
from .agent.browser import dismiss_dialogs, profile_dir, signed_in_session, signed_in_to
from .media_set import clean_album_url, is_album_url, min_images  # noqa: F401  (re-exported for tests)

# Facebook renames its controls often, so every one of these is a list and the first that exists wins. When none
# of them is found the build stops and says which control it wanted, rather than clicking something at random.
CREATE_ALBUM = ["button:Create album", "button:Create Album", "link:Create album",
                "button:Add photos/video", "button:Create Album", "link:Albums"]
TITLE_FIELDS = ["label:Album name", "label:Album title", "label:Name"]
DESC_FIELDS = ["label:Description", "label:Say something about this album", "label:Add a description"]
AUDIENCE = ["button:Audience", "button:Privacy", "button:Edit audience"]
PUBLIC_CHOICE = ["Public", "Everyone"]
ADD_PHOTOS = ["button:Add photos", "button:Add Photos", "button:Upload photos"]
PUBLISH = ["button:Post", "button:Publish", "button:Create"]
SWITCH = ["button:Switch Now", "button:Switch"]


def _try(page: Any, names: list[str]) -> Optional[Any]:
    """The first of these controls that is actually on the page, or None."""
    for n in names:
        role, _, label = n.partition(":")
        try:
            thing = (page.get_by_label(label) if role == "label"
                     else page.get_by_role(role, name=re.compile(rf"^{re.escape(label)}$", re.I)))
            thing = getattr(thing, "first", thing)
            if thing.is_visible(timeout=2500):
                return thing
        except Exception:
            continue
    return None


def _type_into(page: Any, thing: Any, text: str) -> None:
    """Type it. A scripted editor validates on keystrokes, and a value set behind its back posts empty."""
    try:
        thing.click()
    except Exception:
        pass
    _wait(page, 300)
    try:
        thing.type(text, delay=18)
    except TypeError:
        thing.type(text)


def _wait(page: Any, ms: int) -> None:
    try:
        page.wait_for_timeout(ms)
    except Exception:
        pass


def _clear(page: Any) -> list[str]:
    """Close anything covering the page. A welcome dialog is invisible to a selector and fatal to a click."""
    try:
        return dismiss_dialogs(page)
    except Exception:
        return []


def _shot(page: Any, name: str) -> None:
    try:
        page.screenshot(path=f"/tmp/media-set-{name}.png")
    except Exception:
        pass


def build_album(page: Any, page_url: str, title: str, description: str, images: list[dict],
                publish: bool = True, on_step: Optional[Callable[[str], None]] = None) -> dict:
    """Build one album on a Page already signed into. Returns what happened, never raises.

    Written against the screen Facebook actually serves, which is not the one the method was written for.
    **There is no album description field any more.** Create album offers an album name, a caption per photo, an
    audience and Post -- nothing else. So the description, whose first line carries the customer's address, goes
    into the first photo's caption: still text on the album page, still what a searcher reads in the snippet, and
    the only field left that can hold it.

    The photos go up before anything else, because the name and caption boxes do not exist until they do."""
    say = on_step or (lambda s: None)
    base = {"kind": "traffic", "dofollow": False, "stopped_before_publishing": not publish}
    usable = [i for i in images if i.get("path")]
    if len(usable) < min_images():
        return {**base, "ok": False, "step": "pictures",
                "error": f"an album needs at least {min_images()} pictures; {len(usable)} were ready"}

    step = "opening the album form"
    try:
        say(step)
        page.goto("https://www.facebook.com/media/set/create", wait_until="domcontentloaded")
        _wait(page, 7000)
        _clear(page)

        step = "uploading the pictures"
        say(step)
        try:
            page.set_input_files("input[type=file]", [i["path"] for i in usable])
        except Exception as e:
            return {**base, "ok": False, "step": step, "error": f"the upload was refused: {type(e).__name__}"}
        _wait(page, 14000)
        _clear(page)
        _shot(page, "uploaded")

        step = "the album name"
        say(step)
        name = _try(page, TITLE_FIELDS)
        if not name:
            return {**base, "ok": False, "step": step,
                    "error": "the album name box never appeared, so the photos probably did not attach"}
        _type_into(page, name, title)
        _wait(page, 1000)

        step = "the description"
        say(step)
        boxes = _caption_boxes(page)
        if not boxes:
            return {**base, "ok": False, "step": step, "error": "no caption box appeared for the photos"}
        # On the create screen every box belongs to a photo; the album's own description does not exist here and
        # is written afterwards through Edit album, which is the only place it appears.
        step = "the captions"
        say(step)
        for box, img in zip(boxes, usable):
            cap = (img.get("caption") or "").strip()
            if cap:
                _type_into(page, box, cap)
                _wait(page, 500)

        step = "the audience"
        say(step)
        out_audience = _ensure_public(page)

        if not publish:
            _shot(page, "before-publish")
            return {**base, "ok": True, "step": "stopped before publishing", "audience": out_audience,
                    "note": "everything was filled in; nothing was made public"}

        step = "publishing"
        say(step)
        post = _try(page, PUBLISH)
        if not post:
            return {**base, "ok": False, "step": step, "error": "could not find the button that publishes it"}
        post.click()
        _wait(page, 15000)
        _shot(page, "published")

        step = "reading the album address"
        say(step)
        url = getattr(page, "url", "")
        album = clean_album_url(url) if is_album_url(url) else ""
        return {**base, "ok": True, "album_url": album, "audience": out_audience, "step": "done",
                "note": ("" if album else
                         "published, but the address on screen is not the album's own; it is read back from the "
                         "Albums tab instead")}
    except Exception as e:
        return {**base, "ok": False, "step": step, "error": f"{type(e).__name__}: {str(e)[:160]}"}


def set_album_description(page: Any, album_url: str, description: str) -> dict:
    """Put the description in the album's own box, which only exists on Edit album.

    Create offers an album name and one caption per photo and no album description at all. Edit album offers six
    boxes for five photos: the first is the album's own, and it is the only one that renders under the title on
    the album page -- the line that carries the customer's address and the one a searcher reads. A description
    left in a photo caption is invisible to everyone who does not open that individual photo."""
    try:
        page.goto(album_url, wait_until="domcontentloaded")
        _wait(page, 8000)
        _clear(page)
        menu = _try(page, ["button:More options for album"])
        if not menu:
            return {"ok": False, "error": "could not open the album's options"}
        menu.click()
        _wait(page, 2500)
        edit = _try(page, ["button:Edit album", "menuitem:Edit album", "link:Edit album"])
        if edit:
            edit.click()
        else:
            try:
                page.get_by_text(re.compile(r"^Edit album$", re.I)).first.click()
            except Exception:
                return {"ok": False, "error": "could not find Edit album"}
        _wait(page, 5000)
        _clear(page)
        boxes = _caption_boxes(page)
        if not boxes:
            return {"ok": False, "error": "no description box appeared on the edit screen"}
        _type_into(page, boxes[0], description)
        _wait(page, 2000)
        save = _try(page, ["button:Save", "button:Done", "button:Post"])
        if not save:
            return {"ok": False, "error": "could not find the button that saves it"}
        save.click()
        _wait(page, 9000)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {str(e)[:140]}"}


def _caption_boxes(page: Any) -> list:
    """One box per photo, in the order the photos appear. Facebook labels every one of them the same, so they can
    only be told apart by position."""
    try:
        boxes = page.get_by_label("Description (optional)")
        n = boxes.count()
        return [boxes.nth(i) for i in range(n)]
    except Exception:
        return []


def _ensure_public(page: Any) -> str:
    """An album anyone can read is the entire point; behind a login it ranks for nothing. New albums default to
    Public, so this confirms rather than changes, and says which it found."""
    for name in ("Public", "Audience", "Privacy"):
        thing = _try(page, [f"button:{name}"])
        if not thing:
            continue
        try:
            label = (thing.inner_text() or "").strip()
        except Exception:
            label = name
        if "public" in label.lower():
            return "public"
        thing.click()
        _wait(page, 2000)
        pick = _try(page, ["button:Public", "menuitem:Public", "radio:Public"])
        if pick:
            pick.click()
            _wait(page, 1500)
            return "public"
    return "unknown"


# ---------------------------------------------------------------- one command, one address back

def get_traffic(target_url: str, keyword: str, brand: str = "", kind: str = "article",
                images: Optional[list[str]] = None, profile: str = "facebook", use_page: str = "",
                pages_by_site: Optional[dict] = None, may_create_page: bool = False,
                publish: bool = True, on_step: Optional[Callable[[str], None]] = None) -> dict:
    """Everything, from a URL and a phrase to the album's address.

    The only thing it ever asks for is a signed-in browser, and only the first time: the profile is kept, so the
    second album and every one after it runs without a word. Anything it cannot do it reports; it never guesses
    and it never claims an album that is not there."""
    import os

    say = on_step or (lambda s: None)
    out: dict = {"target_url": target_url, "keyword": keyword, "kind": "traffic", "dofollow": False}
    if not (target_url or "").strip() or not (keyword or "").strip():
        return {**out, "ok": False, "error": "a page address and one search phrase are both needed"}

    # Nothing below works without a session, and a session is the one thing a person has to give us.
    if not os.path.isdir(os.path.join(profile_dir(profile), "Default")):
        return {**out, "ok": False, "needs_sign_in": True,
                "say": "I need you signed in to Facebook once. After that I never ask again.",
                "detail": ["I am opening a Facebook window. Sign in there, including any code it asks for.",
                           "The signed-in profile is kept on this machine, so every album after this one is built "
                           "without interrupting you."]}

    say("preparing the words and the pictures")
    try:
        text = media_set.description(target_url, brand or "", keyword, kind=kind)
    except ValueError as e:
        return {**out, "ok": False, "error": str(e)}
    title = media_set.title(keyword)
    folder = os.path.join(os.environ.get("LINKENGINE_RUNS") or os.path.join(os.path.expanduser("~"), ".linkengine", "runs"),
                          "media-set", media_set.slugify(keyword, 40) or "album")

    # Taken before the Facebook window opens: Playwright's sync API cannot be nested, and these need no Facebook.
    say("taking the pictures")
    shots = (media_set.use_images(images, keyword, folder) if images
             else media_set.capture(media_set.shot_plan(target_url, keyword, count=5), folder))
    ready = [s for s in shots if s.get("ok")]
    if not media_set.enough(ready):
        why = next((s.get("error") for s in shots if s.get("error")), "")
        return {**out, "ok": False, "step": "pictures",
                "error": f"only {len(ready)} usable pictures; an album needs {min_images()}"
                         + (f" ({why})" if why else "")}

    with signed_in_session(profile, headless=False, viewport=(1360, 950)) as page:
        # The cookie only exists once the page is on facebook.com; asking a blank tab always says "not signed in".
        page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
        _wait(page, 4000)
        if not signed_in_to(page, "facebook.com"):
            return {**out, "ok": False, "needs_sign_in": True,
                    "say": "The Facebook session has expired. One sign-in and I carry on."}

        say("finding the Page")
        domain = (target_url or "").split("//")[-1].split("/")[0].removeprefix("www.")
        if use_page:
            page_url = use_page
        else:
            pick = choose_page(list_pages(page), domain, remembered=pages_by_site)
            if pick["ask"] and not (pick["create"] and may_create_page):
                # Which Page a site belongs on is theirs to decide, and a Page made by mistake is a public thing
                # under their name. Hand the question back rather than guessing.
                return {**out, "ok": False, "needs_answer": "page", "create_offered": pick["create"],
                        "options": [{"name": o["name"], "page_url": o["url"]} for o in pick["options"]],
                        "say": pick.get("say", ""), "detail": pick.get("detail", [])}
            page_url = pick["page_url"]
            if not page_url:
                say("making the Page")
                made = create_page(page, brand or media_set.title(keyword), target_url)
                if not made.get("ok"):
                    return {**out, "ok": False, "step": "the Page",
                            "error": made.get("error", "could not make a Page")}
                page_url = made["page_url"]
        out["page_url"] = page_url
        out["site"] = domain

        say("building the album")
        built = build_album(page, page_url, title, text, ready, publish=publish, on_step=say)
        out.update({k: v for k, v in built.items() if k not in ("kind", "dofollow")})
        if not built.get("ok"):
            return {**out, "ok": False}

        album = built.get("album_url") or find_album(page, page_url, title)
        if album and publish:
            say("putting your address on the album")
            out["description_set"] = set_album_description(page, album, text)
        if not album:
            return {**out, "ok": False, "step": "the address",
                    "error": "the album was published but its own address could not be read back"}
        out["album_url"] = album

        say("checking a stranger can read it")
        out["public"] = readable_to_a_stranger(page, album, [title[:30]])

    say("asking search engines to look at it")
    out["indexing"] = submit_for_indexing(album, keyword)

    return {**out, "ok": True, "title": title, "description": text,
            "say": f"Your album is live and aiming at “{keyword}”. It sends visitors to your page.",
            "detail": ["This one is for traffic. The link inside it passes no ranking strength; what it sends you "
                       "is people who found the album in search.",
                       "It usually appears in search within days. Ranking takes longer."]}


def choose_page(pages: list[dict], domain: str, remembered: Optional[dict] = None) -> dict:
    """Which Page this site's albums belong on.

    A Page is the customer's asset and every album for one site belongs on the same one: a Page per album leaves a
    row of near-empty Pages, which is weaker and is the pattern Facebook restricts. Someone running several
    businesses may keep a Page each, and only they know which site goes with which -- so with more than one, ask,
    and remember the answer so it is asked once per site rather than once per album."""
    remembered = remembered or {}
    known = remembered.get(domain, "")
    urls = {p.get("url", "") for p in pages}
    if known and known in urls:
        return {"page_url": known, "ask": False, "create": False, "options": pages}
    if len(pages) == 1:
        return {"page_url": pages[0].get("url", ""), "ask": False, "create": False, "options": pages}
    if not pages:
        return {"page_url": "", "ask": True, "create": True, "options": [],
                "say": "You have no Facebook Page yet. Shall I make one for this site?",
                "detail": ["Albums on a personal profile are not picked up by search at all, so this needs a Page.",
                           "It is a one-off: every album for this site afterwards goes on the same Page."]}
    # More than one, and nothing remembered. Put the likeliest first, but it stays their choice.
    label = (domain or "").split(".")[0].lower()
    ranked = sorted(pages, key=lambda p: 0 if label and label in (p.get("name", "")).lower() else 1)
    return {"page_url": "", "ask": True, "create": False, "options": ranked,
            "say": f"Which of your Pages should the album for {domain} go on?",
            "detail": ["Every album for this site will go on the Page you pick, so it builds up in one place.",
                       "I will remember it and not ask again for this site."]}


def albums_url(page_url: str) -> str:
    """Where this Page's albums live.

    A Page that has not claimed a username is addressed as profile.php?id=N, and a path cannot be bolted onto a
    query string -- doing so produces an address Facebook simply does not serve, and the album form is never
    found. Those take &sk=photos_albums; a Page with a username takes the path."""
    u = (page_url or "").strip().rstrip("/")
    if "profile.php" in u and "id=" in u:
        pid = u.split("id=")[-1].split("&")[0]
        base = u.split("profile.php")[0] + "profile.php"
        return f"{base}?id={pid}&sk=photos_albums"
    return f"{u}/photos_albums"


def pick_page(links: list[str], managed: list[str], prefer: str = "") -> Optional[str]:
    """Which of the addresses on the Pages screen is actually a Page this account manages.

    That screen links to the person's own profile as well, and an album on a personal profile is not indexed at
    all -- the whole job would be wasted on a page nobody can find."""
    if prefer:
        return prefer
    ids = {m.strip() for m in managed if m and m.strip()}
    for href in links:
        pid = href.split("id=")[-1].split("&")[0] if "id=" in href else ""
        if pid and pid in ids:
            return href.split("&")[0]
    return None


def list_pages(page: Any) -> list[dict]:
    """Every Page this account manages, with its name. The screen links to the person's own profile too, and an
    album on a personal profile is not indexed at all, so the name matters as much as the address."""
    try:
        page.goto("https://www.facebook.com/pages/?category=your_pages", wait_until="domcontentloaded")
        _wait(page, 7000)
        _clear(page)
        found = page.evaluate(r"""() => {
          const out = [];
          for (const a of document.querySelectorAll('a[href*="profile.php?id="]')) {
            const name = (a.innerText || a.getAttribute('aria-label') || '').trim().split('\n')[0];
            const href = a.href.split('&')[0];
            if (/profile\.php\?id=\d+/.test(href)) out.push({name, url: href});
          }
          const seen = new Set();
          return out.filter(p => !seen.has(p.url) && seen.add(p.url));
        }""")
        return [p for p in (found or []) if p.get("name")]
    except Exception:
        return []


def find_page(page: Any, prefer: str = "") -> Optional[str]:
    """One Page address, for callers that do not need the choice. Prefer `list_pages` plus `choose_page`."""
    if prefer:
        return prefer
    pages = list_pages(page)
    return pages[0]["url"] if len(pages) == 1 else None


def create_page(page: Any, name: str, site: str) -> dict:
    """Make the Page. This is the person's own account and their own instruction; it is still a public thing under
    their name, so whoever calls this is expected to have asked first."""
    step = "opening the form"
    try:
        page.goto("https://www.facebook.com/pages/creation/", wait_until="domcontentloaded")
        _wait(page, 7000)
        host = site.split("//")[-1].split("/")[0].removeprefix("www.")
        for label, value in (("Page name", name[:50]), ("Category", "Website"),
                             ("Bio", f"Honest, evidence-based comparisons at {host}.")):
            step = label
            field = _try(page, [f"label:{label}"])
            if not field:
                return {"ok": False, "error": f"could not find the {label} field"}
            _type_into(page, field, value)
            _wait(page, 1200)
            if label == "Category":
                try:
                    page.keyboard.press("ArrowDown"); _wait(page, 400); page.keyboard.press("Enter")
                except Exception:
                    pass
        step = "creating it"
        btn = _try(page, ["button:Create Page"])
        if not btn:
            return {"ok": False, "error": "could not find Create Page"}
        btn.click()
        _wait(page, 10000)
        url = find_page(page)
        return {"ok": bool(url), "page_url": url} if url else {"ok": False, "error": "the Page was not created"}
    except Exception as e:
        return {"ok": False, "step": step, "error": f"{type(e).__name__}: {str(e)[:140]}"}


def find_album(page: Any, page_url: str, title: str) -> Optional[str]:
    """Open the album we just made and read its own address. Publishing often leaves you on the Page rather than
    the album, and the Page's address is not the thing to promote."""
    try:
        page.goto(albums_url(page_url), wait_until="domcontentloaded")
        _wait(page, 6000)
        links = page.evaluate("""() => [...document.querySelectorAll('a[href*="/media/set"]')].map(a => a.href)""")
        for href in links:
            if is_album_url(href):
                return clean_album_url(href)
    except Exception:
        pass
    return None


def readable_to_a_stranger(page: Any, url: str, expect: list[str]) -> bool:
    """What a signed-out visitor sees, which is the only test that decides whether this can rank at all."""
    try:
        ctx = page.context.browser.new_context()
        p2 = ctx.new_page()
        p2.goto(url, wait_until="domcontentloaded")
        p2.wait_for_timeout(4000)
        ok = media_set.readable_logged_out(p2.inner_text("body"), expect)["readable"]
        ctx.close()
        return ok
    except Exception:
        return False


def submit_for_indexing(album_url: str, keyword: str = "") -> dict:
    """Ask for the album to be crawled.

    Being found and being ranked are different things, and only the first is ours to influence. This shortens
    days to hours when it is configured and says so plainly when it is not; it never implies the second."""
    try:
        from . import indexer
    except Exception:
        return {"submitted": False, "why": "the indexer is not available on this engine"}
    try:
        if not indexer.configured():
            return {"submitted": False, "offer": True,
                    "say": "Want me to push this into the index? It is found in hours rather than days.",
                    "detail": ["Search engines will find it on their own eventually; this asks them to look now.",
                               "It is a paid extra and it is the one thing that shortens the wait."],
                    "why": "indexing is not switched on for this account"}
        name = f"media set: {keyword or album_url}"[:60]
        return {"submitted": True, "project": indexer.submit(name, [album_url])}
    except Exception as e:
        return {"submitted": False, "why": f"{type(e).__name__}: {str(e)[:120]}"}
