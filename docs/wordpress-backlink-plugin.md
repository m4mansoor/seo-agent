---
title: "WordPress backlink plugin (in development)"
description: "A WordPress plugin that plans, builds, verifies and monitors backlinks to your posts, pages and WooCommerce products from inside wp-admin. In development; the engine behind it is built."
---

# The WordPress plugin

**Status: in development.** The engine it runs on is built and tested. This page describes what the plugin will do, so you can tell now whether it is the thing you want. Nothing here is available to install yet; star [the repository](https://github.com/m4mansoor/seo-agent) to hear when it is.

## What it is

A plugin that turns wp-admin into the place your backlinks get planned, built, verified and watched. It talks to the hosted engine, because WordPress hosting cannot run a browser, and it does everything else itself.

## Targets, from your own content

Any post, page, category, custom post type, or WooCommerce product and collection can be a target, picked from a searchable list that shows each page's SEO title, focus keyword and, when Search Console is connected, its impressions and average position. Focus keywords are imported from Yoast, Rank Math, All in One SEO or SEOPress. Select twenty product pages, give each three links, and that is one campaign.

## Anchors you do not have to invent

The plugin reads the target page and proposes keywords from its title, headings and body, then builds an anchor plan across the five types: exact, partial, branded, naked and generic. You drag the ratio; it allocates the anchors. Product names, types and attributes feed the suggestions on WooCommerce pages.

## Campaigns

See the exact sites, their Domain Authority, method and anchor before anything runs. Swap a row for another site, lock the ones you insist on, filter by DA range, dofollow share, method, tier and niche, and exclude domains that already link to you. Then watch each link move from queued to building to placed, unverified, gated or failed, with the proof screenshot inline.

Save your own templates: five links at DA 40 plus for a new blog post, ten mixed methods for a product launch, three at DA 80 plus for an authority push.

## Gates, in the admin bar

When a site asks for a captcha, an email code, a phone code or a social login, a badge appears. You paste the code, open the site and clear it yourself, connect a service once so it never asks again, or skip the site. The build continues where it stopped.

## Your own AI model

Account-based sites are driven by an AI model you supply: an Anthropic, OpenAI, Google or OpenRouter key, entered once in settings. Your model bill stays yours and under your control, and the estimated cost per link is shown before a campaign runs. Login-free sites need no model at all.

## Watching, not just building

Every placed link is re-checked weekly; a lost link raises an email and an admin notice. Beyond your own links, the plugin tracks every referring domain to your site, what is new and lost each month, spam-score flags, your anchor text spread and dofollow ratio, and generates a disavow file you can upload to Search Console.

## Competitor gap

Give it up to three competitor domains and it shows the referring domains they have and you do not, with a method attached to every row that is in the library, so the answer to "who links to them" becomes "build these five today".

## Autopilot

When a post or product is published, queue a template campaign for it after a delay you set, inside a velocity cap you set. Or give it a monthly budget and let it spend the links on the pages that get impressions but sit on page two.

## For agencies

One subscription, many installs, each registered with its own caps and allowance. White-label reports with your logo, colours and name, as a client-facing PDF or a read-only share link. Roles so an editor can run campaigns and a client sees reports only.

## The free tier

Twenty-five sites, built for your site by the hosted engine once your domain is verified, plus verification, weekly monitoring of your own links and a link-building audit of your site. Building on the full library needs a subscription.

Meanwhile, the [command line and MCP version](https://github.com/m4mansoor/seo-agent) works today.
