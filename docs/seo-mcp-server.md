---
title: "SEO MCP server, tool reference"
description: "Tools and prompts of SEO Agent's MCP server for link building. Search a backlink site library, get a site's method, plan a campaign, build, verify and log links."
---

# The SEO MCP server: tool reference

SEO Agent is an MCP server. Any MCP client, Claude, Cursor, Codex, Windsurf, VS Code, Cline and others, can call these tools.

## Free, the pip package

| Tool | What it does |
|---|---|
| `search_sites` | Search the free list of 25 sites by name, domain, method, DA and dofollow; marks the ones `build_link` can do alone, and shows locked higher-DA matches from the full library |
| `get_method` | Playbook, requirements and parsed actions for one site, with the placement step marked |
| `build_link` | Build a link in a local browser on login-free sites, with proof; returns the method elsewhere |
| `verify_link` | Fetch a live page and confirm the hyperlink, anchor text and nofollow |
| `log_link`, `list_results` | The local results log |
| `account`, `upgrade` | Links built, and the subscription links |
| `activate` | Save a subscription key or personal link; every hosted tool appears in the same session |
| `library_summary` | What the free list contains and what a subscription adds |

## Subscribed, after `activate`

$97 a year or $27 a month at [https://mcp.seoagent.dev/buy](https://mcp.seoagent.dev/buy). The same server, now proxying the hosted engine:

| Tool | What it does |
|---|---|
| `search_sites` | The full library of 1,245 sites with referring domains, traffic, spam score and liveness |
| `get_method` | The playbook, requirements and parsed actions for every site, with the placement step marked |
| `get_step_screenshot` | The annotated screenshot for a step, when a page does not match the text |
| `plan_campaign` | Pick sites, balance the dofollow share and method mix, assign anchor text by ratio |
| `build_link` | Build a link automatically, with a proof screenshot |
| `queue_build`, `job_status` | Background builds, for clients with short tool timeouts |
| `verify_link` | Fetch a live page and confirm the hyperlink, anchor text and nofollow |
| `log_link` | Record an outcome: placed, unverified, gated or manual |
| `list_results` | Everything built or logged under your key |
| `account` | Plan, links left, renewal date, your MCP link, dashboard and the upgrade link |
| `set_identity`, `get_identity` | The name, inbox, username and password used on sign-up forms |
| `generate_identity` | A complete, consistent sign-up identity on your catch-all domain |
| `connect_service`, `list_services` | Your own AI model key (Anthropic, OpenAI, Google, OpenRouter) that drives account-based sites, plus a captcha solver, an inbox or an SMS service |
| `read_inbox` | Read recent messages from the connected inbox and extract verification links and codes |
| `resolve_gate` | Continue after a gate: clear it in a window, retry with a service, paste a code, or skip |
| `register_site`, `list_sites`, `verify_site` | Register a site under your key and prove you own the domain, so many sites can run on one subscription |
| `suggest_keywords` | Read a target page and get keywords and a full anchor plan across the five anchor types |
| `monitor_backlinks` | Every referring domain to your site, what is new and lost, spam flags, and a disavow file |
| `competitor_gap` | The referring domains your competitors have and you do not, each row carrying the method to build it |
| `recheck_links` | Re-verify every placed link: still live, still a hyperlink, still dofollow |
| `campaign_report` | Planned against placed, counts by status and method, every live URL, as data or rendered HTML |

Twenty-six tools in all. Two resources come with them: `library://summary` for what the library holds, and
`library://rules` for the rules the agent follows on every link.

Prompts: `build_backlink` for one site, `run_campaign` for the whole loop.

## Method vocabulary

Tiers: A needs no account, B sign-up only, C email verification or captcha, D social login.

Methods: `profile_website_field`, `article_post`, `bookmark_submit`, `url_shortener`, `page_builder`, `forum_post`, `forum_signature`, `document_share`, `directory_listing`, `social_post`, `qa_answer`, `comment`.

Actions in a method: `navigate`, `click`, `fill_form`, `place_link`, `email_verify`, `upload`, `wait_moderation`, `verify`.

## Statuses

`placed` means verified live. `unverified` means placed but not confirmable yet, for example a post awaiting moderation. `gated` means the site asked for a captcha, a verification code, a login or a payment: the result carries the gate and its options, and `resolve_gate` continues the build once you clear it, connect a service, paste a code or skip. `manual` means you placed the link yourself and logged it.

## For plugin and app developers

The hosted engine also speaks plain REST at `/api/v1`, because a WordPress plugin in PHP and a Shopify app in Node are not MCP clients. Every tool above has an endpoint, plus the ones only a hosted client needs: site registration with a callback ownership check, signed outbound webhooks so a plugin never polls, and an agent step endpoint that lets a client with its own browser ask the engine what to do next on a page.

Authentication is the same key, either as a bearer header or inside the URL path, so a client that can only hold a URL still works. That API is what the [WordPress plugin](wordpress-backlink-plugin.html), the [Shopify app](shopify-seo-app.html) and the [desktop app](seo-desktop-app.html) are built on. See the [roadmap](roadmap.html) for where each one is.
