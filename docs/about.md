---
title: "About"
description: "Who builds SEO Agent, why it exists, and the rules it is built to keep."
---

# About

## The person

SEO Agent is built by **Inaamul Haq Mansoor**, an engineer who has spent more than twelve years building systems that have to work unattended: IoT and embedded platforms, edge AI, and the infrastructure that keeps them honest. He is CEO and Chief Technology Officer of [Tech Mentions](https://techmentions.com), and builds production AI agents with [Gaper](https://gaper.io), an AI-native implementation partner that deploys supervised agents into companies' own workflows.

That background shapes this product more than any SEO tool does. An embedded system cannot ask a human what to do when a sensor reads wrong at 3am; it has to know the difference between "the value is zero" and "the value is missing", and act on each correctly. SEO Agent is built with the same discipline. A link that could not be verified is reported as unverified, never counted. A site that answers nothing to this connection is unknown, not dead. A backlink index that shows nothing for a link placed yesterday is a lag, not a failure — and the product says so, in words, rather than leaving you to wonder.

He is on GitHub as [m4mansoor](https://github.com/m4mansoor), where SEO Agent is developed in the open.

## Why this exists

Link building has been the same job for fifteen years, and most of the job is not judgement. It is finding the field, creating the account, placing the link, and checking it went live — repeated fifty times. Agencies charge $150 to $400 a link for that and never show you the method. Bought lists are full of ghosts: sites that still score DA 90 on a decade of old links and shut down years ago, because nobody fetched the URL.

SEO Agent started as a personal project to automate that repetition properly: not to replace the judgement, but to remove everything around it. The library of 1,138 sites, each with its parsed method, is the product of that work. Every site is fetched monthly, and the ones that fail are hidden from search and planning rather than sold. Every method is checked against its live page, and the checker is worded to say "nothing looks wrong" rather than "verified", because only a real build proves a method works.

## The rules it keeps

These are not marketing lines; they are constraints in the code, most of them with a test that fails if they are broken.

- **It never claims a link is live until it has opened the public page and found the hyperlink, the anchor and the follow status.**
- **It reports what it built from its own record**, never from a third-party index that will not show a new link for weeks.
- **It advises with reasons, then does what you say.** Ask for more links than your profile can carry and it tells you once, plainly, and builds what you asked. It is your site.
- **It stops at gates.** A captcha, an email code or a social login is something it will not fake its way through. It says what the site wants and offers the choices.
- **It does not present convention as law.** The pacing and anchor guidance it gives are well-reasoned defaults with the reasoning visible. Google has never confirmed a velocity penalty, and the product does not pretend otherwise.
- **It speaks plainly.** No slugs, ids or file paths in what a person reads. "A followed link", not "dofollow", until you use the jargon first.

## How it is built

An open-source MCP server in Python, so it runs inside whatever assistant you already use — Claude Code, Cursor, Codex, Claude Desktop — rather than being one more dashboard. The library, the planner, the browser executor and the verifier are the same code whether you install the free package or subscribe. Twenty-five sites ship free with no account; the full library, the advisor, and building on account-based sites are the subscription.

The repository is public. If a site changes its method, [open an issue](https://github.com/m4mansoor/seo-agent/issues): a report is how the method gets corrected for everyone.

## Get in touch

The fastest way is [GitHub](https://github.com/m4mansoor/seo-agent). For work with Tech Mentions or Gaper, their sites have the details.
