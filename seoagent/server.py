"""SEO Agent MCP server.

Free mode, no account: the 50 bundled sites with their methods, and local tools that build on login-free sites in
your own browser, verify a live page and keep a results log. Lifetime mode: after `activate` with the key from your
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
PRICE_USD = 97


def _load(name: str):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


SITES: list[dict] = _load("free-sites.json")
PLAYBOOKS: dict[str, str] = _load("playbooks.json")
BY_SLUG = {s["slug"]: s for s in SITES}

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

def search_sites(query: str = "", min_da: int = 0, dofollow_only: bool = False, method: str = "", limit: int = 25) -> list[dict]:
    q = query.lower().strip()
    out = []
    for s in SITES:
        if s["da"] < min_da or (dofollow_only and not s["dofollow"]) or (method and s["method"] != method):
            continue
        if q and q not in " ".join([s["name"], s["domain"], s["slug"], s["method_label"]]).lower():
            continue
        out.append({k: s[k] for k in ("slug", "name", "domain", "url", "da", "dofollow", "method", "method_label", "tier", "referring_domains", "organic_traffic")})
        out[-1]["auto_build"] = s["tier"] == "A" and s["method"] in ("url_shortener", "bookmark_submit")
    return out[:limit]


def get_method(slug: str) -> dict:
    s = BY_SLUG.get(slug.strip().lower())
    if not s:
        return {"error": f"{slug!r} is not in the free list; the full 1,245-site library is in the Lifetime plan", "upgrade": _upgrade_hint()}
    return {**s, "playbook": PLAYBOOKS.get(s["method"], ""), "rules": RULES}


def library_summary() -> dict:
    return {"mode": "free", "sites": len(SITES), "dofollow": sum(1 for s in SITES if s["dofollow"]),
            "da_range": [min(s["da"] for s in SITES), max(s["da"] for s in SITES)],
            "lifetime_plan": {"sites": 1245, "reachable": 1138, "dofollow": 900, "da_90_plus": 117, "price_usd": PRICE_USD, "buy": BUY_URL}}


def _upgrade_hint() -> dict:
    return {"plan": "Lifetime", "price_usd": PRICE_USD, "url": BUY_URL,
            "how": "Pay once at the URL, copy the key shown on the success page, then say: activate <key>."}


def build_link(slug: str, target_url: str, anchor_text: str = "", headless: bool = True, description: str = "") -> dict:
    """Build one link in a local browser on a login-free site. Elsewhere returns the method to follow."""
    s = BY_SLUG.get(slug.strip().lower())
    if not s:
        return {"error": f"{slug!r} is not in the free list", "upgrade": _upgrade_hint()}
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
    return {"placed": res.placed(), "free_sites": len(SITES), "results": res.all(limit)}


def account() -> dict:
    res = local.Results()
    return {"plan": "free", "links_placed": res.placed(), "free_sites": len(SITES),
            "note": "Free mode builds on the 50 bundled sites in your own browser. The Lifetime plan adds 1,245 sites, the campaign planner, "
                    "building on account-based sites, gates with connected services, monitoring, reports and a dashboard.",
            "upgrade": _upgrade_hint()}


def upgrade() -> dict:
    return {"plan": "Lifetime", "price_usd": PRICE_USD, "url": BUY_URL,
            "ask_the_user": f"The Lifetime plan is one payment of ${PRICE_USD} for unlimited links on 1,245 sites: {BUY_URL} . "
                            "After paying, copy the key from the success page and tell me: activate <key>."}


FREE_TOOLS = [
    types.Tool(name="search_sites", description="Search the free list of 50 backlink sites by name, domain, method, DA and dofollow. auto_build marks the ones build_link can do by itself. "
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
    types.Tool(name="upgrade", description=f"The Lifetime plan: ${PRICE_USD} once for unlimited links on 1,245 sites. Returns the payment link and what to do after paying.", inputSchema={"type": "object", "properties": {}}),
    types.Tool(name="activate", description="Activate a Lifetime key (le_...) or a personal MCP link from the purchase success page. Verifies it with the hosted engine and saves it here; from then on every hosted tool is available.",
               inputSchema={"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}),
    types.Tool(name="library_summary", description="What the free list contains and what the Lifetime plan adds.", inputSchema={"type": "object", "properties": {}}),
]
FREE_IMPL = {"search_sites": search_sites, "get_method": get_method, "library_summary": library_summary, "verify_link": verify_link,
             "log_link": log_link, "list_results": list_results, "account": account, "upgrade": upgrade}


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
    r, w, _ = await _stack.enter_async_context(streamablehttp_client(url, headers={"Authorization": f"Bearer {key}"} if key else {}))
    _remote = await _stack.enter_async_context(ClientSession(r, w))
    await _remote.initialize()
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
        res = await sess.call_tool("account", {})
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
            "note": "Lifetime tools are live in this session: plan_campaign, build_link on every site, gates, monitoring, reports."}


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    if hosted():
        return (await (await _remote_session()).list_tools()).tools
    return FREE_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent]:
    arguments = arguments or {}
    if name == "activate":
        return [types.TextContent(type="text", text=json.dumps(await activate(arguments.get("key", "")), ensure_ascii=False))]
    if hosted():
        res = await (await _remote_session()).call_tool(name, arguments)
        return list(res.content)
    if name == "build_link":
        out = await asyncio.to_thread(build_link, **arguments)
        return [types.TextContent(type="text", text=json.dumps(out, ensure_ascii=False))]
    fn = FREE_IMPL.get(name)
    if fn is None:
        return [types.TextContent(type="text", text=json.dumps({"error": f"{name} is a Lifetime tool", "upgrade": _upgrade_hint()}))]
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
