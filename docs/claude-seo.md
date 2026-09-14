---
title: "Claude SEO, link building from Claude Code and Claude Desktop"
description: "Use Claude as an SEO agent for link building. Install SEO Agent's MCP server in Claude Code or Claude Desktop and build verified backlinks from a chat."
---

# Claude SEO: link building from Claude

Claude can plan and build backlinks when it has two things: a library of sites with their methods, and a browser. SEO Agent supplies the first as an MCP server; Claude Code's browser tools or the Playwright MCP supply the second.

## Install

The quickest way is the hosted link. Get one at [https://mcp.seoagent.dev/start](https://mcp.seoagent.dev/start): it carries your key, comes with 50 backlinks free, and upgrades to unlimited for $97 once.

Claude Desktop and claude.ai: Settings, Connectors, Add custom connector, name `SEO Agent`, paste the link, no OAuth, then enable it in a chat.

Claude Code:

```bash
claude mcp add --transport http seo-agent "https://mcp.seoagent.dev/u/le_…/mcp"
```

Local free mode instead, with the 50 bundled sites and no account:

```bash
pip install seo-agent
claude mcp add seo-agent -- seo-agent
```

Claude Desktop, in `claude_desktop_config.json`: `{ "mcpServers": { "seo-agent": { "command": "seo-agent" } } }`

## A first session

1. *Search the free list for dofollow sites above DA 50.* Claude calls `search_sites` and shows the candidates with DA and referring domains.
2. *Get the method for GitBook.* Claude calls `get_method` and reads the playbook, the requirements and the steps, including which step places the link.
3. *Build a link to https://example.com with the anchor "example".* Claude follows the steps in its browser, asks you in the chat if a captcha or a verification code appears, continues once it is cleared, and reports the live URL.
4. *Verify it.* With a key, Claude calls `verify_link` on that page and reports hyperlink, anchor and nofollow status.

## Why Claude does well at this

Long multi-step guides with quoted button names are exactly the kind of instruction Claude follows reliably, and it reads the annotated screenshot for a step when a page does not match. The playbooks add the judgement a guide leaves out: what to write in an article, why a plain-text URL is not a backlink, when to stop.

Related: [Cursor SEO](cursor-seo.html), [how to get backlinks with an AI agent](how-to-get-backlinks-with-ai.html).
