---
title: "Cursor SEO, link building from Cursor"
description: "Use Cursor as an SEO agent for link building. Add SEO Agent's MCP server to Cursor and build verified backlinks with the model of your choice."
---

# Cursor SEO: link building from Cursor

Cursor runs MCP servers with whichever model you choose, so SEO Agent works there with Claude, GPT or Gemini.

## Install

Hosted, with 50 backlinks free and $97 once for unlimited: get your link at [https://mcp.seoagent.dev/start](https://mcp.seoagent.dev/start), then in Cursor, Settings, MCP, Add new MCP server:

```json
{ "mcpServers": { "seo-agent": { "url": "https://mcp.seoagent.dev/u/le_…/mcp" } } }
```

Local free mode, the 50 bundled sites and no account: `pip install seo-agent`, then add a server with command `seo-agent`.

## Use

Open the agent panel and ask for what you want in plain language:

- *List free-list sites for article posts and show DA.*
- *Get the method for the top one and build a link to my site with the anchor "my brand".*
- *Verify the link on the live page.*

Cursor calls the server's tools, follows the site's method with a browser tool if one is installed, and reports the live URL.

## Notes

- Models differ. Claude and GPT-class models follow ten-step methods reliably; small local models struggle. Pick a capable model for building; any model is fine for searching and planning.
- Cursor without a browser tool can still search, plan, verify and log; the built-in executor handles login-free sites through the hosted engine.

Related: [Claude SEO](claude-seo.html), [SEO MCP server tool reference](seo-mcp-server.html).
