---
title: "SEO desktop app for Windows and macOS (in development)"
description: "A desktop app that builds backlinks in its own browser, using accounts you are already signed in to. Windows and macOS, built with Tauri. In development."
---

# The desktop app

**Status: in development.** Windows and macOS, built with Tauri. Star [the repository](https://github.com/m4mansoor/seo-agent) to hear when the signed builds are available.

## Why a desktop app at all

Because it is the only place the agent can use **your own accounts**. A WordPress plugin and a Shopify app run on servers that cannot open a browser, so their links are built by the hosted engine with a generated identity. The desktop app ships a browser. You sign in to Medium, a forum, a directory, once, by hand, in the app. From then on the agent works inside that session: no generated identities, no verification emails, no waiting on an inbox, and a captcha appears in a window where you clear it and the job continues.

## What it does

**Free, without an account.** Everything the pip package does, without Python or a terminal: ten links on the 25 free sites with their methods, building on login-free sites with proof screenshots, verification, and a local results log, all behind a real interface. Guided manual mode opens the page next to the checklist and highlights the field each step names. It will also write the MCP entry for Claude Desktop, Claude Code, Cursor and Windsurf for you, so your assistant uses the same library and the same results database.

**With a subscription.** The full 1,248-site library and the campaign planner. Building on every method inside your own signed-in sessions, with your own AI model key held on your machine and called directly, so page snapshots go to your provider and nowhere else. A session vault showing which sites are signed in and which need a fresh login. The backlink monitor, competitor gap and reports, with PDFs saved straight to disk. Overnight runs with the browser hidden and tray notifications when a link lands, a gate opens or a link drops. Separate profiles per client, so agency accounts never mix.

## How it is built

A Tauri shell around the same open-source package, with its own Chromium downloaded on first run. Signed and notarised on macOS, Authenticode-signed on Windows, with automatic updates. Distributed from this site, and through Homebrew and winget once signing is in place. Not through the Mac App Store, because sandboxing would block the browser profile that makes the whole thing work.

## Privacy

Your accounts, cookies and model key stay on your machine. Nothing about a session is uploaded. When the app asks the hosted engine what to do next on an account-based site, it sends the visible text and element labels of the page, never form values or cookies, and you can read every snapshot it sent in a log.

Meanwhile, the [pip package](https://github.com/m4mansoor/seo-agent) does the free half today on any machine with Python.
