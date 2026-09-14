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
| `search_sites` | The full library of 1,245 sites with referring domains, traffic and spam score |
| `get_method` | Same, for every site |
| `get_step_screenshot` | The annotated screenshot for a step, when a page does not match the text |
| `set_identity`, `get_identity` | The name, inbox, username and password used on sign-up forms |
| `plan_campaign` | Pick sites, balance dofollow share and method mix, assign anchor text by ratio |
| `build_link` | Build a link automatically on login-free sites, with proof screenshot |
| `verify_link` | Fetch a live page and confirm the hyperlink, anchor text and nofollow |
| `connect_service`, `list_services`, `read_inbox` | Connect your own AI model key (Anthropic, OpenAI, Google, OpenRouter) that drives account-based sites, plus a captcha solver, inbox or SMS service; read verification links and codes |
| `resolve_gate` | Continue after a gate: clear it in a window, retry with a service, paste a code, or skip |
| `queue_build`, `job_status` | Background builds for clients with short tool timeouts |
| `generate_identity` | A complete sign-up identity on your catch-all domain |
| `recheck_links`, `campaign_report` | Monitor placed links over time and report a campaign |
| `log_link` | Record an outcome: placed, unverified or manual |
| `list_results` | Everything built or logged under your key, and the credit balance |
| `account` | Plan, links left, your MCP link, dashboard and the upgrade link |

Prompts: `build_backlink` for one site, `run_campaign` for the whole loop.

## Method vocabulary

Tiers: A needs no account, B sign-up only, C email verification or captcha, D social login.

Methods: `profile_website_field`, `article_post`, `bookmark_submit`, `url_shortener`, `page_builder`, `forum_post`, `forum_signature`, `document_share`, `directory_listing`, `social_post`, `qa_answer`, `comment`.

Actions in a method: `navigate`, `click`, `fill_form`, `place_link`, `email_verify`, `upload`, `wait_moderation`, `verify`.

## Statuses

`placed` means verified live. `unverified` means placed but not confirmable yet, for example a post awaiting moderation. `gated` means the site asked for a captcha, a verification code, a login or a payment: the result carries the gate and its options, and `resolve_gate` continues the build once you clear it, connect a service, paste a code or skip. `manual` means you placed the link yourself and logged it.
