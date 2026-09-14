---
title: Cursor SEO, link building from Cursor
description: Use Cursor as an SEO agent for link building. Add the SEO Agent MCP server to Cursor and build verified backlinks with the model of your choice.
---

# Cursor SEO: link building from Cursor

Cursor runs MCP servers with whichever model you choose, so SEO Agent works there with Claude, GPT or Gemini.

## Install

```bash
pip install seo-agent
```

In Cursor: Settings, MCP, Add new MCP server. Command: `seo-agent`. With a free API key, add `SEOAGENT_API_KEY` under the server's environment.

## Use

Open the agent panel and ask for what you want in plain language:

- *List free-list sites for article posts and show DA.*
- *Get the method for the top one and build a link to my site with the anchor "my brand".*
- *Verify the link on the live page.*

Cursor calls the server's tools, follows the site's method with a browser tool if one is installed, and reports the live URL.

## Notes

- Models differ. Claude and GPT-class models follow ten-step methods reliably; small local models struggle. Pick a capable model for building; any model is fine for searching and planning.
- Cursor without a browser tool can still search, plan, verify and log; the built-in executor handles login-free sites through the hosted engine.

Related: [Claude SEO](claude-seo.md), [SEO MCP server tool reference](seo-mcp-server.md).
