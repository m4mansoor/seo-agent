---
title: "Cursor SEO, link building from Cursor"
description: "Use Cursor as an SEO agent for link building. Add SEO Agent's MCP server to Cursor and build verified backlinks with the model of your choice."
---

# Cursor SEO: link building from Cursor

Cursor runs MCP servers with whichever model you choose, so SEO Agent works there with Claude, GPT or Gemini.

## Install

Free, 50 sites, links built in your own browser: `pip install seo-agent && playwright install chromium`, then in Cursor, Settings, MCP, Add new MCP server with command `seo-agent`.

Every site, $97 a year or $27 a month: subscribe at [https://mcp.seoagent.dev/buy](https://mcp.seoagent.dev/buy) and tell the assistant `activate le_your_key`. Or add the personal link from the success page as a server with `"url"` instead of `"command"`.

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
