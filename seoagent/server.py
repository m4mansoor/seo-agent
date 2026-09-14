"""MCP server. Free mode: local tools over the bundled site list. Key mode: every tool of the hosted engine, proxied."""
from __future__ import annotations

import asyncio
import json
import os
from contextlib import AsyncExitStack
from typing import Any, Optional

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
REMOTE_URL = os.environ.get("SEOAGENT_URL", "https://mcp.seoagent.dev/mcp")
API_KEY = os.environ.get("SEOAGENT_API_KEY", "")
# Hosted mode is on when a key is given, or when SEOAGENT_URL is a personal link (the key is inside the URL: /u/<key>/mcp).
HOSTED = bool(API_KEY) or "/u/le_" in REMOTE_URL


def _load(name: str):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


SITES: list[dict] = _load("free-sites.json")
PLAYBOOKS: dict[str, str] = _load("playbooks.json")
BY_SLUG = {s["slug"]: s for s in SITES}

RULES = """Rules for every link: use the target URL and anchor text exactly as given; never place the same link twice on a site;
follow the steps in order, the step marked placement is where the link goes; use the exact button and field names quoted;
stop at captchas or payment gates and report manual; after placing, open the public page and confirm the hyperlink,
anchor and whether it is nofollow; report the live URL."""


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
    return out[:limit]


def get_method(slug: str) -> dict:
    s = BY_SLUG.get(slug.strip().lower())
    if not s:
        return {"error": f"{slug!r} is not in the free list; the full 1,245-site library needs an API key"}
    return {**s, "playbook": PLAYBOOKS.get(s["method"], ""), "rules": RULES}


def library_summary() -> dict:
    return {"mode": "free", "sites": len(SITES), "dofollow": sum(1 for s in SITES if s["dofollow"]),
            "da_range": [min(s["da"] for s in SITES), max(s["da"] for s in SITES)],
            "full_library": {"sites": 1245, "reachable": 1138, "dofollow": 900, "da_90_plus": 117, "needs": "API key"}}


FREE_TOOLS = [
    types.Tool(name="search_sites", description="Search the free list of 50 backlink sites by name, domain, method, DA and dofollow. "
               "Methods: profile_website_field, article_post, bookmark_submit, url_shortener, page_builder, forum_post, directory_listing, document_share, social_post, comment, qa_answer, forum_signature.",
               inputSchema={"type": "object", "properties": {"query": {"type": "string"}, "min_da": {"type": "integer"}, "dofollow_only": {"type": "boolean"},
                                                            "method": {"type": "string"}, "limit": {"type": "integer"}}}),
    types.Tool(name="get_method", description="The method for one site: playbook for its link type, what it requires, the ordered actions with exact button names, and which action places the link.",
               inputSchema={"type": "object", "properties": {"slug": {"type": "string"}}, "required": ["slug"]}),
    types.Tool(name="library_summary", description="What this free list contains and what the full library adds.", inputSchema={"type": "object", "properties": {}}),
]
FREE_IMPL = {"search_sites": search_sites, "get_method": get_method, "library_summary": library_summary}


# ------------------------------------------------------------------ server

server = Server("seo-agent")
_remote: Optional[Any] = None
_stack: Optional[AsyncExitStack] = None


async def _connect_remote():
    global _remote, _stack
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    _stack = AsyncExitStack()
    r, w, _ = await _stack.enter_async_context(streamablehttp_client(REMOTE_URL, headers={"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}))
    _remote = await _stack.enter_async_context(ClientSession(r, w))
    await _remote.initialize()


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    if HOSTED:
        if _remote is None:
            await _connect_remote()
        return (await _remote.list_tools()).tools
    return FREE_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent]:
    arguments = arguments or {}
    if HOSTED:
        if _remote is None:
            await _connect_remote()
        res = await _remote.call_tool(name, arguments)
        return list(res.content)
    fn = FREE_IMPL.get(name)
    if fn is None:
        return [types.TextContent(type="text", text=json.dumps({"error": f"{name} needs an API key; free mode has search_sites, get_method and library_summary"}))]
    return [types.TextContent(type="text", text=json.dumps(fn(**arguments), ensure_ascii=False))]


@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    if HOSTED:
        if _remote is None:
            await _connect_remote()
        return (await _remote.list_prompts()).prompts
    return [types.Prompt(name="build_backlink", description="Build one backlink on a free-list site by following its method, then verify it.",
                         arguments=[types.PromptArgument(name="slug", required=True), types.PromptArgument(name="target_url", required=True), types.PromptArgument(name="anchor_text", required=False)])]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    arguments = arguments or {}
    if HOSTED:
        if _remote is None:
            await _connect_remote()
        return await _remote.get_prompt(name, arguments)
    m = get_method(arguments.get("slug", ""))
    if "error" in m:
        text = m["error"]
    else:
        steps = "\n".join(f"{a['n']}. [{a['kind']}]{' [PLACEMENT]' if a['is_placement'] else ''} {a['text']}" + (f"  targets: {', '.join(a['targets'])}" if a['targets'] else "") for a in m["steps"])
        text = (f"Build a backlink to {arguments.get('target_url')} on {m['name']} ({m['url']}), DA {m['da']}, method {m['method_label']}.\n"
                f"Anchor text: {arguments.get('anchor_text') or '(the URL, or a natural anchor)'}\n\nRequires:\n" + "\n".join(f"- {r}" for r in m["requirements"]) +
                f"\n\nPlaybook:\n{m['playbook']}\n\nSteps:\n{steps}\n\n{RULES}")
    return types.GetPromptResult(messages=[types.PromptMessage(role="user", content=types.TextContent(type="text", text=text))])


async def _run() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
