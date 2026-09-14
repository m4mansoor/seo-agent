---
title: How to get backlinks with an AI agent
description: A practical guide to AI link building, automated link building and backlink automation, with the exact steps an SEO agent follows to plan, place and verify links.
---

# How to get backlinks with an AI agent

Backlinks still decide rankings, and getting them is still slow: find a site that gives links, create an account, find the field or the editor, place the link, and check that it went live and is dofollow. An SEO agent removes the slow part without removing the judgement. Here is how it works with SEO Agent, and what it does not do.

## 1. Decide the campaign, not the links

Give the agent four things: the target URL, two or three keywords, an anchor-text ratio, and a dofollow share. A safe default ratio for a young site is 10% exact match, 20% partial, 30% branded, 25% naked URL and 15% generic. A 70% dofollow share is realistic; a 100% dofollow profile looks bought.

The planner picks sites by authority and ease, spreads the methods so a campaign is not twenty profile pages in a row, and assigns an anchor to every link from the ratio.

## 2. Let the agent follow each site's method

For every site the agent receives a playbook for that kind of link, the site's steps parsed into actions with the exact button names, what the site requires, and the rules: exact URL and anchor, no duplicates, stop at captchas.

Login-free sites, such as URL shorteners and open submission forms, are built automatically with a proof screenshot. Sites that need an account are built by your assistant in its own browser, with the identity you set once.

## 3. Verify before you count

A link only counts when the public page shows a hyperlink to the target with the intended anchor. The agent fetches that page and checks three things: is the target URL a hyperlink, does the anchor match, and does the link carry nofollow. Two traps it catches that humans miss:

- Anonymous hosts often add `rel="nofollow"` to every link or `noindex` to the page. A dofollow attribute on a noindex page passes almost nothing.
- Some sites show your URL as plain text, not as a link. That is not a backlink.

## 4. Keep the log

Every placed link, its live URL, its proof and its status live in one results table, so a month later you can re-check which links still stand.

## What an SEO agent will not do

It will not solve captchas, bypass bot checks, or create accounts on sites that forbid automation. When it meets one of those it stops and tells you what was asked. That keeps your site out of trouble and keeps the links you do get worth having.

## Try it

```bash
pip install seo-agent
claude mcp add seo-agent -- seo-agent
```

Then: *Build a link to my site on a dofollow site from the free list, and verify it.*

Related: [Claude SEO](claude-seo.md), [the free backlink sites list](../README.md#the-free-backlink-sites-list), [high DA backlinks](high-da-backlinks.md).
