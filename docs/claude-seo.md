---
title: "Claude SEO, link building from Claude Code and Claude Desktop"
description: "Use Claude as an SEO agent for link building. Install SEO Agent's MCP server in Claude Code or Claude Desktop and build verified backlinks from a chat."
---

# Claude SEO: link building from Claude

Claude can plan and build backlinks when it has two things: a library of sites with their methods, and a browser. SEO Agent supplies the first as an MCP server; Claude Code's browser tools or the Playwright MCP supply the second.

## Install

Free, ten links on 25 sites, built in your own browser, no account:

```bash
pip install seo-agent && playwright install chromium
claude mcp add seo-agent -- seo-agent
```

Claude Desktop, in `claude_desktop_config.json`: `{ "mcpServers": { "seo-agent": { "command": "seo-agent" } } }`

Every site, $97 a year or $27 a month: subscribe at [https://mcp.seoagent.dev/buy](https://mcp.seoagent.dev/buy), then tell Claude `activate le_your_key`. In Claude Desktop or claude.ai you can instead add the personal link from the success page as a custom connector (Settings, Connectors, Add custom connector, no OAuth).

## A first session

1. *Search the free list for dofollow sites above DA 50.* Claude calls `search_sites` and shows the candidates with DA and referring domains.
2. *Get the method for GitBook.* Claude calls `get_method` and reads the playbook, the requirements and the steps, including which step places the link.
3. *Build a link to https://example.com with the anchor "example".* Claude follows the steps in its browser, asks you in the chat if a captcha or a verification code appears, continues once it is cleared, and reports the live URL.
4. *Verify it.* With a key, Claude calls `verify_link` on that page and reports hyperlink, anchor and nofollow status.

## What else it can do in the same chat

With a subscription the same conversation reaches the rest of the engine, so you rarely leave Claude:

- *Which keywords should this page target?* reads the page and proposes keywords and a full anchor plan.
- *Who links to my competitors but not to me?* returns the gap with a method attached to every row that is buildable.
- *Are my links still live?* re-checks every one it placed and tells you which dropped.
- *Show me my backlink profile* lists every referring domain, what is new and lost this month, spam flags, and generates a disavow file.
- *Report on that campaign* returns planned against placed, counts by status and method, and every live URL, as data or as a rendered page you can send to a client.

## Why Claude does well at this

Long multi-step guides with quoted button names are exactly the kind of instruction Claude follows reliably, and it reads the annotated screenshot for a step when a page does not match. The playbooks add the judgement a guide leaves out: what to write in an article, why a plain-text URL is not a backlink, when to stop.

Related: [Cursor SEO](cursor-seo.html), [how to get backlinks with an AI agent](how-to-get-backlinks-with-ai.html).
