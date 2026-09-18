"""The page that gets published on GitHub Pages, decided offline.

This method differs from the Facebook media set in one way that changes everything about the writing: the link
here is **followed**. It sits on a real domain, it passes ranking strength, and it is therefore held to the
standard a real page is held to. Two failure modes are worth naming because both are tempting and both are dead
ends:

A copy of the customer's own page is duplicate content. Google will not rank it, usually will not index it, and
republishing someone's page is something GitHub will act on. An original page about their page is the thing that
works, which is why this module writes one.

A thin page -- a title and a link -- is not indexed at all on a fresh github.io, so the link is never seen and
the work is wasted. The page has to say something, so it does: what the thing is, who it is for, what is in it.

Everything the page loads, it carries. No fonts, no scripts, no analytics: faster, nothing that breaks when a
third party moves a file, and nothing to explain to a customer reading their own source.
"""
from __future__ import annotations

import html as _html
import re
import time
import unicodedata
from typing import Iterable, Optional

from . import media_set

SLUG_MAX = 60
PAGES_HOST = ".github.io"


def slug(text: str) -> str:
    """Lowercase, hyphenated, no accents. This becomes a path, so it has to survive being typed and shared."""
    plain = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")[:SLUG_MAX].strip("-")


def repo_name(domain: str, taken: Optional[Iterable[str]] = None) -> str:
    """One repo per website, named after the website.

    A repo per keyword would leave a row of thin one-page sites under their account, which is the pattern that
    gets GitHub accounts suspended -- and their account is the asset, exactly as their Facebook Page was."""
    host = (domain or "").strip().lower().split("//")[-1].split("/")[0].removeprefix("www.")
    base = slug(host.split(".")[0]) or "site"
    taken = list(taken or [])
    if base not in taken:
        return base
    n = 2
    while f"{base}-{n}" in taken:
        n += 1
    return f"{base}-{n}"


def path_for(keyword: str) -> str:
    """Where the file lives in the repo. A directory with an index.html gives a clean address with no .html on it."""
    return f"{slug(keyword)}/index.html"


def site_url(owner: str, repo: str, keyword: str) -> str:
    """Where GitHub actually serves it. Not the repo address -- that is a code listing, not the page."""
    return f"https://{owner}{PAGES_HOST}/{repo}/{slug(keyword)}/"


def is_pages_url(url: str) -> bool:
    """A published page, told apart from the repository that holds it."""
    u = (url or "").strip().lower()
    return PAGES_HOST in u.split("/")[2] if u.startswith("http") and len(u.split("/")) > 2 else False


def _para(text: str) -> str:
    return f"<p>{_html.escape(text)}</p>"


def html(target_url: str, keyword: str, brand: str = "", kind: str = "article", benefit: str = "",
         audience: str = "", steps: Optional[list[str]] = None, why: str = "", built_at: Optional[float] = None) -> str:
    """The page itself.

    The keyword is the anchor text and the link is followed, because a followed link is what this method is for.
    Their address also appears as plain text: a reader sees where they are going, and the snippet shows it."""
    kw = " ".join((keyword or "").split())
    if not kw:
        raise ValueError("a page needs one keyword; it becomes the title, and the title is the ranking signal")
    url = (target_url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("the address needs its https:// or the published link will not work")

    name = (brand or "").strip() or kw[:1].upper() + kw[1:]
    who = audience.strip() or "anyone comparing their options"
    because = why.strip() or f"finding a straightforward {kw} took longer than it should"
    article = kind == "article"
    gain = benefit.strip() or ("see the whole picture in one place" if article else "do it in seconds")
    points = [s.strip() for s in (steps or []) if s.strip()] or (
        ["Start with the quick answer if you are in a hurry.",
         "Compare the options side by side.",
         "Read the full write-up on the one you like."] if article else
        ["Open it and make your choices.",
         "Get your result straight away.",
         "Nothing is stored and nothing is sent anywhere."])

    title = media_set.title(kw, name if name.lower() != kw.lower() else "")
    link = f'<a href="{_html.escape(url, quote=True)}">{_html.escape(kw)}</a>'
    if article:
        opening = (f"{_html.escape(name)} is a {link} written for {_html.escape(who)}. It lets you "
                   f"{_html.escape(gain)}, with the real numbers rather than a list of links to somewhere else.")
        standing = (f"It is free to read, there is no sign-up, and nothing sits behind an email form. Every figure "
                    f"in it comes from the specifications and the listed price, so any of it can be checked.")
    else:
        opening = (f"{_html.escape(name)} is a free {link} for {_html.escape(who)}. It lets you "
                   f"{_html.escape(gain)}, with no sign-up and no watermark on what comes out.")
        standing = (f"It runs in the browser on a phone as well as a desktop, and there is no account to make "
                    f"before it will work.")
    closing = f"It exists because {because}."

    listed = "\n".join(f"      <li>{_html.escape(p)}</li>" for p in points[:4])
    when = time.strftime("%Y-%m-%d", time.localtime(built_at or time.time()))
    summary = f"{name}: what it does, who it is for, and where to find it."

    # The heading says what the page is about; the link inside the first paragraph is the one that counts, so
    # that paragraph is assembled as markup and everything dropped into it is escaped as it is built. The address
    # is repeated as plain text at the end, which is what a reader checks before they click.
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{_html.escape(title)}</title>
    <meta name="description" content="{_html.escape(summary)}">
    <style>
      :root {{ color-scheme: light dark; }}
      body {{ max-width: 38rem; margin: 0 auto; padding: 2.5rem 1.25rem;
             font: 1rem/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
      h1 {{ font-size: 1.6rem; line-height: 1.25; margin: 0 0 1rem; }}
      h2 {{ font-size: 1.1rem; margin: 2rem 0 .5rem; }}
      ul {{ padding-left: 1.2rem; }}
      footer {{ margin-top: 2.5rem; font-size: .9rem; opacity: .75; }}
    </style>
  </head>
  <body>
    <h1>{_html.escape(title)}</h1>
    <p>{opening}</p>
    <h2>What is in it</h2>
    <ul>
{listed}
    </ul>
    {_para(standing)}
    {_para(closing)}
    <footer>
      <p>Find it at <a href="{_html.escape(url, quote=True)}">{_html.escape(url)}</a></p>
      <p>Last checked {when}.</p>
    </footer>
  </body>
</html>
"""


def index_html(brand: str, entries: list[dict], built_at: Optional[float] = None) -> str:
    """The repo's front page, listing everything published in it.

    A page nothing links to is crawled late or not at all. This is what leads a crawler to each one, and what a
    person sees if they open the site's root."""
    name = (brand or "").strip() or "Notes"
    rows = "\n".join(
        f'      <li><a href="{_html.escape(e.get("path", ""), quote=True)}">{_html.escape(e.get("title") or e.get("keyword", ""))}</a></li>'
        for e in entries)
    when = time.strftime("%Y-%m-%d", time.localtime(built_at or time.time()))
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{_html.escape(name)}</title>
    <meta name="description" content="Write-ups published by {_html.escape(name)}.">
    <style>
      :root {{ color-scheme: light dark; }}
      body {{ max-width: 38rem; margin: 0 auto; padding: 2.5rem 1.25rem;
             font: 1rem/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
      h1 {{ font-size: 1.6rem; margin: 0 0 1rem; }}
      ul {{ padding-left: 1.2rem; }}
      footer {{ margin-top: 2.5rem; font-size: .9rem; opacity: .75; }}
    </style>
  </head>
  <body>
    <h1>{_html.escape(name)}</h1>
    <ul>
{rows}
    </ul>
    <footer><p>Updated {when}.</p></footer>
  </body>
</html>
"""
