"""What the free plan includes, and what it does not.

Ten links, of which one may be on a DA 90+ site, and neither Facebook albums nor GitHub Pages. The shape is
deliberate: ten is enough to see the thing work on real sites and get real links out of it, the single strong
site is enough to feel the difference between a DA 30 link and a DA 90 one, and the two methods held back are the
two that produce an asset rather than a submission -- a page that ranks and sends traffic, and a followed link on
a site the customer owns.

Every decision here is a pure function of numbers already known, so the wording a person reads and the rule that
stops the build are the same thing and cannot drift apart. Nothing here reads a file or calls anything.

This runs on the customer's own machine, which means a determined person can edit it. That is true of the whole
free tier and is not worth pretending otherwise: the limit is there to be honest with people who are honest,
and what a subscription really buys -- the full library, the engine, indexing, monitoring -- is not in this file
at all and cannot be unlocked by editing it.
"""
from __future__ import annotations

FREE_LINKS = 10
FREE_STRONG = 1            # how many of those ten may be on a DA 90+ site
STRONG_DA = 90

# The two methods that build an asset rather than submit a link. Both are subscription-only.
PAID_ONLY = {
    "get_traffic": "Facebook albums",
    "traffic_plan": "Facebook albums",
    "facebook_sign_in": "Facebook albums",
    "publish_page": "GitHub Pages links",
    "github_connect": "GitHub Pages links",
}


def is_strong(da: int) -> bool:
    return int(da or 0) >= STRONG_DA


def left(placed: int, strong_placed: int) -> dict:
    """What is left of the free plan, in the two numbers that matter."""
    return {"links": max(0, FREE_LINKS - int(placed or 0)),
            "strong": max(0, FREE_STRONG - int(strong_placed or 0))}


def check(placed: int, strong_placed: int, da: int = 0, paid: bool = False) -> dict:
    """May this link be built on the free plan?

    The strong-site rule is checked first. Refusing on the total when they still have links left but have used
    their one strong site tells them the wrong thing, and they would come back with another DA 90 site."""
    if paid:
        return {"allowed": True, "reason": "", "say": "", "detail": [], "remaining": None}
    room = left(placed, strong_placed)

    if is_strong(da) and room["strong"] <= 0:
        return {"allowed": False, "reason": "strong_used", "remaining": room,
                "say": f"The free plan includes one link on a site this strong, and it has been used.",
                "detail": [f"You have {room['links']} free link{'s' if room['links'] != 1 else ''} left, and they "
                           f"can go on any of the other sites.",
                           "A subscription lifts the limit on the strong ones, which is where most of the value "
                           "in a link is.",
                           "Ask me to show the upgrade and I will."]}

    if room["links"] <= 0:
        return {"allowed": False, "reason": "used_up", "remaining": room,
                "say": f"That is all {FREE_LINKS} free links used.",
                "detail": ["Everything built so far is yours and stays live; nothing is taken away.",
                           "A subscription opens the full library, the engine, indexing and monitoring.",
                           "Ask me to show the upgrade and I will."]}

    after = {"links": room["links"] - 1, "strong": room["strong"] - (1 if is_strong(da) else 0)}
    return {"allowed": True, "reason": "", "remaining": after, "say": "", "detail": []}


def tool(name: str, paid: bool = False) -> dict:
    """May this tool be used on the free plan? Some are not a matter of how many, but of which."""
    if paid or name not in PAID_ONLY:
        return {"allowed": True, "reason": "", "say": "", "detail": []}
    what = PAID_ONLY[name]
    return {"allowed": False, "reason": "paid_only", "what": what,
            "say": f"{what} are part of a subscription, not the free plan.",
            "detail": ["The free plan builds links on the bundled sites, in your own browser, with no account "
                       "and no key.",
                       f"{what} build something that keeps working for you afterwards, which is why they sit "
                       f"with the paid library.",
                       "Ask me to show the upgrade and I will."]}


def summary(placed: int, strong_placed: int, paid: bool = False) -> dict:
    """What to tell someone who asks what they are on."""
    if paid:
        return {"plan": "subscription", "say": "You are on a subscription: the whole library and every method."}
    room = left(placed, strong_placed)
    return {"plan": "free", "links_left": room["links"], "strong_left": room["strong"],
            "say": f"Free plan: {room['links']} of {FREE_LINKS} links left"
                   + (", including one on a DA 90+ site." if room["strong"] else ", and the strong one is used."),
            "detail": [f"The free plan is {FREE_LINKS} links, one of which may be on a DA 90+ site.",
                       "Facebook albums and GitHub Pages links are part of a subscription."]}
