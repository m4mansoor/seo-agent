"""SEO Agent MCP server.

Free mode, no account: the bundled free sites with their methods, and local tools that build on login-free sites in
your own browser, verify a live page and keep a results log. Subscribed: after `activate` with the key from your
purchase, every tool of the hosted engine is proxied (1,245 sites, planner, model executor, gates, monitoring)."""
from __future__ import annotations

import asyncio
import json
import os
import re
from contextlib import AsyncExitStack
from typing import Any, Optional

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from . import local
from .models import JobResult, Site

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
HOST = os.environ.get("SEOAGENT_HOST", "https://mcp.seoagent.dev").rstrip("/")
BUY_URL = os.environ.get("SEOAGENT_BUY_URL", f"{HOST}/buy")
PRICE_YEARLY_USD = int(os.environ.get("SEOAGENT_PRICE_YEARLY_USD", "97"))
PRICE_MONTHLY_USD = int(os.environ.get("SEOAGENT_PRICE_MONTHLY_USD", "27"))
CONNECT_TIMEOUT = 20


def _load(name: str):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


SITES: list[dict] = _load("free-sites.json")
PLAYBOOKS: dict[str, str] = _load("playbooks.json")
TEASERS: list[dict] = _load("teasers.json")          # the highest-DA locked sites: names and numbers, no methods
STATS: dict = _load("library_stats.json")
BY_SLUG = {s["slug"]: s for s in SITES}
LOCKED = {t["slug"]: t for t in TEASERS}
N_FREE = len(SITES)

RULES = """Rules for every link: use the target URL and anchor text exactly as given; never place the same link twice on a site;
follow the steps in order, the step marked placement is where the link goes; use the exact button and field names quoted;
at a captcha, code or login ask the user in this chat rather than working around it; after placing, open the public page
and confirm the hyperlink, anchor and whether it is nofollow; report the live URL; finish with log_link."""


# ------------------------------------------------------------------ where the key comes from

def _personal_key(url: str) -> str:
    m = re.search(r"/u/(le_[A-Za-z0-9_\-]+)/mcp", url or "")
    return m.group(1) if m else ""


def credentials() -> tuple[str, str]:
    """(remote MCP URL, bearer key). Env wins, then the saved activation. Either a bare key or a personal link works."""
    env_url, env_key = os.environ.get("SEOAGENT_URL", "").strip(), os.environ.get("SEOAGENT_API_KEY", "").strip()
    if env_url or env_key:
        return env_url or f"{HOST}/mcp", env_key or _personal_key(env_url)
    cfg = local.read_config()
    url = cfg.get("url") or f"{HOST}/mcp"
    return url, cfg.get("api_key") or _personal_key(url)


def hosted() -> bool:
    return bool(credentials()[1])


# ------------------------------------------------------------------ free mode tools

def _matches(s: dict, q: str, min_da: int, dofollow_only: bool, method: str) -> bool:
    if (s.get("da") or 0) < min_da or (dofollow_only and not s["dofollow"]) or (method and s["method"] != method):
        return False
    return not q or q in " ".join([s["name"], s["domain"], s["slug"], s["method_label"]]).lower()


def search_sites(query: str = "", min_da: int = 0, dofollow_only: bool = False, method: str = "", limit: int = 25) -> dict:
    """Free matches with their methods, then what the full library holds for the same search: up to five locked
    examples by name and DA, and the counts. The locked part is how the assistant knows when to offer the upgrade."""
    q = query.lower().strip()
    free = []
    for s in SITES:
        if not _matches(s, q, min_da, dofollow_only, method):
            continue
        free.append({k: s[k] for k in ("slug", "name", "domain", "url", "da", "dofollow", "method", "method_label", "tier", "referring_domains", "organic_traffic")})
        free[-1]["auto_build"] = s["tier"] == "A" and s["method"] in ("url_shortener", "bookmark_submit")
    locked = [{**{k: t[k] for k in ("slug", "name", "domain", "da", "dofollow", "method_label", "tier", "referring_domains")}, "locked": True}
              for t in TEASERS if _matches(t, q, min_da, dofollow_only, method)]
    band = "da_90_plus" if min_da >= 90 else "da_70_plus" if min_da >= 70 else "da_50_plus" if min_da >= 50 else None
    out = {"free": free[:limit], "free_total": len(free), "locked_examples": locked[:5],
           "full_library": {"sites": STATS["sites"], "reachable": STATS["reachable"], **STATS["by_da"]}, "upgrade": _upgrade_hint()}
    if len(free) < limit and (locked or band):
        more = STATS["by_da"].get(band) if band else STATS["reachable"] - N_FREE
        out["ask_the_user"] = (f"The free list has {len(free)} site{'s' if len(free) != 1 else ''} for this search; the full library has about {more} "
                               f"{'at DA ' + str(min_da) + '+ ' if min_da else ''}(for example {', '.join(t['name'] + ' DA ' + str(t['da']) for t in locked[:3]) or 'many more'}). "
                               f"Offer the subscription: ${PRICE_YEARLY_USD} a year or ${PRICE_MONTHLY_USD} a month.")
    return out


def _locked_result(slug: str) -> dict:
    t = LOCKED.get(slug)
    if t:
        return {"locked": True, "site": t, "error": f"{t['name']} (DA {t['da']}) is in the full library; its method unlocks with a subscription", "upgrade": _upgrade_hint(),
                "ask_the_user": f"{t['name']} is DA {t['da']} and needs the subscription: ${PRICE_YEARLY_USD} a year or ${PRICE_MONTHLY_USD} a month. Shall I show the free sites instead?"}
    return {"error": f"{slug!r} is not in the free list; the full {STATS['sites']:,}-site library needs a subscription", "upgrade": _upgrade_hint()}


def get_method(slug: str) -> dict:
    s = BY_SLUG.get(slug.strip().lower())
    if not s:
        return _locked_result(slug.strip().lower())
    return {**s, "playbook": PLAYBOOKS.get(s["method"], ""), "rules": RULES}


def library_summary() -> dict:
    return {"mode": "free", "sites": N_FREE, "dofollow": sum(1 for s in SITES if s["dofollow"]),
            "da_range": [min(s["da"] for s in SITES), max(s["da"] for s in SITES)],
            "subscription": {"sites": STATS["sites"], "reachable": STATS["reachable"], "dofollow": STATS["dofollow"], **STATS["by_da"], "plans": _plans()}}


def _plans() -> dict:
    return {"yearly": {"price_usd": PRICE_YEARLY_USD, "per": "year", "url": f"{BUY_URL}?plan=yearly"},
            "monthly": {"price_usd": PRICE_MONTHLY_USD, "per": "month", "url": f"{BUY_URL}?plan=monthly"}}


def _upgrade_hint() -> dict:
    return {"plans": _plans(), "how": "Subscribe at either URL, copy the key shown on the success page, then say: activate <key>."}


def build_link(slug: str, target_url: str, anchor_text: str = "", headless: bool = True, description: str = "") -> dict:
    """Build one link in a local browser on a login-free site. Elsewhere returns the method to follow."""
    s = BY_SLUG.get(slug.strip().lower())
    if not s:
        return _locked_result(slug.strip().lower())
    res = local.Results()
    if res.placed_on(s["slug"], target_url):
        return {"status": "skipped", "notes": f"a link to {target_url} is already placed on {s['name']}"}
    from .agent.executor import can_auto_build, run_job
    site = Site.from_record(s)
    if not can_auto_build(site):
        return {"status": "manual", "reason": f"{s['method_label']} on {s['name']} needs an account; follow the method in your browser, then verify_link and log_link",
                **get_method(slug)}
    r = run_job(site, target_url, anchor_text, headless=headless, description=description)
    res.save(r)
    out = r.model_dump()
    if r.status == "gated" and r.gate:
        out["ask_the_user"] = (f"{r.gate['message']} Options: " + "; ".join(o["label"] for o in r.gate["options"]) +
                               ". Re-run build_link with headless=false to clear it in a visible window, or skip the site.")
    out["links_placed"] = res.placed()
    return out


def verify_link(live_url: str, target_url: str, anchor_text: str = "") -> dict:
    from .verify import check_live
    return check_live(live_url, target_url, anchor_text).model_dump()


def log_link(slug: str, target_url: str, live_url: str, anchor_text: str = "", status: str = "placed", notes: str = "") -> dict:
    if status not in ("placed", "unverified", "manual", "failed"):
        return {"error": "status must be placed, unverified, manual or failed"}
    r = JobResult(slug=slug, target_url=target_url, anchor_text=anchor_text, status=status, live_url=live_url or None, notes=notes)
    rid = local.Results().save(r)
    return {"id": rid, **r.model_dump()}


def list_results(limit: int = 100) -> dict:
    res = local.Results()
    return {"placed": res.placed(), "free_sites": N_FREE, "results": res.all(limit)}


def account() -> dict:
    res = local.Results()
    return {"plan": "free", "links_placed": res.placed(), "free_sites": N_FREE,
            "note": f"Free mode builds on the {N_FREE} bundled sites in your own browser. A subscription adds {STATS['sites']:,} sites, the campaign planner, "
                    "building on account-based sites, gates with connected services, monitoring, reports and a dashboard.",
            "upgrade": _upgrade_hint()}


def upgrade() -> dict:
    p = _plans()
    return {"plans": p,
            "ask_the_user": f"Every one of 1,245 sites and the whole engine: ${PRICE_YEARLY_USD} a year ({p['yearly']['url']}) or "
                            f"${PRICE_MONTHLY_USD} a month ({p['monthly']['url']}). After paying, copy the key from the success page and tell me: activate <key>."}


# Some work cannot be sent to a server, and should not be. Anything that drives a browser runs on this machine:
# it is the person's own browser, their own signed-in accounts and their own password, none of which should ever
# be handed to us. Everything else -- the library, the planner, the monitor, anything that costs money -- comes
# from the engine, because that is where the data and the billing live.
LOCAL_ALWAYS = {"get_traffic", "traffic_plan", "build_link", "verify_link", "log_link", "list_results",
                "facebook_sign_in"}


def runs_here(name: str) -> bool:
    """True when this tool must run on the person's machine whatever their plan says."""
    return name in LOCAL_ALWAYS


def facebook_sign_in(wait_minutes: int = 30) -> dict:
    """Open a real browser and wait while the person signs in to Facebook. Asked once, ever."""
    import time
    from .agent.browser import signed_in_session, signed_in_to
    deadline = time.time() + max(1, min(wait_minutes, 60)) * 60
    with signed_in_session("facebook", headless=False, url="https://www.facebook.com/") as page:
        try:
            page.bring_to_front()
        except Exception:
            pass
        while time.time() < deadline:
            if signed_in_to(page, "facebook.com"):
                page.wait_for_timeout(3000)
                return {"signed_in": True,
                        "say": "You are signed in. I will not need to ask again on this machine.",
                        "detail": ["The signed-in browser is kept here on your computer.",
                                   "Your password was never seen by me and never leaves this machine."]}
            page.wait_for_timeout(2000)
    return {"signed_in": False, "say": "Nobody signed in, so I stopped waiting.",
            "detail": ["Say the word and I will open the window again."]}


def traffic_plan(urls: str, page_url: str = "") -> dict:
    """Plan albums for several pages: when each lands and which Facebook Page it lands on. One a week, and a Page
    carries four before the next album starts a fresh one — a restricted Page takes every album on it down."""
    import time as _t

    from . import media_set_pace
    wanted = [u.strip() for u in (urls or "").split(",") if u.strip()]
    if not wanted:
        return {"error": "give me the page addresses, separated by commas"}
    cfg = local.read_config()
    page = page_url.strip() or next(iter((cfg.get("pages_by_site") or {}).values()), "")
    history = cfg.get("albums_by_page") or {}
    pages = {page: history.get(page, [])} if page else {}
    rows = media_set_pace.plan(wanted, pages=pages)   # no Page yet means the first album already needs one made
    more = media_set_pace.pages_needed(len(wanted), pages)
    per, cap = media_set_pace.per_week(), media_set_pace.per_page()
    return {"plan": [{"url": r["url"], "when": _t.strftime("%a %d %b, %H:%M", _t.localtime(r["at"])),
                      "at": r["at"], "page": r["page"] or "your Page", "new_page": r["new_page"],
                      "say": r["say"]} for r in rows],
            "page_url": page, "pages_to_make": more,
            "say": f"{len(rows)} albums, {per} a week. The first goes up now."
                   + (f" You will need {more} {'more ' if pages else ''}Facebook Page"
                      f"{'s' if more > 1 else ''} along the way." if more else ""),
            "detail": ["One album a week is the pace this method is built around; a burst is what gets a Page restricted.",
                       f"A Page carries {cap} albums, about a month's worth, and then the next starts a fresh Page.",
                       "Each website's own Page gets its own allowance, so several sites move faster than one.",
                       "Say the word and I will build the first now."]}


def get_traffic(url: str, keyword: str, brand: str = "", kind: str = "article", images: str = "",
                page_url: str = "", make_page: bool = False) -> dict:
    """Build a Facebook album that ranks for a phrase and sends visitors to one page. Runs here, on this machine,
    because it needs the person's own browser and their own signed-in Facebook."""
    from . import media_set_run
    files = [p.strip() for p in (images or "").split(",") if p.strip()]
    steps: list[str] = []
    cfg = local.read_config()
    by_site = cfg.get("pages_by_site") or {}
    history = cfg.get("albums_by_page") or {}
    site = url.split("//")[-1].split("/")[0].removeprefix("www.")
    r = media_set_run.get_traffic(url.strip(), keyword.strip(), brand=brand.strip(), kind=kind,
                                  images=files or None, use_page=page_url.strip(),
                                  pages_by_site=by_site, may_create_page=make_page,
                                  built_at=history.get(page_url.strip() or by_site.get(site, ""), []),
                                  on_step=steps.append)
    if r.get("site") and r.get("page_url"):
        by_site[r["site"]] = r["page_url"]          # asked once per website, not once per album
        local.write_config(pages_by_site=by_site)
    if r.get("ok") and r.get("album_url") and r.get("page_url"):
        import time as _t
        history.setdefault(r["page_url"], []).append(_t.time())    # what the pace is measured against
        local.write_config(albums_by_page=history)
    return {**r, "did": steps}


FREE_TOOLS = [
    types.Tool(name="search_sites", description=f"Search the free list of {N_FREE} backlink sites by name, domain, method, DA and dofollow. auto_build marks the ones build_link can do by itself. "
               "The result also lists locked higher-DA matches from the full library; when the user wants those, offer the subscription (see ask_the_user). "
               "Methods: profile_website_field, article_post, bookmark_submit, url_shortener, page_builder, forum_post, directory_listing, document_share, social_post, comment, qa_answer, forum_signature.",
               inputSchema={"type": "object", "properties": {"query": {"type": "string"}, "min_da": {"type": "integer"}, "dofollow_only": {"type": "boolean"},
                                                            "method": {"type": "string"}, "limit": {"type": "integer"}}}),
    types.Tool(name="get_method", description="The method for one site: playbook for its link type, what it requires, the ordered actions with exact button names, and which action places the link.",
               inputSchema={"type": "object", "properties": {"slug": {"type": "string"}}, "required": ["slug"]}),
    types.Tool(name="build_link", description="Build one backlink in a browser on this machine (login-free sites: shorteners and open submit forms), with a proof screenshot. "
               "On other sites it returns the method for you to follow. Status placed means verified live; gated means a captcha appeared: ask the user, then retry with headless=false or skip.",
               inputSchema={"type": "object", "properties": {"slug": {"type": "string"}, "target_url": {"type": "string"}, "anchor_text": {"type": "string"},
                                                            "headless": {"type": "boolean"}, "description": {"type": "string"}}, "required": ["slug", "target_url"]}),
    types.Tool(name="verify_link", description="Fetch a live page and confirm the backlink: target URL present as a hyperlink, anchor text, and whether it is nofollow.",
               inputSchema={"type": "object", "properties": {"live_url": {"type": "string"}, "target_url": {"type": "string"}, "anchor_text": {"type": "string"}}, "required": ["live_url", "target_url"]}),
    types.Tool(name="log_link", description="Record a link you placed by following a method: status placed (verified live), unverified, manual or failed.",
               inputSchema={"type": "object", "properties": {"slug": {"type": "string"}, "target_url": {"type": "string"}, "live_url": {"type": "string"}, "anchor_text": {"type": "string"},
                                                            "status": {"type": "string"}, "notes": {"type": "string"}}, "required": ["slug", "target_url", "live_url"]}),
    types.Tool(name="list_results", description="Every link built or logged on this machine.", inputSchema={"type": "object", "properties": {"limit": {"type": "integer"}}}),
    types.Tool(name="account", description="Current plan, links placed, and how to upgrade. Call it when the user asks about credits, pricing or limits.", inputSchema={"type": "object", "properties": {}}),
    types.Tool(name="upgrade", description="The subscription: every one of 1,245 sites and the whole engine, yearly or monthly. Returns the payment links and what to do after paying.", inputSchema={"type": "object", "properties": {}}),
    types.Tool(name="activate", description="Activate a subscription key (le_...) or a personal MCP link from the purchase success page. Verifies it with the hosted engine and saves it here; from then on every hosted tool is available.",
               inputSchema={"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}),
    types.Tool(name="library_summary", description="What the free list contains and what a subscription adds.", inputSchema={"type": "object", "properties": {}}),
    types.Tool(name="facebook_sign_in", description="Open a browser here and wait while the person signs in to Facebook. Needed once, ever; the signed-in browser is kept on their machine and their password never leaves it.",
               inputSchema={"type": "object", "properties": {"wait_minutes": {"type": "integer"}}}),
    types.Tool(name="traffic_plan", description="Plan albums for several of the customer's pages at once: a date and a Facebook Page for each. "
               "Albums go up one a week, and a Page carries four before the next starts a fresh Page. Show the dates plainly, say how many new "
               "Pages they will have to make, then build the first with get_traffic.",
               inputSchema={"type": "object", "properties": {"urls": {"type": "string"}, "page_url": {"type": "string"}}, "required": ["urls"]}),
    types.Tool(name="get_traffic", description="Get traffic to one page by building a Facebook album that ranks for a phrase and sends visitors on. "
               "Writes the text with their address on the first line, photographs their page, finds or makes their Facebook Page, builds and publishes the album, "
               "puts the address in the album's own description and checks a signed-out visitor can read it. Runs on this machine because it needs their own browser. "
               "If it answers needs_sign_in, call facebook_sign_in first. If it answers needs_answer 'page' they have more than one Facebook Page: put the options to them and call again with page_url set; the choice is remembered per website so later albums never ask again. What it returns is a traffic asset, never a followed link: say so.",
               inputSchema={"type": "object", "properties": {"url": {"type": "string"}, "keyword": {"type": "string"},
                                                            "brand": {"type": "string"}, "kind": {"type": "string"},
                                                            "images": {"type": "string"}, "page_url": {"type": "string"},
                                                            "make_page": {"type": "boolean"}}, "required": ["url", "keyword"]}),
]
FREE_IMPL = {"search_sites": search_sites, "get_method": get_method, "library_summary": library_summary, "verify_link": verify_link,
             "log_link": log_link, "list_results": list_results, "account": account, "upgrade": upgrade,
             "facebook_sign_in": facebook_sign_in, "get_traffic": get_traffic,
             "traffic_plan": traffic_plan}


# ------------------------------------------------------------------ server

server = Server("seo-agent")
_remote: Optional[Any] = None
_stack: Optional[AsyncExitStack] = None


async def _connect_remote(url: Optional[str] = None, key: Optional[str] = None):
    global _remote, _stack
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    u, k = credentials()
    url, key = url or u, key or k
    await _disconnect_remote()
    _stack = AsyncExitStack()

    async def open_session():
        r, w, _ = await _stack.enter_async_context(streamablehttp_client(url, headers={"Authorization": f"Bearer {key}"} if key else {}))
        sess = await _stack.enter_async_context(ClientSession(r, w))
        await sess.initialize()
        return sess

    try:
        _remote = await asyncio.wait_for(open_session(), CONNECT_TIMEOUT)
    except BaseException as e:   # a dead host must fail fast, never hang the assistant
        await _disconnect_remote()
        raise ConnectionError(f"could not reach {url} within {CONNECT_TIMEOUT}s: {type(e).__name__}") from None
    return _remote


async def _disconnect_remote():
    global _remote, _stack
    if _stack is not None:
        try:
            await _stack.aclose()
        except Exception:
            pass
    _remote = _stack = None


async def _remote_session():
    if _remote is None:
        await _connect_remote()
    return _remote


async def activate(key: str) -> dict:
    key = (key or "").strip()
    url, _ = credentials()
    if key.startswith("http"):
        url, key = key, _personal_key(key)
        url = url if "/u/" not in url else f"{HOST}/mcp"
    if not key.startswith("le_"):
        return {"error": "a key looks like le_... ; copy it from the purchase success page, or paste your personal MCP link"}
    try:
        sess = await _connect_remote(url, key)
        res = await asyncio.wait_for(sess.call_tool("account", {}), CONNECT_TIMEOUT)
        text = "".join(c.text for c in res.content if getattr(c, "type", "") == "text")
        info = json.loads(text) if text else {}
    except Exception as e:
        await _disconnect_remote()
        return {"error": f"could not verify the key with {url}: {type(e).__name__}: {str(e)[:120]}"}
    if "error" in info:
        await _disconnect_remote()
        return {"error": f"the engine rejected this key: {info['error']}"}
    local.write_config(api_key=key, url=url)
    try:
        await server.request_context.session.send_tool_list_changed()
    except Exception:
        pass
    return {"activated": True, "plan": info.get("plan"), "links_left": info.get("links_left"), "dashboard": info.get("dashboard_url"),
            "note": "Subscription tools are live in this session: plan_campaign, build_link on every site, gates, monitoring, reports."}


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    if not hosted():
        return FREE_TOOLS
    try:
        remote = list((await (await _remote_session()).list_tools()).tools)
    except Exception:
        # The engine being unreachable is not a reason to lose the tools that never needed it. Their browser is
        # on this machine and works whether or not our server does.
        return FREE_TOOLS
    # The engine advertises browser tools too, but running them there would mean a server with no browser and no
    # session. Ours replace them by name; everything else is the engine's.
    mine = {t.name: t for t in FREE_TOOLS if runs_here(t.name)}
    merged = [mine.get(t.name, t) for t in remote]
    have = {t.name for t in merged}
    return merged + [t for n, t in mine.items() if n not in have]


@server.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent]:
    arguments = arguments or {}
    if name == "activate":
        return [types.TextContent(type="text", text=json.dumps(await activate(arguments.get("key", "")), ensure_ascii=False))]
    if hosted() and not runs_here(name):
        try:
            res = await (await _remote_session()).call_tool(name, arguments)
            return list(res.content)
        except Exception as e:
            if name not in FREE_IMPL:
                return [types.TextContent(type="text", text=json.dumps(
                    {"error": f"the engine is unreachable: {type(e).__name__}",
                     "say": "I cannot reach the service right now, so that one will have to wait.",
                     "detail": ["Anything that runs on your own machine still works: building a link, checking one "
                                "is live, and your own results."]}, ensure_ascii=False))]
            await _disconnect_remote()      # fall through to the local version rather than failing outright
    if name in ("build_link", "get_traffic", "facebook_sign_in"):
        fn = {"build_link": build_link, "get_traffic": get_traffic, "facebook_sign_in": facebook_sign_in}[name]
        out = await asyncio.to_thread(fn, **arguments)
        return [types.TextContent(type="text", text=json.dumps(out, ensure_ascii=False))]
    fn = FREE_IMPL.get(name)
    if fn is None:
        return [types.TextContent(type="text", text=json.dumps({"error": f"{name} needs a subscription", "upgrade": _upgrade_hint()}))]
    return [types.TextContent(type="text", text=json.dumps(fn(**arguments), ensure_ascii=False))]


@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    if hosted():
        return (await (await _remote_session()).list_prompts()).prompts
    return [types.Prompt(name="build_backlink", description="Build one backlink on a free-list site by following its method, then verify it.",
                         arguments=[types.PromptArgument(name="slug", required=True), types.PromptArgument(name="target_url", required=True), types.PromptArgument(name="anchor_text", required=False)])]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    arguments = arguments or {}
    if hosted():
        return await (await _remote_session()).get_prompt(name, arguments)
    m = get_method(arguments.get("slug", ""))
    if "error" in m:
        text = m["error"]
    else:
        steps = "\n".join(f"{a['n']}. [{a['kind']}]{' [PLACEMENT]' if a['is_placement'] else ''} {a['text']}" + (f"  targets: {', '.join(a['targets'])}" if a['targets'] else "") for a in m["steps"])
        text = (f"Build a backlink to {arguments.get('target_url')} on {m['name']} ({m['url']}), DA {m['da']}, method {m['method_label']}.\n"
                f"Anchor text: {arguments.get('anchor_text') or '(the URL, or a natural anchor)'}\n\nRequires:\n" + "\n".join(f"- {r}" for r in m["requirements"]) +
                f"\n\nIf build_link can do this site by itself (auto_build), call it. Otherwise follow the steps, then verify_link and log_link.\n\nPlaybook:\n{m['playbook']}\n\nSteps:\n{steps}\n\n{RULES}")
    return types.GetPromptResult(messages=[types.PromptMessage(role="user", content=types.TextContent(type="text", text=text))])


async def _run() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":   # `python -m seoagent.server` should start it, not import it silently
    main()
