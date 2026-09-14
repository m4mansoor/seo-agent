---
title: "Roadmap and status"
description: "What SEO Agent does today, what is in development, and what is planned: the hosted engine, the WordPress plugin, the Shopify app and the Windows and macOS desktop app."
---

# Roadmap and status

Written plainly, because a roadmap that reads like a brochure is useless. Three states only: **live** means you can use it right now, **in development** means the code is being written, **planned** means designed and scheduled but not started.

## Live today

| What | Where it is |
|---|---|
| The `seo-agent` package | `pip install seo-agent`, MIT, on GitHub |
| 25 backlink sites with their step-by-step methods | Bundled in the package, two of them at DA 90 or higher |
| Local building on login-free sites | Scripted playbooks drive a browser on your machine, with a proof screenshot |
| Link verification | Fetches the live page and checks the hyperlink, the anchor and nofollow |
| Local results log | Every link you build or place by hand, on your machine |
| Works in any MCP client | Claude Code, Claude Desktop, claude.ai, Cursor, Codex, ChatGPT, Windsurf |

## In development

**The hosted engine.** The full 1,245-site library, the campaign planner, building on account-based sites with your own AI model key, gates with connected services, link velocity pacing, the backlink monitor with a disavow file, competitor gap analysis, campaign reports and a dashboard. Every piece is built and tested; it is not deployed yet, so the subscription is not open. When it opens, the same package activates with a key and nothing else changes.

## Planned

**WordPress plugin.** Pick any post, page, product or category as a target, get keyword and anchor suggestions from the page itself, plan a campaign, build every link from the full library, clear gates from the admin bar, watch links weekly, and read a white-label report. WooCommerce products and categories are targets from the start, and Yoast, Rank Math, All in One SEO and SEOPress focus keywords are imported. Free tier included.

**Shopify app.** The same, built on Polaris and embedded in the Shopify admin, with products, collections, pages and blog posts as targets, billing through Shopify, and campaigns that fire when a product or collection goes live.

**Windows and macOS desktop app.** The one place the agent uses your own accounts: sign in to a site once in the app's browser, and from then on the agent works inside that session. No generated identities, no verification emails, and captchas appear in a window where you clear them yourself. Built with Tauri, signed and notarised.

## Not planned

Buying links, private blog networks, spun content, and anything that pretends to be a person. The library is public properties whose owners allow a link; the agent follows each site's own rules and reports honestly when a link is nofollow, unindexed or awaiting moderation.

## Follow along

Star [the repository](https://github.com/m4mansoor/seo-agent) to hear when the hosted service and the plugins open. Everything above is built in the open.
