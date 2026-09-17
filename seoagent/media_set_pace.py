"""How fast albums may go up, and when a Page has carried enough of them.

Two numbers, and they answer different questions.

*One a week* is the guide's own cadence and the operator confirmed it on 2026-09-18. It is what stops a Page
gaining albums faster than a real page would: Facebook's spam systems and Google's quality systems both notice
bursts of thin, near-duplicate content, and a restricted Page takes every album on it down at once.

*Four to a Page* is a lifetime ceiling, not a rolling one. At one a week a Page reaches it in a month, and the
next album starts a fresh Page. Keeping each Page's footprint small means a Page that does get restricted costs
four albums rather than forty. It also paces Page creation itself to about one a month per account, which matters
because making Pages in a burst is its own flag.

A Page that is full is not waiting for anything, so no date is offered for it: the answer is another Page, which
is made for them. Signing in to Facebook is the only thing the customer ever does by hand.

Both numbers are settings. They are judgements about risk, and whoever carries the risk should be able to change
them without waiting for a deploy.

Nothing here talks to Facebook. It decides when and where, and says so in words a person can act on.
"""
from __future__ import annotations

import os
import time
from typing import Optional

DAY = 86400.0
WEEK = 7 * DAY
PER_WEEK = 1               # the guide's own cadence
PER_PAGE = 4               # albums one Page ever carries; at one a week, a month's worth
MIN_GAP_HOURS = 20         # a floor under the cadence, so a raised weekly cap never means two in an afternoon


def _num(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name) or default)
    except ValueError:
        return default


def per_week() -> int:
    return max(1, int(_num("MEDIA_SETS_PER_WEEK", PER_WEEK)))


def per_page() -> int:
    return max(1, int(_num("MEDIA_SETS_PER_PAGE", PER_PAGE)))


def min_gap() -> float:
    return _num("MEDIA_SET_MIN_GAP_HOURS", MIN_GAP_HOURS) * 3600


def cadence() -> float:
    """The spacing one album a week works out to, used to keep a rollover Page on the same rhythm."""
    return WEEK / per_week()


def _recent(built: list[float], now: float) -> list[float]:
    return sorted(t for t in built if now - t < WEEK)


def wait_for(built: list[float], now: Optional[float] = None) -> dict:
    """When the next album may go up, on timing alone.

    This is the website's rhythm rather than one Page's capacity, so it is asked of every album the customer has
    published for a site, across all of their Pages. Rolling onto a fresh Page must not become a way to publish
    four in an afternoon."""
    now = time.time() if now is None else float(now)
    recent = _recent(built, now)
    cap = per_week()

    gap_at = (max(built) + min_gap()) if built else now
    week_at = (recent[0] + WEEK) if len(recent) >= cap else now
    at = max(gap_at, week_at)

    if at <= now:
        return {"allowed": True, "rule": "", "needs_new_page": False, "next_at": now,
                "built_this_week": len(recent), "on_this_page": len(built), "say": "", "detail": []}

    # Both rules are worked out and the later one decides. Checking them in order would let whichever fired first
    # hide the other, and the weekly cap would never be reached because the spacing rule always answers sooner.
    if week_at >= gap_at:
        return {"allowed": False, "rule": "per_week", "needs_new_page": False, "next_at": at,
                "built_this_week": len(recent), "on_this_page": len(built),
                "say": f"There {'has' if len(recent) == 1 else 'have'} been {len(recent)} "
                       f"album{'s' if len(recent) != 1 else ''} this week, which is the pace. The next can go up "
                       f"{_ago(at - now)} from now.",
                "detail": [f"It is {cap} a week, which is what the method's own guide advises.",
                           "Hand me more pages any time — I will queue them and tell you when each one lands."]}
    return {"allowed": False, "rule": "too_soon", "needs_new_page": False, "next_at": at,
            "built_this_week": len(recent), "on_this_page": len(built),
            "say": f"The last album went up {_ago(now - max(built))} ago. I will put the next one up "
                   f"{_ago(at - now)} from now.",
            "detail": ["Albums arriving minutes apart is the pattern Facebook restricts Pages for.",
                       "Spacing them out is what keeps the Page, and every album on it, alive."]}


def check(built: list[float], now: Optional[float] = None) -> dict:
    """May another album go up on this Page right now, and if not, when — or whether the answer is a new Page."""
    now = time.time() if now is None else float(now)
    recent = _recent(built, now)
    ceiling = per_page()

    if len(built) >= ceiling:
        # Waiting does not fix this one, so no date is offered. The next album belongs on a Page of its own.
        return {"allowed": False, "rule": "page_full", "needs_new_page": True, "next_at": 0.0,
                "built_this_week": len(recent), "on_this_page": len(built),
                "say": f"This Page is carrying {len(built)} albums, which is as many as I put on one. The next one "
                       f"needs a new Page.",
                "detail": [f"A Page holds {ceiling} albums here. Spreading them means a Page that does get "
                           f"restricted costs you four, not everything you have built.",
                           "I will make a second Page for this website and carry on from there."]}

    return wait_for(built, now)


def next_slot(built: list[float], now: Optional[float] = None) -> float:
    """The earliest moment another album may go up on this Page. A full Page never comes free."""
    now = time.time() if now is None else float(now)
    d = check(built, now)
    if d["needs_new_page"]:
        return float("inf")
    return now if d["allowed"] else float(d["next_at"])


def choose(pages: dict, now: Optional[float] = None) -> dict:
    """Which of this website's Pages the next album goes on, and when.

    `pages` maps Page address to the times albums went up on it — one website's Pages, in the order they were
    made. The oldest Page with room is used until it is full, rather than spreading albums thinly over all of
    them: finishing one Page and moving on is what keeps each Page's footprint small and predictable."""
    now = time.time() if now is None else float(now)
    everything = [t for history in pages.values() for t in history]
    # A new Page does not reset the customer's rhythm: the website still gains one album a week, wherever it sits.
    floor = (max(everything) + cadence()) if everything else now

    for url, history in pages.items():
        if len(history) < per_page():
            at = max(next_slot(list(history), now), floor, now)
            left = per_page() - len(history) - 1
            return {"page_url": url, "at": at, "new_page": False, "room_after": left,
                    "say": ("Building this one now." if at <= now else f"This one goes up {_ago(at - now)} from now."),
                    "detail": ([f"{left} more will fit on this Page before it needs a second one."] if left
                               else ["This is the last one this Page takes; the next needs a new Page."])}

    return {"page_url": "", "at": max(now, floor), "new_page": True, "room_after": per_page() - 1,
            "say": "This one starts a new Page — the ones you have are full.",
            "detail": [f"A Page holds {per_page()} albums here, about a month's worth at one a week.",
                       "I make the new Page myself; you will not have to do anything."]}


def plan(urls: list[str], built: Optional[list[float]] = None, now: Optional[float] = None,
         pages: Optional[dict] = None) -> list[dict]:
    """When each of these pages gets its album, and which Page it lands on.

    Someone handing over ten URLs should be told when each one lands, not told no. The schedule accounts for what
    their Pages have already published, and rolls onto a fresh Page each time one fills up."""
    now = time.time() if now is None else float(now)
    if pages is None:
        pages = {"": list(built or [])}
    state = {url: list(history) for url, history in pages.items()}
    out: list[dict] = []
    extra = 0
    cursor = now                       # the clock moves with the schedule, or every slot is judged from today
    for i, url in enumerate(urls):
        pick = choose(state, cursor)
        at = max(pick["at"], cursor)
        cursor = at
        key = pick["page_url"]
        if pick["new_page"]:
            extra += 1
            key = f"new page {extra}"   # a Page they have yet to make, named so the plan can be read aloud
            state[key] = []
        out.append({"url": url, "at": at, "position": i + 1, "page_url": pick["page_url"],
                    "page": key or pick["page_url"], "new_page": pick["new_page"],
                    "say": ("Building this one now." if at <= now else f"This one goes up {_ago(at - now)} from now.")})
        state[key].append(at)
    return out


def pages_needed(count: int, pages: Optional[dict] = None) -> int:
    """How many Pages the customer still has to make to fit this many albums."""
    room = sum(max(0, per_page() - len(h)) for h in (pages or {}).values())
    short = max(0, count - room)
    return -(-short // per_page())     # ceiling division: whatever will not fit needs a Page of its own


def _ago(seconds: float) -> str:
    """A span said the way a person would say it, not in seconds."""
    s = max(0.0, float(seconds))
    if s < 90 * 60:
        return f"{max(1, round(s / 60))} minutes"
    if s < 36 * 3600:
        return f"{max(1, round(s / 3600))} hours"
    return f"{max(1, round(s / DAY))} days"
